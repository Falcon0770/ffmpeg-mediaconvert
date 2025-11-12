import boto3
import json

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"

# Videos to delete (the 3 that were processed incorrectly)
videos_to_delete = [
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Summary/",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/"
]

print("Deleting incorrectly processed videos from S3...")
print("="*80)

for prefix in videos_to_delete:
    print(f"\nDeleting: s3://{bucket}/{prefix}")
    
    # List all objects with this prefix
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    objects_to_delete = []
    for page in pages:
        if 'Contents' in page:
            for obj in page['Contents']:
                objects_to_delete.append({'Key': obj['Key']})
    
    if objects_to_delete:
        print(f"  Found {len(objects_to_delete)} files to delete")
        
        # Delete in batches of 1000 (S3 limit)
        for i in range(0, len(objects_to_delete), 1000):
            batch = objects_to_delete[i:i+1000]
            s3.delete_objects(
                Bucket=bucket,
                Delete={'Objects': batch}
            )
            print(f"  Deleted {len(batch)} files")
        print(f"  ✅ Deleted all files for this video")
    else:
        print(f"  No files found")

print("\n" + "="*80)
print("Clearing processed_videos.json...")

# Clear the processed videos list
processed_videos = []
with open('processed_videos.json', 'w') as f:
    json.dump(processed_videos, f, indent=4)

print("✅ processed_videos.json cleared")
print("="*80)
print("\n✅ All done! Now restart the conversion script to reprocess these videos correctly.")

