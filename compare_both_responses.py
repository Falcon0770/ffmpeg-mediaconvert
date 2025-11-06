import urllib.request
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("Comparing FFmpeg vs MediaConvert Responses")
print("="*60)

# FFmpeg video
ffmpeg_url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/master.m3u8"
print(f"\n1. FFmpeg Video (NOT working):")
try:
    response = urllib.request.urlopen(ffmpeg_url)
    print(f"   Status: {response.status}")
    print(f"   Via: {response.headers.get('Via', 'Direct')}")
    print(f"   X-Cache: {response.headers.get('X-Cache', 'N/A')}")
    print(f"   CORS: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
except Exception as e:
    print(f"   Error: {e}")

# MediaConvert video
mc_url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20UX%20Designer%20/Introduction%20-%20Summary%20/AI%2B_UX_Designer-V3-Course_Introduction/MASTER.m3u8"
print(f"\n2. MediaConvert Video (WORKING):")
try:
    response = urllib.request.urlopen(mc_url)
    print(f"   Status: {response.status}")
    print(f"   Via: {response.headers.get('Via', 'Direct')}")
    print(f"   X-Cache: {response.headers.get('X-Cache', 'N/A')}")
    print(f"   CORS: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("💡 If both show CloudFront, try invalidating the cache")
print("   or wait 5-10 minutes for cache to expire")
print("="*60)

