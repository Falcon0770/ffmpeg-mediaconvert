import os
import boto3
import time
import sys
import io
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("FFmpeg S3 Video Converter - Single Folder Test")
print("="*60)

# AWS Configuration
AWS_REGION = "us-east-1"
s3 = boto3.client("s3", region_name=AWS_REGION)

# Rendition settings - EXACT MATCH to convert_video.py (widths must be even for H.264)
RENDITIONS = [
    {"height": 240, "width": 426, "bitrate": 200000, "name_modifier": "240p"},
    {"height": 360, "width": 640, "bitrate": 500000, "name_modifier": "360p"},
    {"height": 480, "width": 854, "bitrate": 800000, "name_modifier": "480p"},
    {"height": 720, "width": 1280, "bitrate": 1500000, "name_modifier": "720p"},
    {"height": 1080, "width": 1920, "bitrate": 2000000, "name_modifier": "1080p"}
]

AUDIO_BITRATE = 64000
AUDIO_SAMPLE_RATE = 48000
SEGMENT_LENGTH = 4
GOP_SIZE_SECONDS = 4

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg found and ready.\n")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: FFmpeg is not installed or not in PATH")
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
        if '/' in fps_str:
            num, den = map(float, fps_str.split('/'))
            return num / den
        return float(fps_str)
    except:
        return 30.0  # Default fallback

