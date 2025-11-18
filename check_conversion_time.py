import boto3
from datetime import datetime

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"

# Check a few recently processed videos
videos = [
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 2/AI+Writer-V3-2.9/",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.2/",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 5/AI+Writer-V3-5.3/",
]

print("Checking conversion times for recent videos...")
print("="*80)

for video_prefix in videos:
    print(f"\n{video_prefix}")
    
    # List files for this video
    response = s3.list_objects_v2(Bucket=bucket, Prefix=video_prefix, MaxKeys=5)
    
    if 'Contents' in response:
        # Get timestamps
        timestamps = [obj['LastModified'] for obj in response['Contents']]
        if timestamps:
            first_file = min(timestamps)
            last_file = max(timestamps)
            duration = (last_file - first_file).total_seconds() / 60
            
            print(f"  First file: {first_file}")
            print(f"  Last file:  {last_file}")
            print(f"  Duration:   {duration:.1f} minutes")
            
            # Get file size to estimate video length
            total_size = sum(obj['Size'] for obj in response['Contents'][:5])
            print(f"  Total size (sample): {total_size / (1024*1024):.1f} MB")

print("\n" + "="*80)
print("\nNote: This shows upload time, not total conversion time.")
print("Total time = Download + Convert + Upload")

