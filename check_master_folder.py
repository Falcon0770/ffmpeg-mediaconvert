import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/MASTER/MASTER.m3u8"

print(f"Checking: s3://{bucket}/{key}")
print("="*80)

try:
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    print("✅ Found MASTER.m3u8 inside /MASTER/ folder!")
    print("\nContent:")
    print(content[:500])  # First 500 chars
    print("\n" + "="*80)
    print("This file needs to be MOVED UP one level to:")
    print(f"s3://{bucket}/streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/MASTER.m3u8")
except Exception as e:
    print(f"❌ Not found in /MASTER/ folder either: {e}")
    print("\nThis video needs to be reprocessed!")

