import subprocess
import sys

# Run the conversion script
cmd = [
    sys.executable,
    "convert_ffmpeg.py",
    "AI CERTs/Synthesia V3 Videos/AI+ Writer/",
    "cdn.netcomplus.com",
    "cdn.netcomplus.com",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/"
]

print("="*60)
print("Starting FFmpeg Video Conversion")
print("="*60)
print(f"Command: {' '.join(cmd)}")
print("="*60)
print()

# Run with real-time output
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    universal_newlines=True
)

# Print output in real-time
for line in process.stdout:
    print(line, end='')

process.wait()
print()
print("="*60)
print(f"Process completed with exit code: {process.returncode}")
print("="*60)

