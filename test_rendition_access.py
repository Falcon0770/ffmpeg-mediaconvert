import urllib.request
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("Testing Rendition Playlist Access")
print("="*60)

# Test FFmpeg rendition
ffmpeg_url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/AI%2B_Writer-V3-Course_Introduction_240p.m3u8"

print(f"\n1. FFmpeg 240p rendition:")
print(f"   {ffmpeg_url}")
try:
    response = urllib.request.urlopen(ffmpeg_url)
    content = response.read().decode('utf-8')
    print(f"   ✅ Status: {response.status}")
    print(f"   ✅ Content-Type: {response.headers.get('Content-Type')}")
    lines = content.split('\n')[:10]
    print(f"   First 10 lines:")
    for line in lines:
        print(f"      {line}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test MediaConvert rendition
mc_url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20UX%20Designer%20/Introduction%20-%20Summary%20/AI%2B_UX_Designer-V3-Course_Introduction/MASTER240p.m3u8"

print(f"\n2. MediaConvert 240p rendition (WORKING):")
print(f"   {mc_url}")
try:
    response = urllib.request.urlopen(mc_url)
    content = response.read().decode('utf-8')
    print(f"   ✅ Status: {response.status}")
    print(f"   ✅ Content-Type: {response.headers.get('Content-Type')}")
    lines = content.split('\n')[:10]
    print(f"   First 10 lines:")
    for line in lines:
        print(f"      {line}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test segment file
seg_url = "https://cdn.netcomplus.com/streams/AI%20CERTs/Synthesia%20V3%20Videos/AI%2B%20Writer/Intro%20and%20Summary/AI%2B_Writer-V3-Course_Introduction/AI%2B_Writer-V3-Course_Introduction_240p00000.ts"

print(f"\n3. FFmpeg segment file:")
print(f"   {seg_url}")
try:
    response = urllib.request.urlopen(seg_url)
    print(f"   ✅ Status: {response.status}")
    print(f"   ✅ Content-Type: {response.headers.get('Content-Type')}")
    print(f"   ✅ Size: {len(response.read())} bytes")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)

