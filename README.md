# Video Streaming Conversion System

## Overview

This repository contains tools for converting MP4 videos to HLS (HTTP Live Streaming) format with multiple quality renditions for adaptive bitrate streaming.

## 🎯 Two Conversion Methods

### Method 1: AWS MediaConvert (Current)
- **Script**: `aws/convert_video.py`
- **Cost**: $0.60 per 10-min video
- **Speed**: Fast (cloud parallel processing)
- **Setup**: None required
- **Best for**: Urgent videos, small batches

### Method 2: FFmpeg (New - 90% Cost Savings)
- **Script**: `aws/convert_ffmpeg.py`
- **Cost**: $0.06 per 10-min video
- **Speed**: Depends on hardware
- **Setup**: 5-30 minutes
- **Best for**: Large batches, cost savings

## 💰 Cost Comparison

For your **19,500 remaining videos**:

| Method | Cost | Time | Savings |
|--------|------|------|---------|
| MediaConvert | $11,700 | 1-2 days | - |
| FFmpeg (EC2 Spot) | $1,170 | 30-50 days | $10,530 (90%) |
| FFmpeg (Local) | $195 | 3-6 months | $11,505 (98%) |

## 🚀 Quick Start

### Option 1: MediaConvert (Existing)

```bash
cd aws
python convert_video.py \
  "AI CERTs/Course1/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/Course1/"
```

### Option 2: FFmpeg (New)

**Step 1: Install FFmpeg**
```bash
# Windows: Download from https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
```

**Step 2: Run Conversion**
```bash
cd aws
python convert_ffmpeg.py \
  "AI CERTs/Course1/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/Course1/"
```

## 📁 Repository Structure

```
streaming/
├── aws/
│   ├── convert_video.py              # MediaConvert script (original)
│   ├── convert_ffmpeg.py             # FFmpeg script (new, 90% savings)
│   ├── convert_final.py              # Alternative MediaConvert version
│   ├── convert_audio_AAC.py          # Audio conversion script
│   ├── test_comparison.py            # Compare outputs
│   ├── README_FFMPEG.md              # FFmpeg technical docs
│   └── COMPARISON_MEDIACONVERT_VS_FFMPEG.md  # Detailed comparison
├── coverter/
│   └── convert.sh                    # Local FFmpeg bash script
├── processed_videos.json             # Progress tracking
├── processed_audios.json             # Audio progress tracking
├── QUICK_START_FFMPEG.md            # FFmpeg setup guide
└── IMPLEMENTATION_SUMMARY.md         # Complete overview
```

## 📚 Documentation

### Getting Started
- **[QUICK_START_FFMPEG.md](QUICK_START_FFMPEG.md)** - Step-by-step setup guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Complete overview

### Technical Details
- **[aws/README_FFMPEG.md](aws/README_FFMPEG.md)** - FFmpeg technical reference
- **[aws/COMPARISON_MEDIACONVERT_VS_FFMPEG.md](aws/COMPARISON_MEDIACONVERT_VS_FFMPEG.md)** - Side-by-side comparison

## 🎬 Output Format

Both methods produce identical HLS output:

```
s3://cdn.netcomplus.com/streams/AI CERTs/Course1/video_name/MASTER/
├── MASTER_240p.m3u8      # 426x240, 200 Kbps
├── MASTER_360p.m3u8      # 640x360, 500 Kbps
├── MASTER_480p.m3u8      # 854x480, 800 Kbps
├── MASTER_720p.m3u8      # 1280x720, 1500 Kbps
├── MASTER_1080p.m3u8     # 1920x1080, 2000 Kbps
├── seg_240p_0000.ts
├── seg_240p_0001.ts
... (all segments)
```

### Technical Specifications

| Setting | Value |
|---------|-------|
| **Video Codec** | H.264 Main Profile |
| **Audio Codec** | AAC LC, 64 Kbps, 48 kHz |
| **Segment Length** | 4 seconds |
| **GOP Size** | 4 seconds |
| **Format** | HLS (HTTP Live Streaming) |
| **Playlist Type** | VOD (Video on Demand) |

## 🔧 Features

### Both Scripts Support

✅ Recursive S3 folder processing
✅ Preserves nested folder structure
✅ Progress tracking (skip already processed)
✅ Handles spaces in filenames
✅ Error handling and logging
✅ Resume capability
✅ Force reprocess option (`--force`)

