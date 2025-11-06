import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

print("="*60)
print("Comparing S3 File Headers")
print("="*60)

# FFmpeg uploaded file (not working)
ffmpeg_file = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/master.m3u8"

print("\n1. FFmpeg-uploaded file (NOT working):")
print(f"   {ffmpeg_file}")
try:
    response = s3.head_object(Bucket=bucket, Key=ffmpeg_file)
    print(f"   Content-Type: {response.get('ContentType', 'NOT SET')}")
    print(f"   Cache-Control: {response.get('CacheControl', 'NOT SET')}")
except Exception as e:
    print(f"   Error: {e}")

# Ask user for a working MediaConvert file path
print("\n2. MediaConvert file (working):")
print("   Please provide the S3 key of a working master.m3u8 from MediaConvert")
print("   Example: streams/AI CERTs/Some Course/video_name/master.m3u8")

