import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket = 'cdn.netcomplus.com'

folders_to_delete = [
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Summary/"
]

print("="*60)
print("Deleting Test Video Folders")
print("="*60)

for folder in folders_to_delete:
    print(f"\n🗑️  Deleting: {folder}")
    
    # List all objects in folder
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=folder)
    
    objects_to_delete = []
    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                objects_to_delete.append({'Key': obj['Key']})
    
    if objects_to_delete:
        print(f"   Found {len(objects_to_delete)} files to delete...")
        
        # Delete in batches of 1000 (S3 limit)
        for i in range(0, len(objects_to_delete), 1000):
            batch = objects_to_delete[i:i+1000]
            s3.delete_objects(
                Bucket=bucket,
                Delete={'Objects': batch}
            )
        print(f"   ✅ Deleted {len(objects_to_delete)} files")
    else:
        print(f"   ℹ️  Folder already empty or doesn't exist")

print("\n" + "="*60)
print("✅ Cleanup complete!")
print("="*60)

