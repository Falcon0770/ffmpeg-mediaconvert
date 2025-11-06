import boto3
import subprocess
import tempfile
import os
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

print("="*60)
print("Verifying Video Codec in Segment Files")
print("="*60)

# Download a segment file
segment_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/AI+_Writer-V3-Course_Introduction_240p00000.ts"

temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ts')
temp_path = temp_file.name
temp_file.close()

try:
    print(f"\n⬇️  Downloading segment file...")
    s3.download_file(bucket, segment_key, temp_path)
    file_size = os.path.getsize(temp_path)
    print(f"   ✅ Downloaded: {file_size} bytes")
    
    print(f"\n🔍 Analyzing with ffprobe...")
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_name,codec_type,width,height,pix_fmt,profile",
        "-of", "json",
        temp_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        import json
        data = json.loads(result.stdout)
        print("\n📊 Stream Information:")
        for stream in data.get('streams', []):
            print(f"\n   Type: {stream.get('codec_type')}")
            print(f"   Codec: {stream.get('codec_name')}")
            if stream.get('width'):
                print(f"   Resolution: {stream.get('width')}x{stream.get('height')}")
            if stream.get('pix_fmt'):
                print(f"   Pixel Format: {stream.get('pix_fmt')}")
            if stream.get('profile'):
                print(f"   Profile: {stream.get('profile')}")
    else:
        print(f"   ❌ ffprobe error: {result.stderr}")
        
finally:
    if os.path.exists(temp_path):
        os.unlink(temp_path)

print("\n" + "="*60)

