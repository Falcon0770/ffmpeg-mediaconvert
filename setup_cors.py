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
print("Setting up CORS for S3 Bucket")
print("="*60)
print(f"Bucket: {bucket_name}\n")

# Define CORS configuration
cors_config = {
    'CORSRules': [
        {
            'AllowedHeaders': ['*'],
            'AllowedMethods': ['GET', 'HEAD'],
            'AllowedOrigins': ['*'],
            'ExposeHeaders': ['ETag', 'Content-Length', 'Content-Type'],
            'MaxAgeSeconds': 3000
        }
    ]
}

print("📝 CORS Configuration to apply:")
print(json.dumps(cors_config, indent=2))
print()

try:
    # Apply CORS configuration
    s3.put_bucket_cors(
        Bucket=bucket_name,
        CORSConfiguration=cors_config
    )
    print("✅ CORS configuration applied successfully!")
    print()
    print("🎉 Your videos should now work in web browsers and online players!")
    print()
    print("Test again at:")
    print("https://hls-js.netlify.app/demo/?src=https%3A//cdn.netcomplus.com/streams/AI%2520CERTs/Synthesia%2520V3%2520Videos/AI%252B%2520Writer/Intro%2520and%2520Summary/AI%252B_Writer-V3-Course_Introduction/master.m3u8")
    
except Exception as e:
    print(f"❌ Failed to apply CORS: {e}")
    print()
    print("You may need to apply this manually in AWS Console:")
    print("1. Go to S3 → cdn.netcomplus.com")
    print("2. Click 'Permissions' tab")
    print("3. Scroll to 'Cross-origin resource sharing (CORS)'")
    print("4. Click 'Edit' and paste the configuration above")

print("\n" + "="*60)

