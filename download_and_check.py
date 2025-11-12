import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/MASTER.m3u8"

print(f"Downloading fresh: s3://{bucket}/{key}")
print("="*80)

response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8')

print("CURRENT CONTENT:")
print(content)
print("\n" + "="*80)

print("\nParsing references:")
for line in content.split('\n'):
    if line.strip().endswith('.m3u8'):
        print(f"  References: {line.strip()}")
        
        # Check if this file exists
        check_key = f"streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/{line.strip()}"
        try:
            s3.head_object(Bucket=bucket, Key=check_key)
            print(f"    ✅ EXISTS on S3")
        except:
            print(f"    ❌ DOES NOT EXIST on S3!")
            print(f"       Looking for: s3://{bucket}/{check_key}")

print("\n" + "="*80)
print("Checking Content-Type metadata:")
print(f"Content-Type: {response['ContentType']}")
print(f"Metadata: {response.get('Metadata', {})}")

