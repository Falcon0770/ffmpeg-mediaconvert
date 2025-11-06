import urllib.request
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test the working MediaConvert URL
url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20UX%20Designer%20/Introduction%20-%20Summary%20/AI%2B_UX_Designer-V3-Course_Introduction/MASTER.m3u8"

print("="*60)
print("Testing MediaConvert URL (WORKING)")
print("="*60)
print(f"\nURL: {url}\n")

try:
    response = urllib.request.urlopen(url)
    print(f"✅ Status: {response.status}")
    print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
    print("\n📋 This is your WORKING MediaConvert video URL")
    print("   Try this in VLC to confirm it works")
except Exception as e:
    print(f"❌ Error: {e}")

