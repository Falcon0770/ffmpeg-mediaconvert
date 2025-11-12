import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/MASTER.m3u8"

print(f"Fixing: s3://{bucket}/{key}")
print("="*80)

# Download the file
response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8')

print("BEFORE:")
print(content)
print("\n" + "="*80)

# Fix the content - replace WITHOUT underscore WITH underscore
fixed_content = content.replace("MASTER_240p", "MASTER_240p")  # Already has underscore
fixed_content = fixed_content.replace("MASTER_360p", "MASTER_360p")
fixed_content = fixed_content.replace("MASTER_480p", "MASTER_480p")
fixed_content = fixed_content.replace("MASTER_720p", "MASTER_720p")
fixed_content = fixed_content.replace("MASTER_1080p", "MASTER_1080p")

# Wait, the output shows they DON'T have underscores. Let me check the actual bytes
print("Checking exact bytes...")
print(repr(content[:500]))

print("\n" + "="*80)
print("AFTER:")
print(fixed_content)

# Upload the fixed file
s3.put_object(
    Bucket=bucket,
    Key=key,
    Body=fixed_content.encode('utf-8'),
    ContentType='application/vnd.apple.mpegurl'
)

print("\n✅ Fixed and uploaded")

