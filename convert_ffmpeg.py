import os
import boto3
import time
import sys
import io
import json
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
FFmpeg-based Video Converter for S3
Exact replica of convert_video.py but using FFmpeg instead of MediaConvert
Cost savings: 85-90% compared to MediaConvert
"""

# Define processed videos log file
PROCESSED_LOG_FILE = "processed_videos.json"

# Define your AWS region
AWS_REGION = "us-east-1"

# Initialize S3 client
s3 = boto3.client("s3", region_name=AWS_REGION)

print("FFmpeg S3 Video Converter initialized successfully.")


# Define rendition settings - EXACT MATCH to convert_video.py
RENDITIONS = [
    {"height": 240, "width": 426, "bitrate": 200000, "name_modifier": "240p"},  # 200 KBit/s
    {"height": 360, "width": 640, "bitrate": 500000, "name_modifier": "360p"},  # 500 KBit/s
    {"height": 480, "width": 854, "bitrate": 800000, "name_modifier": "480p"},  # 800 KBit/s
    {"height": 720, "width": 1280, "bitrate": 1500000, "name_modifier": "720p"}, # 1.5 MBit/s
    {"height": 1080, "width": 1920, "bitrate": 2000000, "name_modifier": "1080p"} # 2 MBit/s
]

# Audio settings - match MediaConvert
AUDIO_BITRATE = 64000  # 64 KBit/s
AUDIO_SAMPLE_RATE = 48000

# HLS settings - match MediaConvert
SEGMENT_LENGTH = 4  # 4 seconds (matching convert_video.py line 76)
GOP_SIZE_SECONDS = 4  # 4 seconds (matching convert_video.py line 115)

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("FFmpeg found and ready.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: FFmpeg is not installed or not in PATH")
        print("Please install FFmpeg first: https://ffmpeg.org/download.html")
        return False

def get_video_framerate(video_path):
    """Get video framerate using ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=r_frame_rate",
            "-of", "csv=p=0",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        fps_str = result.stdout.strip()
        # Parse fraction (e.g., "30000/1001" or "30/1")
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den)
        else:
            fps = float(fps_str)
        return int(round(fps))
    except:
        return 30  # Default to 30fps if detection fails

def convert_video_ffmpeg(input_path, output_dir, input_file_name):
    """
    Convert video to HLS using FFmpeg
    Replicates MediaConvert settings exactly
    Process each rendition separately to avoid dimension issues
    """
    print(f"Starting FFmpeg conversion...")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video framerate for GOP size calculation
    fps = get_video_framerate(input_path)
    gop_size_frames = int(fps * GOP_SIZE_SECONDS)  # 4 seconds worth of frames
    
    print(f"  Detected framerate: {fps:.2f} fps")
    print(f"  GOP size: {gop_size_frames} frames ({GOP_SIZE_SECONDS} seconds)")
    print(f"  Converting {len(RENDITIONS)} renditions...")
    
    start_time = time.time()
    
    # Process each rendition separately
    for i, rendition in enumerate(RENDITIONS):
        name_mod = rendition['name_modifier']
        print(f"  [{i+1}/{len(RENDITIONS)}] Processing {name_mod}...", end=" ", flush=True)
        
        output_playlist = os.path.join(output_dir, f"MASTER_{name_mod}.m3u8")
        segment_pattern = os.path.join(output_dir, f"seg_{name_mod}_%04d.ts")
        
        # Build FFmpeg command for this rendition
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"scale='trunc(oh*a/2)*2:{rendition['height']}',format=yuv420p",  # Ensure even width
            "-c:v", "libx264",
            "-profile:v", "main",
            "-preset", "fast",
            "-b:v", str(rendition['bitrate']),
            "-maxrate", str(int(rendition['bitrate'] * 1.2)),
            "-bufsize", str(int(rendition['bitrate'] * 2)),
            "-g", str(gop_size_frames),
            "-keyint_min", str(gop_size_frames),
            "-sc_threshold", "0",
            "-c:a", "aac",
            "-b:a", str(AUDIO_BITRATE),
            "-ar", str(AUDIO_SAMPLE_RATE),
            "-ac", "2",
            "-f", "hls",
            "-hls_time", str(SEGMENT_LENGTH),
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", segment_pattern,
            "-loglevel", "error",  # Suppress verbose output
            output_playlist
        ]
        
        # Run FFmpeg for this rendition
        rendition_start = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        rendition_time = time.time() - rendition_start
        
        if result.returncode != 0:
            print(f"❌ FAILED")
            print(f"  Error: {result.stderr}")
            return False
        print(f"✅ ({rendition_time:.1f}s)")
    
    elapsed = time.time() - start_time
    print(f"✅ All renditions completed in {elapsed:.1f} seconds total")
    
    # Verify output files were created
    for rendition in RENDITIONS:
        playlist = os.path.join(output_dir, f"MASTER_{rendition['name_modifier']}.m3u8")
        if not os.path.exists(playlist):
            print(f"❌ Missing output playlist: {playlist}")
            return False
    
    # Create master playlist - Match MediaConvert format
    print(f"📝 Creating master playlist...")
    master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-INDEPENDENT-SEGMENTS\n"
    
    for rendition in RENDITIONS:
        # Calculate average bandwidth (typically 60-70% of max)
        avg_bandwidth = int(rendition['bitrate'] * 0.65)
        total_bandwidth = rendition['bitrate'] + AUDIO_BITRATE
        
        # Add stream info with detailed attributes like MediaConvert
        master_playlist += f'#EXT-X-STREAM-INF:BANDWIDTH={total_bandwidth},'
        master_playlist += f'AVERAGE-BANDWIDTH={avg_bandwidth},'
        master_playlist += f'CODECS="avc1.4d401f,mp4a.40.2",'
        master_playlist += f'RESOLUTION={rendition["width"]}x{rendition["height"]},'
        master_playlist += f'FRAME-RATE={fps:.3f}\n'
        master_playlist += f"MASTER{rendition['name_modifier']}.m3u8\n"
    
    master_file = os.path.join(output_dir, "MASTER.m3u8")
    with open(master_file, 'w') as f:
        f.write(master_playlist)
    
    print(f"✅ All {len(RENDITIONS)} renditions + master playlist created successfully")
    return True