def submit_job(input_key, input_bucket, output_bucket, output_prefix, s3_input_folder_prefix):
    """Convert video using FFmpeg and upload to S3"""
    
    print(f"📹 Processing: {input_key}")
    
    # Extract file name
    input_file_name = os.path.splitext(os.path.basename(input_key))[0]
    input_file_name = input_file_name.replace(" ", "_")
    
    # Calculate folder structure
    input_folder = ""
    if input_key.startswith(s3_input_folder_prefix):
        relative_path = input_key[len(s3_input_folder_prefix):]
        input_folder = os.path.dirname(relative_path)
        if input_folder in ['.', '']:
            input_folder = ""
    
    # Construct output path
    if input_folder and input_folder != "":
        output_folder = os.path.join(output_prefix, input_folder, input_file_name).replace("\\", "/")
    else:
        output_folder = os.path.join(output_prefix, input_file_name).replace("\\", "/")
    
    print(f"📤 Output folder: s3://{output_bucket}/{output_folder}/")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_input = os.path.join(temp_dir, "input.mp4")
    temp_output_dir = os.path.join(temp_dir, "output")
    os.makedirs(temp_output_dir, exist_ok=True)
    
    try:
        # Download from S3
        print(f"⬇️  Downloading from S3...")
        s3.download_file(input_bucket, input_key, temp_input)
        file_size_mb = os.path.getsize(temp_input) / (1024 * 1024)
        print(f"   File size: {file_size_mb:.2f} MB")
        
        # Get framerate
        fps = get_video_framerate(temp_input)
        gop_size_frames = int(fps * GOP_SIZE_SECONDS)
        print(f"   Framerate: {fps:.2f} fps, GOP size: {gop_size_frames} frames")
        
        # Process each rendition separately
        print(f"🎬 Converting to HLS with {len(RENDITIONS)} renditions...")
        start_time = time.time()
        
        for i, r in enumerate(RENDITIONS):
            print(f"   [{i+1}/{len(RENDITIONS)}] Processing {r['name_modifier']}...", end=" ", flush=True)
            # Match MediaConvert naming: MASTER240p.m3u8, MASTER240p_00001.ts
            output_file = os.path.join(temp_output_dir, f"MASTER{r['name_modifier']}.m3u8")
            segment_pattern = os.path.join(temp_output_dir, f"MASTER{r['name_modifier']}_%05d.ts")
            
            cmd = [
                "ffmpeg", "-y", "-i", temp_input,
                "-vf", f"scale='trunc(oh*a/2)*2:{r['height']}',format=yuv420p",  # Ensure even width
                "-c:v", "libx264",
                "-profile:v", "main",
                "-preset", "fast",  # Changed to 'fast' for speed
                "-b:v", str(r['bitrate']),
                "-maxrate", str(int(r['bitrate'] * 1.2)),
                "-bufsize", str(int(r['bitrate'] * 2)),
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
                output_file
            ]
            
            # Run FFmpeg for this rendition
            rendition_start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            rendition_time = time.time() - rendition_start
            
            if result.returncode != 0:
                print(f"❌ FAILED")
                print(f"   Error: {result.stderr}")
                return False
            print(f"✅ ({rendition_time:.1f}s)")
        
        conversion_time = time.time() - start_time
        print(f"   ✅ All renditions completed in {conversion_time:.1f} seconds total")
        
        # Create master playlist - Match MediaConvert format exactly
        print(f"📝 Creating master playlist...")
        master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-INDEPENDENT-SEGMENTS\n"
        
        for r in RENDITIONS:
            # Calculate average bandwidth (typically 60-70% of max)
            avg_bandwidth = int(r['bitrate'] * 0.65)
            total_bandwidth = r['bitrate'] + AUDIO_BITRATE
            
            # Add stream info with detailed attributes like MediaConvert
            master_playlist += f'#EXT-X-STREAM-INF:BANDWIDTH={total_bandwidth},'
            master_playlist += f'AVERAGE-BANDWIDTH={avg_bandwidth},'
            master_playlist += f'CODECS="avc1.4d401f,mp4a.40.2",'
            master_playlist += f'RESOLUTION={r["width"]}x{r["height"]},'
            master_playlist += f'FRAME-RATE={fps:.3f}\n'
            master_playlist += f"MASTER{r['name_modifier']}.m3u8\n"
        
        master_file = os.path.join(temp_output_dir, "MASTER.m3u8")
        with open(master_file, 'w') as f:
            f.write(master_playlist)
        
        # Upload to S3 with correct Content-Type
        print(f"⬆️  Uploading to S3...")
        uploaded_count = 0
        for root, dirs, files in os.walk(temp_output_dir):
            for file in files:
                local_path = os.path.join(root, file)
                s3_key = f"{output_folder}/{file}"
                
                # Set correct Content-Type based on file extension
                extra_args = {}
                if file.endswith('.m3u8'):
                    extra_args['ContentType'] = 'application/vnd.apple.mpegurl'
                elif file.endswith('.ts'):
                    extra_args['ContentType'] = 'video/mp2t'
                
                s3.upload_file(local_path, output_bucket, s3_key, ExtraArgs=extra_args)
                uploaded_count += 1
        
        print(f"   ✅ Uploaded {uploaded_count} files")
        print(f"✅ SUCCESS! Video converted and uploaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# Main execution
if __name__ == "__main__":
    if not check_ffmpeg():
        sys.exit(1)
    
    # Test configuration
    input_bucket = "cdn.netcomplus.com"
    output_bucket = "cdn.netcomplus.com"
    s3_input_folder_prefix = "AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/"
    output_prefix = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary"
    
    print(f"📂 Input folder: s3://{input_bucket}/{s3_input_folder_prefix}")
    print(f"📂 Output folder: s3://{output_bucket}/{output_prefix}/")
    print()
    
    # List videos in folder
    print("🔍 Scanning S3 folder for videos...")
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=input_bucket, Prefix=s3_input_folder_prefix)
    
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    video_keys = []
    
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                if key.lower().endswith(video_extensions):
                    video_keys.append(key)
    
    if not video_keys:
        print(f"❌ No videos found in s3://{input_bucket}/{s3_input_folder_prefix}")
        sys.exit(1)
    
    print(f"✅ Found {len(video_keys)} video(s) to process\n")
    print("="*60)
    
    # Process each video
    success_count = 0
    failed_count = 0
    
    for i, video_key in enumerate(video_keys, 1):
        print(f"\n📹 Video {i}/{len(video_keys)}")
        print("-"*60)
        
        success = submit_job(video_key, input_bucket, output_bucket, output_prefix, s3_input_folder_prefix)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        print("-"*60)
    
    # Summary
    print("\n" + "="*60)
    print("CONVERSION COMPLETE!")
    print("="*60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📊 Total: {len(video_keys)}")
    print("="*60)
    
    if success_count > 0:
        print(f"\n🎉 Videos available at: s3://{output_bucket}/{output_prefix}/")

