import urllib.request
import urllib.error
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/master.m3u8"

print("="*60)
print("Testing URL Access")
print("="*60)
print(f"\nURL: {url}\n")

try:
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    print("✅ URL is accessible!")
    print(f"Status Code: {response.status}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print("\nContent:")
    print("-"*60)
    print(content)
    print("-"*60)
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error {e.code}: {e.reason}")
    if e.code == 403:
        print("\n⚠️  This is a PERMISSIONS ERROR!")
        print("   The S3 bucket doesn't allow public access.")
        print("   You need to:")
        print("   1. Make the bucket public, OR")
        print("   2. Add a bucket policy for public read access")
except urllib.error.URLError as e:
    print(f"❌ URL Error: {e.reason}")
except Exception as e:
    print(f"❌ Error: {e}")

