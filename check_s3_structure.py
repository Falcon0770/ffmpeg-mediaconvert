import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
prefix = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/"

print(f"Checking S3 structure in:")
print(f"s3://{bucket}/{prefix}")
print("=" * 80)

paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter='/')

# List folders
for page in pages:
    if 'CommonPrefixes' in page:
        for prefix_obj in page['CommonPrefixes']:
            folder = prefix_obj['Prefix']
            print(f"FOLDER: {folder}")

print("\n" + "=" * 80)
print("Checking one video folder in detail:")
print("=" * 80)

# Check a specific video folder
video_prefix = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/"
response = s3.list_objects_v2(Bucket=bucket, Prefix=video_prefix, MaxKeys=10)

if 'Contents' in response:
    for obj in response['Contents']:
        print(f"FILE: {obj['Key']}")
else:
    print("No files found")

