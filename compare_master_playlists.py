import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

print("="*60)
print("Comparing Master Playlist Contents")
print("="*60)

# FFmpeg file (not working)
ffmpeg_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/master.m3u8"
print("\n❌ FFmpeg master.m3u8 (NOT working):")
print("-"*60)
resp1 = s3.get_object(Bucket=bucket, Key=ffmpeg_key)
content1 = resp1['Body'].read().decode('utf-8')
print(content1)
print("-"*60)

# MediaConvert file (working)
mediaconvert_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ UX Designer /Introduction - Summary /AI+_UX_Designer-V3-Course_Introduction/MASTER.m3u8"
print("\n✅ MediaConvert MASTER.m3u8 (working):")
print("-"*60)
resp2 = s3.get_object(Bucket=bucket, Key=mediaconvert_key)
content2 = resp2['Body'].read().decode('utf-8')
print(content2)
print("-"*60)

print("\n🔍 Key Differences:")
if content1 == content2:
    print("   ✅ Contents are identical!")
else:
    print("   ❌ Contents are different")
    print(f"   FFmpeg lines: {len(content1.splitlines())}")
    print(f"   MediaConvert lines: {len(content2.splitlines())}")

