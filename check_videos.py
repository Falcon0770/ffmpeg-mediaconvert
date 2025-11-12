import boto3

# Initialize S3 client
s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
prefix = "AI CERTs/Synthesia V3 Videos/AI+ Writer/"

print(f"Checking S3 bucket: {bucket}")
print(f"Prefix: {prefix}")
print("-" * 60)

# List objects
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv')
videos = []

for page in pages:
    if "Contents" in page:
        for obj in page["Contents"]:
            key = obj["Key"]
            if key.lower().endswith(video_extensions):
                videos.append(key)
                print(f"Found video: {key}")

print("-" * 60)
print(f"Total videos found: {len(videos)}")

