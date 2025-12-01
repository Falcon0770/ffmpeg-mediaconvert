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
import random
import signal
from pathlib import Path

# Import fcntl for Linux file locking (EC2)
try:
    import fcntl
    LOCK_AVAILABLE = True
except ImportError:
    # Windows doesn't have fcntl, fallback to basic operation
    LOCK_AVAILABLE = False
    print("⚠️  Warning: File locking not available on this platform. Parallel processing may cause conflicts.")

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

# File to track videos currently being processed (in-progress lock)
IN_PROGRESS_FILE = "in_progress_videos.json"

# Global variable to track current video being processed (for cleanup on interrupt)
CURRENT_VIDEO_KEY = None

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
        master_playlist += f"MASTER_{rendition['name_modifier']}.m3u8\n"
    
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
        
        # Skip files that are too small (likely corrupted or metadata files)
        if file_size < 1024:  # Less than 1KB
            print(f"⚠️  Skipping file - too small ({file_size} bytes), likely corrupted or metadata file")
            return False
        
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
                # Get filename from key
                filename = key.split('/')[-1]
                
                # Skip macOS metadata files (._filename) and files with 0 size
                if filename.startswith('._'):
                    continue
                
                # Skip files that are too small (likely corrupted)
                if obj.get('Size', 0) < 1024:  # Skip files smaller than 1KB
                    continue
                
                if key.lower().endswith(video_extensions):
                    video_objects.append(key)
    return video_objects