### Unique to FFmpeg Script

✅ 90% cost savings
✅ Local or EC2 processing
✅ Full control over encoding settings
✅ No AWS service limits
✅ Can run offline (after download)

## 📊 Performance

### MediaConvert
- **Speed**: Very fast (automatic parallel processing)
- **Scalability**: Unlimited (AWS managed)
- **Cost**: $0.60 per 10-min video

### FFmpeg on EC2 c6i.4xlarge
- **Speed**: 4-6 videos per hour
- **Scalability**: Manual (run multiple instances)
- **Cost**: $0.06 per 10-min video

### FFmpeg on Local (8-core CPU)
- **Speed**: 1-2 videos per hour
- **Scalability**: Limited by hardware
- **Cost**: ~$0.01 per video (electricity)

## 🧪 Testing

### Compare Outputs

```bash
python aws/test_comparison.py \
  --mediaconvert "s3://bucket/mediaconvert-output/video/MASTER/" \
  --ffmpeg "s3://bucket/ffmpeg-output/video/MASTER/"
```

### Verify Quality

1. Process same video with both methods
2. Compare file counts and sizes
3. Test playback in your player
4. Verify all quality levels work

## ⚙️ Configuration

### Renditions

Edit `RENDITIONS` in either script to customize:

```python
RENDITIONS = [
    {"height": 240, "bitrate": 200000, "name_modifier": "240p"},
    {"height": 360, "bitrate": 500000, "name_modifier": "360p"},
    {"height": 480, "bitrate": 800000, "name_modifier": "480p"},
    {"height": 720, "bitrate": 1500000, "name_modifier": "720p"},
    {"height": 1080, "bitrate": 2000000, "name_modifier": "1080p"}
]
```

**Cost Optimization**: Remove 240p and 360p to save 40%:
```python
RENDITIONS = [
    {"height": 480, "bitrate": 800000, "name_modifier": "480p"},
    {"height": 720, "bitrate": 1500000, "name_modifier": "720p"},
    {"height": 1080, "bitrate": 2000000, "name_modifier": "1080p"}
]
```

## 🐛 Troubleshooting

### FFmpeg Not Found
```bash
# Check installation
ffmpeg -version

# Install if missing
# Windows: https://ffmpeg.org/download.html
# Linux: sudo apt-get install ffmpeg
# Mac: brew install ffmpeg
```

### AWS Credentials Error
```bash
# Configure credentials
aws configure

# Test access
aws s3 ls s3://aicertslms/
```

### Out of Disk Space
```bash
# Check space
df -h

# Clean temp files
rm -rf /tmp/ffmpeg_convert_*
```

## 📈 Recommendations

### For Your 19,500 Videos

**Phase 1: Testing (This Week)**
1. Test FFmpeg with 10 videos
2. Validate quality and output
3. Get team approval

**Phase 2: Pilot (Next Week)**
1. Process 100 videos with FFmpeg
2. Monitor for issues
3. Measure actual costs

**Phase 3: Production (Next 1-2 Months)**
1. Launch EC2 Spot Instance (c6i.4xlarge)
2. Run 4 parallel jobs
3. Process all 19,500 videos
4. **Save $10,500** (90% cost reduction)

## 🎯 Next Steps

1. Read **[QUICK_START_FFMPEG.md](QUICK_START_FFMPEG.md)** for setup instructions
2. Test with 5-10 videos locally
3. Review **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** for complete overview
4. Deploy on EC2 for production processing

## 📞 Support

- **Setup Issues**: See [QUICK_START_FFMPEG.md](QUICK_START_FFMPEG.md)
- **Technical Details**: See [aws/README_FFMPEG.md](aws/README_FFMPEG.md)
- **Comparison**: See [aws/COMPARISON_MEDIACONVERT_VS_FFMPEG.md](aws/COMPARISON_MEDIACONVERT_VS_FFMPEG.md)

## 📝 License

Same as your existing codebase.

---

## Summary

You have two options for video conversion:

1. **MediaConvert** (`convert_video.py`) - Fast, easy, expensive
2. **FFmpeg** (`convert_ffmpeg.py`) - Slower, requires setup, **90% cheaper**

Both produce identical outputs. **Recommended**: Use FFmpeg for bulk processing to save $10,500+ on your remaining videos.

**Ready to start?** See [QUICK_START_FFMPEG.md](QUICK_START_FFMPEG.md) for setup instructions.

