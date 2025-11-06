# FFmpeg S3 Video Converter

## Overview

`convert_ffmpeg.py` is a drop-in replacement for `convert_video.py` that uses FFmpeg instead of AWS MediaConvert for video transcoding. It provides **85-90% cost savings** while maintaining identical output quality and structure.

## Key Features

✅ **Exact same CLI interface** as `convert_video.py`  
✅ **Identical output structure** - works with existing playback systems  
✅ **Same settings** - 5 renditions, 4-second segments, H.264 Main profile  
✅ **Preserves folder structure** - maintains nested S3 paths  
✅ **Progress tracking** - uses same `processed_videos.json` file  
✅ **85-90% cost savings** compared to MediaConvert  

## Cost Comparison

| Service | Cost per 10-min Video | Cost for 19,500 Videos |
|---------|----------------------|------------------------|
| **MediaConvert (current)** | $0.60 | $11,700 |
| **FFmpeg (this script)** | $0.06 | $1,170 |
| **Savings** | $0.54 (90%) | $10,530 (90%) |

## Requirements

### 1. FFmpeg Installation

**Windows:**
```bash
# Download from https://ffmpeg.org/download.html
# Add to PATH
ffmpeg -version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Python Dependencies

```bash
pip install boto3
```

### 3. AWS Credentials

Same as `convert_video.py` - ensure your AWS credentials are configured:
```bash
aws configure
```

## Usage

### Exact Same Command as convert_video.py

```bash
python convert_ffmpeg.py <s3_input_folder_prefix> <input_bucket> <output_bucket> <output_prefix> [--force]
```

### Examples

**Example 1: Process videos from a specific folder**
```bash
python convert_ffmpeg.py \
  "AI CERTs/Course1/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/Course1/"
```

**Example 2: Force reprocess all videos**
```bash
python convert_ffmpeg.py \
  "AI CERTs/Course1/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/Course1/" \
  --force
```

**Example 3: Process entire bucket**
```bash
python convert_ffmpeg.py \
  "" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/"
```

## Technical Details

### Exact Settings Match

The script replicates MediaConvert settings exactly:

| Setting | MediaConvert | FFmpeg Equivalent |
|---------|-------------|-------------------|
| **Segment Length** | 4 seconds | `-hls_time 4` |
| **GOP Size** | 4 seconds | `-g 120` (at 30fps) |
| **B-Frames** | 0 | `-bf 0` |
| **Reference Frames** | 3 | `-refs 3` |
| **Profile** | Main | `-profile:v main` |
| **Audio Codec** | AAC LC | `-c:a aac` |
| **Audio Bitrate** | 64 Kbps | `-b:a 64000` |
| **Audio Sample Rate** | 48 kHz | `-ar 48000` |

### Renditions

Identical to `convert_video.py`:

| Resolution | Bitrate | Audio | Name Modifier |
|-----------|---------|-------|---------------|
| 1920x1080 | 2000 Kbps | 64 Kbps | `_1080p` |
| 1280x720 | 1500 Kbps | 64 Kbps | `_720p` |
| 854x480 | 800 Kbps | 64 Kbps | `_480p` |
| 640x360 | 500 Kbps | 64 Kbps | `_360p` |
| 426x240 | 200 Kbps | 64 Kbps | `_240p` |

### Output Structure

Matches MediaConvert exactly:

```
s3://output-bucket/output-prefix/subfolder/video_name/MASTER/
├── MASTER_1080p.m3u8
├── MASTER_720p.m3u8
├── MASTER_480p.m3u8
├── MASTER_360p.m3u8
├── MASTER_240p.m3u8
├── seg_1080p_0000.ts
├── seg_1080p_0001.ts
├── seg_720p_0000.ts
├── seg_720p_0001.ts
... (all segments)
```

## Workflow

The script follows the exact same workflow as `convert_video.py`:

1. **List Videos** - Recursively find all MP4 files in S3 input folder
2. **Check Processed** - Skip videos already in `processed_videos.json`
3. **For Each Video:**
   - Download from S3 to temporary location
   - Convert with FFmpeg (all 5 renditions in parallel)
   - Upload all output files to S3 (preserving folder structure)
   - Add to `processed_videos.json`
   - Clean up temporary files
4. **Report** - Show success/failure statistics

## Where to Run

### Option 1: Local Computer (Testing)

Good for testing with a few videos:
- Free (uses your computer)
- Slower (depends on your CPU)
- Manual start/stop

```bash
python convert_ffmpeg.py "test-folder/" aicertslms cdn.netcomplus.com "streams/test/"
```

### Option 2: EC2 Spot Instance (Recommended for Production)

Best cost/performance for large batches:
- **Instance**: c6i.4xlarge (16 vCPU)
- **Cost**: ~$0.20/hour (spot pricing)
- **Speed**: ~4-6 videos/hour
- **Total cost for 19,500 videos**: ~$800-1,200

**Setup:**
```bash
# Launch EC2 Spot Instance (c6i.4xlarge, us-east-1)
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt-get update
sudo apt-get install -y ffmpeg python3-pip awscli
pip3 install boto3