def download_from_s3(bucket, key, local_path):
    """Download file from S3 with progress indication"""
    print(f"⬇️  Downloading from S3: s3://{bucket}/{key}")
    try:
        # Get file size for progress indication
        response = s3.head_object(Bucket=bucket, Key=key)
        file_size = response['ContentLength']
        print(f"   File size: {file_size / (1024*1024):.2f} MB")
        
        s3.download_file(bucket, key, local_path)
        print(f"✅ Download complete: {local_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def upload_directory_to_s3(local_dir, bucket, s3_prefix):
    """Upload entire directory to S3, preserving structure"""
    print(f"⬆️  Uploading to S3: s3://{bucket}/{s3_prefix}")
    
    uploaded_count = 0
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")
                
                # Set correct Content-Type based on file extension
                extra_args = {}
                if file.endswith('.m3u8'):
                    extra_args['ContentType'] = 'application/vnd.apple.mpegurl'
                elif file.endswith('.ts'):
                    extra_args['ContentType'] = 'video/mp2t'
                
                # Upload file with proper Content-Type
                file_size = os.path.getsize(local_path)
                s3.upload_file(local_path, bucket, s3_key, ExtraArgs=extra_args)
                uploaded_count += 1
                total_size += file_size
                
                if uploaded_count % 10 == 0:
                    print(f"   Uploaded {uploaded_count} files...")
        
        print(f"✅ Upload complete: {uploaded_count} files ({total_size / (1024*1024):.2f} MB)")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def submit_job(input_key, input_bucket, output_bucket, output_prefix, s3_input_folder_prefix):
    """
    Process a single video - exact replica of convert_video.py submit_job logic
    """
    # Extract file name and folder structure - EXACT MATCH to convert_video.py lines 35-50
    input_file_name, input_file_extension = os.path.splitext(os.path.basename(input_key))
    
    # Replace spaces with underscores in the filename for URL-safe paths
    input_file_name = input_file_name.replace(" ", "_")
    
    # Calculate the folder structure relative to the input prefix robustly
    # This ensures subfolders are preserved correctly without "../"
    input_folder = ""
    if input_key.startswith(s3_input_folder_prefix):
        # Get the path after the s3_input_folder_prefix
        relative_path_from_prefix = input_key[len(s3_input_folder_prefix):]
        # Get the directory part of this relative path, without the filename
        input_folder = os.path.dirname(relative_path_from_prefix)
        # If input_folder is '.' (meaning file is directly in s3_input_folder_prefix), make it empty
        if input_folder == '.':
            input_folder = ""
    
    # Construct the output destination, preserving folder structure
    # Ensure no double-slash if input_folder is empty
    if input_folder:
        destination = f"s3://{output_bucket}/{output_prefix}{input_folder}/{input_file_name}/"
    else:
        destination = f"s3://{output_bucket}/{output_prefix}{input_file_name}/"
    
    # Parse destination for upload
    dest_path = destination.replace(f"s3://{output_bucket}/", "")
    
    print(f"\n{'='*60}")
    print(f"Processing: {input_key}")
    print(f"Output destination: {destination}")
    print(f"{'='*60}")
    
    # Create temporary directory for processing
    temp_dir = tempfile.mkdtemp(prefix="ffmpeg_convert_")
    
    try:
        # Step 1: Download from S3
        print("\n[1/4] Downloading from S3...")
        temp_input = os.path.join(temp_dir, f"input{input_file_extension}")
        if not download_from_s3(input_bucket, input_key, temp_input):
            return False
        
        # Step 2: Convert with FFmpeg
        print("\n[2/4] Converting video with FFmpeg...")
        temp_output = os.path.join(temp_dir, "output")
        
        # Simulate job status polling like MediaConvert
        print("Job Status: PROCESSING")
        
        success = convert_video_ffmpeg(temp_input, temp_output, input_file_name)
        
        if not success:
            print("Job Status: ERROR")
            return False
        
        print("Job Status: COMPLETE")
        
        # Step 3: Upload to S3
        print("\n[3/4] Uploading to S3...")
        if not upload_directory_to_s3(temp_output, output_bucket, dest_path):
            return False
        
        # Step 4: Cleanup
        print("\n[4/4] Cleaning up temporary files...")
        shutil.rmtree(temp_dir)
        print("✅ Cleanup complete")
        
        print(f"\n{'='*60}")
        print(f"✅ Successfully processed: {input_key}")
        print(f"   Output: {destination}")
        print(f"   Renditions: {len(RENDITIONS)} ({', '.join([r['name_modifier'] for r in RENDITIONS])})")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing {input_key}: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        return False

def list_s3_video_objects(bucket_name, prefix):
    """List all video files in S3 bucket - EXACT MATCH to convert_video.py lines 219-233"""
    video_objects = []
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv')

    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                if key.lower().endswith(video_extensions):
                    video_objects.append(key)
    return video_objects

def load_processed_videos():
    """Load list of already processed videos - EXACT MATCH to convert_video.py lines 235-239"""
    if os.path.exists(PROCESSED_LOG_FILE):
        with open(PROCESSED_LOG_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_videos(processed_videos):
    """Save list of processed videos - EXACT MATCH to convert_video.py lines 241-243"""
    with open(PROCESSED_LOG_FILE, 'w') as f:
        json.dump(list(processed_videos), f, indent=4)

# Main execution - EXACT MATCH to convert_video.py lines 246-295
if __name__ == "__main__":
    # Check FFmpeg availability first
    if not check_ffmpeg():
        sys.exit(1)
    
    # Add argument for forcing re-processing - EXACT MATCH to CLI
    parser = argparse.ArgumentParser(description="Submit videos to FFmpeg for HLS conversion (S3 to S3).")
    parser.add_argument("s3_input_folder_prefix", help="Input S3 folder path, e.g. AI CERTs/...")
    parser.add_argument("input_bucket", help="Input S3 bucket name, e.g. aicertslms")
    parser.add_argument("output_bucket", help="Output S3 bucket name, e.g. cdn.netcomplus.com")
    parser.add_argument("output_prefix", help="Output S3 folder prefix, e.g. streams/AI CERTs/...")
    parser.add_argument("--force", action="store_true", help="Force reprocessing all videos, ignoring processed_videos.json")
    args = parser.parse_args()

    s3_input_folder_prefix = args.s3_input_folder_prefix
    input_bucket = args.input_bucket
    output_bucket = args.output_bucket
    output_prefix = args.output_prefix
    force_reprocess = args.force

    processed_videos = load_processed_videos()
    print(f"Loaded {len(processed_videos)} previously processed videos.")

    print(f"Listing video objects in s3://{input_bucket}/{s3_input_folder_prefix}...")
    all_video_keys = list_s3_video_objects(input_bucket, s3_input_folder_prefix)

    if force_reprocess:
        print("Force reprocessing enabled. All videos will be processed.")
        video_keys_to_process = all_video_keys
    else:
        video_keys_to_process = [key for key in all_video_keys if key not in processed_videos]

    if not video_keys_to_process:
        print(f"No new video files found in s3://{input_bucket}/{s3_input_folder_prefix} to process.")
        sys.exit(0)

    print(f"Found {len(video_keys_to_process)} new video(s) to process. Starting conversion...")
    
    success_count = 0
    failed_count = 0
    
    for input_key in video_keys_to_process:
        print(f"\nProcessing video {success_count + failed_count + 1}/{len(video_keys_to_process)}")
        
        success = submit_job(input_key, input_bucket, output_bucket, output_prefix, s3_input_folder_prefix)
        
        if success:
            # Add to processed list after successful completion
            processed_videos.add(input_key)
            save_processed_videos(processed_videos)
            success_count += 1
        else:
            failed_count += 1
        
        print(f"\n📊 Progress: {success_count + failed_count}/{len(video_keys_to_process)} " +
              f"(✅ {success_count} | ❌ {failed_count})")

    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📋 Total: {len(video_keys_to_process)}")
    print("="*60)
    
    if failed_count > 0:
        print("\n⚠️  Some videos failed to process. Check the output above for details.")
        sys.exit(1)
    else:
        print("\n🎉 All videos processed successfully!")

