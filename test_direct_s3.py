import urllib.request
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Direct S3 URL (not through CloudFront)
s3_url = "https://cdn.netcomplus.com.s3.us-east-1.amazonaws.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/master.m3u8"

print("="*60)
print("Testing Direct S3 URL (bypassing CloudFront)")
print("="*60)
print(f"\nURL: {s3_url}\n")

try:
    req = urllib.request.Request(s3_url)
    req.add_header('Origin', 'https://hls-js.netlify.app')
    
    response = urllib.request.urlopen(req)
    
    print(f"✅ Status: {response.status}")
    print(f"✅ CORS: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
    
    if response.headers.get('Access-Control-Allow-Origin'):
        print(f"\n🎉 CORS is working on direct S3!")
        print(f"   The issue is CloudFront caching or configuration")
    else:
        print(f"\n❌ CORS still not working on direct S3")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)

