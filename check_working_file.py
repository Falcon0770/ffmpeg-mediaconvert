import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

print("="*60)
print("Comparing File Headers")
print("="*60)

# FFmpeg file (not working)
ffmpeg_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/master.m3u8"
print("\n❌ FFmpeg-uploaded file (NOT working):")
print(f"   {ffmpeg_key}")
resp1 = s3.head_object(Bucket=bucket, Key=ffmpeg_key)
print(f"   Content-Type: {resp1.get('ContentType', 'NOT SET')}")

# MediaConvert file (working)
mediaconvert_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ UX Designer /Introduction - Summary /AI+_UX_Designer-V3-Course_Introduction/MASTER.m3u8"
print("\n✅ MediaConvert file (working):")
print(f"   {mediaconvert_key}")
resp2 = s3.head_object(Bucket=bucket, Key=mediaconvert_key)
print(f"   Content-Type: {resp2.get('ContentType', 'NOT SET')}")

print("\n" + "="*60)
print("SOLUTION:")
print(f"   FFmpeg files need Content-Type: {resp2.get('ContentType')}")
print("="*60)

