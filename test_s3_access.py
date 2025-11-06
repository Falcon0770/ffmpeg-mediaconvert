import boto3
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test S3 access
s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"
prefix = "AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/"

print(f"Testing S3 access to: s3://{bucket}/{prefix}")
print("="*60)

try:
    print("\nListing objects...")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=10)
    
    if "Contents" in response:
        print(f"\n✅ Found {len(response['Contents'])} objects:")
        for obj in response['Contents']:
            key = obj['Key']
            size_mb = obj['Size'] / (1024 * 1024)
            print(f"  - {key} ({size_mb:.2f} MB)")
    else:
        print("\n❌ No objects found in this path")
        
except Exception as e:
    print(f"\n❌ Error accessing S3: {e}")
    sys.exit(1)