def load_json_file_with_lock(file_path, lock_type=fcntl.LOCK_SH if LOCK_AVAILABLE else None):
    """
    Load JSON file with file locking for thread-safe reads
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            if LOCK_AVAILABLE and lock_type:
                fcntl.flock(f.fileno(), lock_type)
            try:
                data = json.load(f)
            finally:
                if LOCK_AVAILABLE and lock_type:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return data
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"⚠️  Warning: Could not read {file_path}: {e}")
        return []

def save_json_file_with_lock(file_path, data):
    """
    Save JSON file with exclusive file locking for thread-safe writes
    """
    try:
        with open(file_path, 'w') as f:
            if LOCK_AVAILABLE:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=4)
            finally:
                if LOCK_AVAILABLE:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {e}")
        return False

def load_processed_videos():
    """Load list of already processed videos with thread-safe locking"""
    data = load_json_file_with_lock(PROCESSED_LOG_FILE, fcntl.LOCK_SH if LOCK_AVAILABLE else None)
    return set(data)

def save_processed_videos(processed_videos):
    """Save list of processed videos with thread-safe locking"""
    save_json_file_with_lock(PROCESSED_LOG_FILE, list(processed_videos))

def load_in_progress_videos():
    """Load list of videos currently being processed"""
    data = load_json_file_with_lock(IN_PROGRESS_FILE, fcntl.LOCK_SH if LOCK_AVAILABLE else None)
    return set(data)

def save_in_progress_videos(in_progress_videos):
    """Save list of videos currently being processed"""
    save_json_file_with_lock(IN_PROGRESS_FILE, list(in_progress_videos))

def acquire_next_video(all_videos, max_retries=10):
    """
    Thread-safe way to get the next video to process
    Returns: (video_key, should_continue) - video_key is None if no videos available
    """
    for attempt in range(max_retries):
        try:
            # Open processed videos file with exclusive lock
            with open(PROCESSED_LOG_FILE, 'r+') as pf:
                if LOCK_AVAILABLE:
                    fcntl.flock(pf.fileno(), fcntl.LOCK_EX)
                
                try:
                    # Load both processed and in-progress videos
                    processed = set(json.load(pf) if os.path.getsize(PROCESSED_LOG_FILE) > 0 else [])
                    
                    # Also check in-progress file
                    in_progress = load_in_progress_videos()
                    
                    # Find a video that's neither processed nor in progress
                    available_videos = [v for v in all_videos if v not in processed and v not in in_progress]
                    
                    if not available_videos:
                        return None, False  # No more videos to process
                    
                    # Pick the first available video
                    selected_video = available_videos[0]
                    
                    # Mark it as in-progress
                    in_progress.add(selected_video)
                    save_in_progress_videos(in_progress)
                    
                    return selected_video, True
                    
                finally:
                    if LOCK_AVAILABLE:
                        fcntl.flock(pf.fileno(), fcntl.LOCK_UN)
                        
        except FileNotFoundError:
            # Create the file if it doesn't exist
            with open(PROCESSED_LOG_FILE, 'w') as f:
                json.dump([], f)
            # Retry
            time.sleep(random.uniform(0.1, 0.5))
            continue
            
        except Exception as e:
            print(f"⚠️  Attempt {attempt + 1}/{max_retries} failed: {e}")
            time.sleep(random.uniform(0.5, 1.5))
            continue
    
    # Max retries exceeded
    print("❌ Could not acquire lock after maximum retries")
    return None, False

def mark_video_complete(video_key):
    """
    Mark a video as completed (move from in-progress to processed)
    """
    try:
        # Add to processed list
        processed = load_processed_videos()
        processed.add(video_key)
        save_processed_videos(processed)
        
        # Remove from in-progress list
        in_progress = load_in_progress_videos()
        if video_key in in_progress:
            in_progress.remove(video_key)
            save_in_progress_videos(in_progress)
        
        return True
    except Exception as e:
        print(f"❌ Error marking video complete: {e}")
        return False

def mark_video_failed(video_key):
    """
    Remove video from in-progress (so it can be retried later)
    """
    try:
        in_progress = load_in_progress_videos()
        if video_key in in_progress:
            in_progress.remove(video_key)
            save_in_progress_videos(in_progress)
        return True
    except Exception as e:
        print(f"❌ Error marking video failed: {e}")
        return False

def signal_handler(sig, frame):
    """
    Handle Ctrl+C and other interrupts gracefully
    Release the current video lock before exiting
    """
    global CURRENT_VIDEO_KEY
    print("\n\n⚠️  Interrupt received! Cleaning up...")
    if CURRENT_VIDEO_KEY:
        print(f"🔓 Releasing lock on: {CURRENT_VIDEO_KEY}")
        mark_video_failed(CURRENT_VIDEO_KEY)
    print("✅ Cleanup complete. Exiting.")
    sys.exit(0)

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

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    s3_input_folder_prefix = args.s3_input_folder_prefix
    input_bucket = args.input_bucket
    output_bucket = args.output_bucket
    output_prefix = args.output_prefix
    force_reprocess = args.force

    # Get all videos from S3
    print(f"Listing video objects in s3://{input_bucket}/{s3_input_folder_prefix}...")
    all_video_keys = list_s3_video_objects(input_bucket, s3_input_folder_prefix)
    
    if not all_video_keys:
        print(f"No video files found in s3://{input_bucket}/{s3_input_folder_prefix}")
        sys.exit(0)
    
    # Load processed and in-progress videos
    processed_videos = load_processed_videos()
    in_progress_videos = load_in_progress_videos()
    
    print(f"📊 Status:")
    print(f"   Total videos in S3: {len(all_video_keys)}")
    print(f"   Already processed: {len(processed_videos)}")
    print(f"   Currently in progress: {len(in_progress_videos)}")
    print(f"   Available to process: {len([v for v in all_video_keys if v not in processed_videos and v not in in_progress_videos])}")

    if force_reprocess:
        print("\n⚠️  Force reprocessing enabled. Clearing processed and in-progress lists...")
        save_processed_videos(set())
        save_in_progress_videos(set())
        print("All videos will be reprocessed.")
    
    print(f"\n🚀 Starting video conversion (parallel-safe mode)...")
    if LOCK_AVAILABLE:
        print("✅ File locking enabled - safe for parallel processing")
    else:
        print("⚠️  File locking not available - avoid running multiple instances")
    
    success_count = 0
    failed_count = 0
    
    # Process videos one at a time, but use thread-safe acquisition
    while True:
        # Acquire next video to process
        input_key, should_continue = acquire_next_video(all_video_keys)
        
        if not should_continue or input_key is None:
            print("\n✅ No more videos to process.")
            break
        
        # Set current video for signal handler
        CURRENT_VIDEO_KEY = input_key
        
        print(f"\n{'='*60}")
        print(f"🎬 Acquired video: {input_key}")
        print(f"{'='*60}")
        
        # Process the video
        success = submit_job(input_key, input_bucket, output_bucket, output_prefix, s3_input_folder_prefix)
        
        if success:
            # Mark as complete
            mark_video_complete(input_key)
            success_count += 1
            print(f"\n✅ Video marked as COMPLETED")
        else:
            # Mark as failed (removes from in-progress so it can be retried)
            mark_video_failed(input_key)
            failed_count += 1
            print(f"\n❌ Video marked as FAILED (can be retried)")
        
        # Clear current video after processing
        CURRENT_VIDEO_KEY = None
        
        # Show current progress
        total_processed = len(load_processed_videos())
        total_in_progress = len(load_in_progress_videos())
        remaining = len([v for v in all_video_keys if v not in load_processed_videos() and v not in load_in_progress_videos()])
        
        print(f"\n📊 Overall Progress:")
        print(f"   ✅ Completed: {total_processed}/{len(all_video_keys)}")
        print(f"   🔄 In Progress (all workers): {total_in_progress}")
        print(f"   ⏳ Remaining: {remaining}")
        print(f"   This worker: ✅ {success_count} | ❌ {failed_count}")

    print("\n" + "="*60)
    print("🏁 Worker Finished!")
    print("="*60)
    print(f"This worker processed:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Failed: {failed_count}")
    print(f"   📋 Total: {success_count + failed_count}")
    print("="*60)
    
    # Show overall status
    final_processed = len(load_processed_videos())
    final_in_progress = len(load_in_progress_videos())
    final_remaining = len([v for v in all_video_keys if v not in load_processed_videos() and v not in load_in_progress_videos()])
    
    print(f"\n📊 Overall Status (all workers):")
    print(f"   ✅ Completed: {final_processed}/{len(all_video_keys)}")
    print(f"   🔄 In Progress: {final_in_progress}")
    print(f"   ⏳ Remaining: {final_remaining}")
    print("="*60)
    
    if final_remaining > 0 or final_in_progress > 0:
        print("\n💡 Tip: Other workers may still be processing, or you can run this script again to continue.")
    else:
        print("\n🎉 All videos have been processed!")

