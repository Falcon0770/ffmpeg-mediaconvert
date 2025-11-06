import boto3
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s3 = boto3.client('s3', region_name='us-east-1')
bucket_name = 'cdn.netcomplus.com'

print("="*60)
print("Setting up Public Read Access for S3 Bucket")
print("="*60)
print(f"Bucket: {bucket_name}\n")

# Define bucket policy for public read access
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}

print("📝 Bucket Policy to apply:")
print(json.dumps(bucket_policy, indent=2))
print()

try:
    # Check existing policy
    try:
        existing = s3.get_bucket_policy(Bucket=bucket_name)
        print("ℹ️  Bucket already has a policy")
        print("   Checking if it allows public read...")
        existing_policy = json.loads(existing['Policy'])
        print(json.dumps(existing_policy, indent=2))
        print()
    except:
        print("ℹ️  No existing bucket policy found")
        print()
    
    response = input("❓ Apply public read policy? This will make ALL files in the bucket publicly accessible. (yes/no): ")
    
    if response.lower() == 'yes':
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("\n✅ Bucket policy applied successfully!")
        print("🎉 All files in the bucket are now publicly readable!")
    else:
        print("\n❌ Policy not applied. Files will remain private.")
        print("\n💡 Alternative: Make only the 'streams/' folder public")
        print("   You can do this in AWS Console:")
        print("   1. Go to S3 → cdn.netcomplus.com")
        print("   2. Select the 'streams' folder")
        print("   3. Actions → Make public using ACL")
    
except Exception as e:
    print(f"\n❌ Failed to apply policy: {e}")
    print("\n⚠️  You may need to:")
    print("   1. Disable 'Block all public access' in bucket settings")
    print("   2. Then apply this policy manually in AWS Console")

print("\n" + "="*60)