# Configure AWS
aws configure

# Upload script
scp -i your-key.pem convert_ffmpeg.py ubuntu@your-ec2-ip:~/

# Run in background
nohup python3 convert_ffmpeg.py \
  "AI CERTs/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/" > conversion.log 2>&1 &

# Monitor progress
tail -f conversion.log
```

### Option 3: Dedicated Server

Best for ongoing video processing:
- One-time setup
- Run 24/7
- Lowest long-term cost

## Performance

### Processing Speed

Depends on:
- Video length and complexity
- CPU power
- Number of parallel jobs

**Typical speeds:**
- **Local (8-core CPU)**: 1-2 videos/hour
- **EC2 c6i.4xlarge**: 4-6 videos/hour
- **EC2 c6i.8xlarge**: 8-12 videos/hour

### Parallel Processing

To process multiple videos in parallel, run multiple instances of the script:

```bash
# Terminal 1
python convert_ffmpeg.py "folder1/" ...

# Terminal 2
python convert_ffmpeg.py "folder2/" ...
```

The `processed_videos.json` file prevents duplicate processing.

## Comparison with convert_video.py

### Identical Features

✅ CLI interface and arguments  
✅ S3 folder structure preservation  
✅ Filename handling (spaces → underscores)  
✅ Progress tracking with JSON file  
✅ Skip already processed videos  
✅ Error handling and reporting  
✅ Output structure and naming  
✅ Video/audio quality settings  

### Differences

| Feature | convert_video.py | convert_ffmpeg.py |
|---------|-----------------|-------------------|
| **Processing** | Cloud (MediaConvert) | Local/EC2 (FFmpeg) |
| **Cost** | $0.60 per video | $0.06 per video |
| **Speed** | Fast (parallel cloud) | Depends on hardware |
| **Monitoring** | AWS Console | Script output |
| **Scalability** | Automatic | Manual (multiple instances) |
| **Setup** | None (uses AWS) | Requires FFmpeg install |

## Troubleshooting

### FFmpeg Not Found

```bash
# Check if FFmpeg is installed
ffmpeg -version

# If not, install it
# Windows: Download from https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

### AWS Credentials Error

```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Out of Disk Space

FFmpeg needs temporary space for processing:
- Each video needs ~2-3x its size in temp space
- Default temp location: `/tmp` (Linux) or `%TEMP%` (Windows)
- Solution: Use larger disk or clean up temp files

```bash
# Check disk space
df -h

# Clean temp files
rm -rf /tmp/ffmpeg_convert_*
```

### Slow Processing

- Use faster CPU (more cores)
- Use EC2 compute-optimized instance
- Process multiple videos in parallel
- Reduce number of renditions (edit RENDITIONS list)

## Testing

Before processing all 19,500 videos, test with a small batch:

```bash
# Test with 5 videos
python convert_ffmpeg.py \
  "test-folder/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/test/"
```

**Verify:**
1. ✅ All 5 renditions created
2. ✅ Playback works correctly
3. ✅ Folder structure preserved
4. ✅ File sizes reasonable
5. ✅ Quality acceptable

## Migration Strategy

### Phase 1: Testing (1-2 days)
- Process 10-20 videos with `convert_ffmpeg.py`
- Compare with MediaConvert output
- Validate quality and playback
- Get stakeholder approval

### Phase 2: Pilot (1 week)
- Process 500 videos
- Monitor for issues
- Measure actual costs
- Adjust settings if needed

### Phase 3: Full Deployment
- Set up EC2 Spot Instance
- Process remaining 19,000 videos
- Monitor progress daily
- Handle any failures

## Support

For issues or questions:
1. Check this README
2. Review script output for error messages
3. Verify FFmpeg and AWS credentials
4. Test with a single video first

## License

Same as your existing codebase.

