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
print("S3 Bucket Configuration Checker")
print("="*60)
print(f"Bucket: {bucket_name}\n")

# Check CORS
print("1️⃣  Checking CORS configuration...")
try:
    cors = s3.get_bucket_cors(Bucket=bucket_name)
    print("✅ CORS is configured:")
    print(json.dumps(cors['CORSRules'], indent=2))
except Exception as e:
    print(f"❌ No CORS configuration found")
    print(f"\n📝 Recommended CORS configuration:")
    cors_config = {
        'CORSRules': [{
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'HEAD'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': []
        }]
    }
    print(json.dumps(cors_config, indent=2))
    
    response = input("\n❓ Would you like to apply this CORS configuration? (yes/no): ")
    if response.lower() == 'yes':
        try:
            s3.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
            print("✅ CORS configuration applied!")
        except Exception as e:
            print(f"❌ Failed to apply CORS: {e}")

# Check bucket policy
print("\n2️⃣  Checking bucket policy...")
try:
    policy = s3.get_bucket_policy(Bucket=bucket_name)
    print("✅ Bucket policy exists")
    print(json.dumps(json.loads(policy['Policy']), indent=2))
except Exception as e:
    print(f"❌ No public read policy found")
    print(f"\n📝 Recommended policy for public read access:")
    policy_config = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }]
    }
    print(json.dumps(policy_config, indent=2))
    
    response = input("\n❓ Would you like to apply this policy? (yes/no): ")
    if response.lower() == 'yes':
        try:
            s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy_config))
            print("✅ Bucket policy applied!")
        except Exception as e:
            print(f"❌ Failed to apply policy: {e}")

# Check one file's metadata
print("\n3️⃣  Checking file Content-Type...")
test_key = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/master.m3u8"
try:
    response = s3.head_object(Bucket=bucket_name, Key=test_key)
    content_type = response.get('ContentType', 'Not set')
    print(f"✅ master.m3u8 Content-Type: {content_type}")
    if content_type != 'application/vnd.apple.mpegurl':
        print(f"⚠️  Should be: application/vnd.apple.mpegurl")
except Exception as e:
    print(f"❌ Could not check file: {e}")

print("\n" + "="*60)
print("Configuration check complete!")
print("="*60)

