import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

print("="*60)
print("Checking Rendition Playlists")
print("="*60)

# FFmpeg 240p playlist
ffmpeg_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/AI+_Writer-V3-Course_Introduction_240p.m3u8"
print("\n❌ FFmpeg 240p playlist:")
print("-"*60)
try:
    resp1 = s3.get_object(Bucket=bucket, Key=ffmpeg_key)
    content1 = resp1['Body'].read().decode('utf-8')
    lines = content1.split('\n')[:15]
    print('\n'.join(lines))
    print(f"... ({len(content1.splitlines())} total lines)")
except Exception as e:
    print(f"Error: {e}")
print("-"*60)

# MediaConvert 240p playlist
mediaconvert_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ UX Designer /Introduction - Summary /AI+_UX_Designer-V3-Course_Introduction/MASTER240p.m3u8"
print("\n✅ MediaConvert 240p playlist:")
print("-"*60)
try:
    resp2 = s3.get_object(Bucket=bucket, Key=mediaconvert_key)
    content2 = resp2['Body'].read().decode('utf-8')
    lines = content2.split('\n')[:15]
    print('\n'.join(lines))
    print(f"... ({len(content2.splitlines())} total lines)")
except Exception as e:
    print(f"Error: {e}")
print("-"*60)

# Check if segment files exist
print("\n🔍 Checking segment files...")
ffmpeg_seg = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/AI+_Writer-V3-Course_Introduction_240p00000.ts"
try:
    s3.head_object(Bucket=bucket, Key=ffmpeg_seg)
    print(f"✅ FFmpeg segment exists: {ffmpeg_seg.split('/')[-1]}")
except:
    print(f"❌ FFmpeg segment missing: {ffmpeg_seg.split('/')[-1]}")

