import urllib.request
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/master.m3u8"

print("="*60)
print("Testing CORS Headers")
print("="*60)

try:
    req = urllib.request.Request(url)
    req.add_header('Origin', 'https://hls-js.netlify.app')
    
    response = urllib.request.urlopen(req)
    
    print(f"\n✅ Status: {response.status}")
    print(f"\n📋 Response Headers:")
    for header, value in response.headers.items():
        print(f"   {header}: {value}")
    
    # Check for CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
    }
    
    print(f"\n🔍 CORS Headers:")
    for header, value in cors_headers.items():
        if value:
            print(f"   ✅ {header}: {value}")
        else:
            print(f"   ❌ {header}: NOT SET")
    
    if not cors_headers['Access-Control-Allow-Origin']:
        print(f"\n⚠️  CORS headers are missing!")
        print(f"   The CORS configuration may not have been applied correctly.")
        print(f"   Try waiting a few minutes for S3 to propagate the changes.")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)

