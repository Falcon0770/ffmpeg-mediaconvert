import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

AWS_REGION = "us-east-1"
s3 = boto3.client("s3", region_name=AWS_REGION)

bucket = "cdn.netcomplus.com"
prefix = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/"

print(f"Checking S3 bucket: {bucket}")
print(f"Prefix: {prefix}")
print("="*60)

# List files
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

files = []
for page in pages:
    if "Contents" in page:
        for obj in page["Contents"]:
            files.append(obj["Key"])

print(f"\n✅ Found {len(files)} files\n")

# Show master playlist and individual playlists
playlists = [f for f in files if f.endswith('.m3u8')]
print(f"📋 Playlists ({len(playlists)}):")
for p in sorted(playlists):
    print(f"   - {p.split('/')[-1]}")

# Download and show master.m3u8 content
master_key = prefix + "master.m3u8"
print(f"\n📄 Content of master.m3u8:")
print("-"*60)
try:
    response = s3.get_object(Bucket=bucket, Key=master_key)
    content = response['Body'].read().decode('utf-8')
    print(content)
except Exception as e:
    print(f"❌ Error reading master.m3u8: {e}")

print("-"*60)

# Show one rendition playlist
if playlists:
    rendition_key = [p for p in playlists if '240p' in p][0]
    print(f"\n📄 Content of {rendition_key.split('/')[-1]} (first 20 lines):")
    print("-"*60)
    try:
        response = s3.get_object(Bucket=bucket, Key=rendition_key)
        content = response['Body'].read().decode('utf-8')
        lines = content.split('\n')[:20]
        print('\n'.join(lines))
    except Exception as e:
        print(f"❌ Error: {e}")
    print("-"*60)

# Check file accessibility
print(f"\n🌐 Public URLs:")
print(f"Master playlist: https://{bucket}/{master_key}")
print(f"\n⚠️  Note: Make sure your S3 bucket has:")
print("   1. Public read access enabled")
print("   2. CORS configuration for video streaming")
print("   3. Correct Content-Type headers (application/vnd.apple.mpegurl for .m3u8)")

