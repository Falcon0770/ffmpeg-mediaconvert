import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

print("="*60)
print("Debugging Playlist File Paths")
print("="*60)

# Check FFmpeg files
ffmpeg_folder = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/"
print(f"\n📁 FFmpeg folder contents:")
print(f"   {ffmpeg_folder}")

paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket, Prefix=ffmpeg_folder, MaxKeys=20)

files = []
for page in pages:
    if "Contents" in page:
        for obj in page["Contents"]:
            files.append(obj['Key'].replace(ffmpeg_folder, ''))

print(f"\n   First 20 files:")
for f in files[:20]:
    print(f"      {f}")

# Check if master.m3u8 exists
master_key = ffmpeg_folder + "master.m3u8"
print(f"\n🔍 Checking master.m3u8:")
try:
    s3.head_object(Bucket=bucket, Key=master_key)
    print(f"   ✅ EXISTS: {master_key}")
    
    # Download and show content
    resp = s3.get_object(Bucket=bucket, Key=master_key)
    content = resp['Body'].read().decode('utf-8')
    print(f"\n   Content (first 500 chars):")
    print(f"   {'-'*56}")
    print(content[:500])
    print(f"   {'-'*56}")
except:
    print(f"   ❌ NOT FOUND: {master_key}")

# Check if a rendition playlist exists
rendition_key = ffmpeg_folder + "AI+_Writer-V3-Course_Introduction_240p.m3u8"
print(f"\n🔍 Checking 240p rendition:")
try:
    s3.head_object(Bucket=bucket, Key=rendition_key)
    print(f"   ✅ EXISTS")
    
    # Download and show content
    resp = s3.get_object(Bucket=bucket, Key=rendition_key)
    content = resp['Body'].read().decode('utf-8')
    lines = content.split('\n')[:12]
    print(f"\n   First 12 lines:")
    for line in lines:
        print(f"      {line}")
except:
    print(f"   ❌ NOT FOUND")

# Check if segment exists
segment_key = ffmpeg_folder + "AI+_Writer-V3-Course_Introduction_240p00000.ts"
print(f"\n🔍 Checking first segment:")
try:
    s3.head_object(Bucket=bucket, Key=segment_key)
    print(f"   ✅ EXISTS: AI+_Writer-V3-Course_Introduction_240p00000.ts")
except:
    print(f"   ❌ NOT FOUND: AI+_Writer-V3-Course_Introduction_240p00000.ts")

print("\n" + "="*60)

