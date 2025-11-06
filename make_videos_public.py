import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

folders = [
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Summary/"
]

print("="*60)
print("Making FFmpeg Videos Publicly Readable")
print("="*60)

for folder in folders:
    print(f"\n📁 Processing: {folder}")
    
    # List all files in folder
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=folder)
    
    files = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                files.append(obj['Key'])
    
    if not files:
        print(f"   ⚠️  No files found")
        continue
    
    print(f"   Found {len(files)} files")
    print(f"   Making them public...")
    
    # Make each file public
    count = 0
    for file_key in files:
        try:
            s3.put_object_acl(
                Bucket=bucket,
                Key=file_key,
                ACL='public-read'
            )
            count += 1
            if count % 50 == 0:
                print(f"      {count}/{len(files)} files made public...")
        except Exception as e:
            print(f"   ❌ Failed on {file_key}: {e}")
            break
    
    print(f"   ✅ Made {count} files public")

print("\n" + "="*60)
print("✅ Complete! Test your videos now:")
print("https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/master.m3u8")
print("="*60)

