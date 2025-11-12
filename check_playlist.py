import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/MASTER.m3u8"

print(f"Downloading: s3://{bucket}/{key}")
print("="*80)

try:
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    print("MASTER.m3u8 content:")
    print(content)
    print("="*80)
except Exception as e:
    print(f"Error: {e}")
    print("\nTrying MASTER folder version...")
    key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/MASTER/MASTER.m3u8"
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        print("MASTER/MASTER.m3u8 content:")
        print(content)
    except Exception as e2:
        print(f"Also failed: {e2}")

