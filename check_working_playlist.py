import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/MASTER.m3u8"

print(f"Downloading: s3://{bucket}/{key}")
print("="*80)

try:
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    print("MASTER.m3u8 content:")
    print(content)
    print("="*80)
    print("\nThis playlist references these files:")
    lines = content.split('\n')
    for line in lines:
        if line.endswith('.m3u8'):
            print(f"  - {line}")
except Exception as e:
    print(f"Error: {e}")

