import urllib.parse
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Your video path
bucket = "cdn.netcomplus.com"
path = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/master.m3u8"

# URL encode the path
encoded_path = urllib.parse.quote(path)

# Full URL
url = f"https://{bucket}/{encoded_path}"

print("="*80)
print("🎬 HLS Video URLs")
print("="*80)
print(f"\n📺 Video 1: AI+ Writer - Course Introduction")
print(f"URL: {url}")
print(f"\n📋 Test in online player:")
print(f"   https://hls-js.netlify.app/demo/?src={urllib.parse.quote(url)}")
print(f"\n   OR")
print(f"\n   https://www.hlsplayer.net/ (paste the URL above)")

# Video 2
path2 = "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Summary/master.m3u8"
encoded_path2 = urllib.parse.quote(path2)
url2 = f"https://{bucket}/{encoded_path2}"

print(f"\n\n📺 Video 2: AI+ Writer - Course Summary")
print(f"URL: {url2}")
print(f"\n📋 Test in online player:")
print(f"   https://hls-js.netlify.app/demo/?src={urllib.parse.quote(url2)}")

print("\n" + "="*80)
print("⚠️  If videos don't play, check:")
print("   1. S3 bucket has public read access")
print("   2. CORS is configured for video streaming")
print("   3. Files have correct Content-Type headers")
print("="*80)

