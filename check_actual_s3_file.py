import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/MASTER.m3u8"

print(f"Downloading ACTUAL file from S3 RIGHT NOW:")
print(f"s3://{bucket}/{key}")
print("="*80)

response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8')

print("ACTUAL CONTENT ON S3:")
print(content)
print("\n" + "="*80)

print("\nSearching for playlist references:")
for i, line in enumerate(content.split('\n'), 1):
    if '.m3u8' in line and not line.startswith('#'):
        has_underscore = '_' in line
        print(f"Line {i}: {line.strip()}")
        if has_underscore:
            print("  ✅ HAS underscore")
        else:
            print("  ❌ NO underscore - THIS IS THE PROBLEM!")

print("\n" + "="*80)
print(f"Last Modified: {response['LastModified']}")
print(f"ETag: {response['ETag']}")

