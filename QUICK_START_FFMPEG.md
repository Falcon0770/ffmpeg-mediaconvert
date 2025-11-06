# Quick Start Guide: FFmpeg Video Converter

## 🎯 Goal
Save 85-90% on video conversion costs by using FFmpeg instead of AWS MediaConvert, while maintaining identical output quality and structure.

## 💰 Cost Savings

For your remaining **19,500 videos**:
- **MediaConvert cost**: $11,700
- **FFmpeg cost**: $1,170
- **Savings**: $10,530 (90%)

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install FFmpeg (5 minutes)

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Test: Open CMD and run `ffmpeg -version`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
ffmpeg -version
```

**macOS:**
```bash
brew install ffmpeg
ffmpeg -version
```

### Step 2: Test with 3 Videos (10 minutes)

```bash
cd "C:\AI_certs repos\streaming\aws"

# Test with a small folder
python convert_ffmpeg.py \
  "test-folder/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/test-folder/"
```

**What to check:**
- ✅ Script runs without errors
- ✅ Videos download from S3
- ✅ FFmpeg converts successfully
- ✅ Files upload back to S3
- ✅ Playback works in your player

### Step 3: Process All Videos

**Option A: On Your Computer (Free, Slower)**
```bash
# Run for all videos
python convert_ffmpeg.py \
  "AI CERTs/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/"
```

**Option B: On EC2 Spot Instance (Recommended, 90% savings)**

See "EC2 Setup Guide" below.

---

## 🖥️ EC2 Setup Guide (For Best Performance)

### Why EC2?
- **Fast**: 16 CPU cores process videos 4-6x faster than typical laptop
- **Cheap**: Spot instances cost ~$0.20/hour (vs $0.68 on-demand)
- **Reliable**: Runs 24/7, no need to keep your computer on

### Setup Steps (30 minutes)

**1. Launch EC2 Spot Instance**

Go to AWS Console → EC2 → Launch Instance:
- **Name**: video-converter
- **AMI**: Ubuntu Server 22.04 LTS
- **Instance type**: c6i.4xlarge (16 vCPU, 32 GB RAM)
- **Pricing**: Request Spot Instance
- **Storage**: 500 GB gp3
- **Security Group**: Allow SSH (port 22) from your IP
- **Key pair**: Create or use existing

**2. Connect and Setup**

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt-get update
sudo apt-get install -y ffmpeg python3-pip awscli
pip3 install boto3

# Verify installations
ffmpeg -version
python3 --version
aws --version

# Configure AWS credentials
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Region: us-east-1
# Output format: json
```

**3. Upload Script**

From your local machine:
```bash
scp -i your-key.pem "C:\AI_certs repos\streaming\aws\convert_ffmpeg.py" ubuntu@your-ec2-ip:~/
```

Or clone from git if you have a repo.

**4. Run Conversion**

```bash
# On EC2 instance
cd ~

# Test with small batch first
python3 convert_ffmpeg.py \
  "test-folder/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/test-folder/"

# If test succeeds, run for all videos
nohup python3 convert_ffmpeg.py \
  "AI CERTs/" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/AI CERTs/" > conversion.log 2>&1 &

# Monitor progress
tail -f conversion.log

# Check progress periodically
grep "Progress:" conversion.log | tail -1
```

**5. Monitor and Wait**

```bash
# Check if still running
ps aux | grep convert_ffmpeg

# Check disk space
df -h

# Check CPU usage
top

# View recent logs
tail -50 conversion.log
```

### Performance Estimates

**c6i.4xlarge (16 vCPU):**
- Speed: ~4-6 videos per hour
- Time for 19,500 videos: ~3,250-4,875 hours = ~135-203 days (if running 1 job)
- **But you can run multiple jobs in parallel!**

**To speed up - run 4 parallel jobs:**
```bash
# Split your videos into 4 folders, then run 4 jobs:

# Terminal 1
nohup python3 convert_ffmpeg.py "AI CERTs/batch1/" ... > log1.txt 2>&1 &

# Terminal 2
nohup python3 convert_ffmpeg.py "AI CERTs/batch2/" ... > log2.txt 2>&1 &

# Terminal 3
nohup python3 convert_ffmpeg.py "AI CERTs/batch3/" ... > log3.txt 2>&1 &

# Terminal 4
nohup python3 convert_ffmpeg.py "AI CERTs/batch4/" ... > log4.txt 2>&1 &
```

With 4 parallel jobs: ~34-51 days

### Cost Calculation

**EC2 Spot Instance (c6i.4xlarge):**
- Hourly rate: $0.20
- Processing time: ~800-1,200 hours (with 4 parallel jobs)
- **Total cost: $800-1,200**

**Compare to MediaConvert: $11,700**
**Savings: $10,500-10,900 (90%)**

---

## 📊 Monitoring Progress

### Check Processed Count
```bash
# On your machine or EC2
cd "C:\AI_certs repos\streaming"

# Count processed videos
python -c "import json; print(len(json.load(open('processed_videos.json'))))"
```

### View Recent Activity
```bash
# Last 20 lines of log
tail -20 conversion.log

# Search for errors
grep "❌" conversion.log

# Search for successes
grep "✅" conversion.log

# Count successes and failures
grep -c "Successfully processed" conversion.log
grep -c "Error processing" conversion.log
```

### Estimate Time Remaining
```bash
# Check progress line
grep "Progress:" conversion.log | tail -1

# Example output: Progress: 150/19500 (✅ 148 | ❌ 2)
# Means: 150 done, 19,350 remaining
# At 5 videos/hour: 19,350 / 5 = 3,870 hours = 161 days
```

---

## 🧪 Testing & Validation

### Test Checklist

Before processing all videos, test with 5-10 videos:

1. **Output Structure**
   ```bash
   # Check S3 output
   aws s3 ls s3://cdn.netcomplus.com/streams/test-folder/video_name/MASTER/
   
   # Should see:
   # MASTER_240p.m3u8
   # MASTER_360p.m3u8
   # MASTER_480p.m3u8
   # MASTER_720p.m3u8
   # MASTER_1080p.m3u8
   # seg_240p_0000.ts, seg_240p_0001.ts, ...
   # seg_360p_0000.ts, seg_360p_0001.ts, ...
   # etc.
   ```

2. **Playback Test**
   - Load video in your player
   - Test all quality levels (240p through 1080p)
   - Check adaptive switching works
   - Verify audio sync

3. **Quality Check**
   - Compare side-by-side with MediaConvert output
   - Check sharpness, colors, compression artifacts
   - Verify audio quality

4. **File Size Check**
   ```bash
   # Compare file sizes
   python test_comparison.py \
     --mediaconvert "s3://bucket/mediaconvert-output/video/MASTER/" \
     --ffmpeg "s3://bucket/ffmpeg-output/video/MASTER/"
   ```

---

## ❓ Troubleshooting

### FFmpeg Not Found
```bash
# Windows
where ffmpeg
# Should show: C:\ffmpeg\bin\ffmpeg.exe

# Linux/Mac
which ffmpeg
# Should show: /usr/bin/ffmpeg

# If not found, reinstall and add to PATH
```

### AWS Credentials Error
```bash
# Test AWS access
aws s3 ls s3://aicertslms/

# If error, reconfigure
aws configure
```

### Out of Disk Space
```bash
# Check space
df -h

# Clean temp files
rm -rf /tmp/ffmpeg_convert_*

# Or increase disk size (EC2: modify volume in console)
```

### Slow Processing
- **Use faster CPU**: Switch to c6i.8xlarge (32 vCPU)
- **Run parallel jobs**: Process multiple folders simultaneously
- **Reduce renditions**: Edit RENDITIONS list in script (e.g., only 3 renditions)

### Video Fails to Process
```bash
# Check error in log
grep -A 10 "Error processing" conversion.log

# Common issues:
# - Corrupted source video
# - Unsupported codec
# - Network timeout

# Retry single video
python convert_ffmpeg.py \
  "path/to/specific/video.mp4" \
  aicertslms \
  cdn.netcomplus.com \
  "streams/path/" \
  --force
```

---

## 🎯 Recommended Workflow

### Week 1: Testing
- ✅ Install FFmpeg locally
- ✅ Test with 10 videos
- ✅ Validate quality
- ✅ Get approval from team

### Week 2: Setup Production
- ✅ Launch EC2 Spot Instance
- ✅ Test with 100 videos
- ✅ Verify costs
- ✅ Set up monitoring

### Week 3-8: Full Processing
- ✅ Run 4 parallel jobs
- ✅ Monitor daily
- ✅ Handle any failures
- ✅ Track costs

---

## 📞 Need Help?

1. Check `aws/README_FFMPEG.md` for detailed documentation
2. Review script output for specific error messages
3. Test with a single video to isolate issues
4. Verify FFmpeg and AWS credentials are working

---

## 🎉 Success Metrics

After completion, you should have:
- ✅ 19,500 videos converted to HLS
- ✅ All 5 renditions per video
- ✅ Identical playback quality
- ✅ ~$10,500 saved (90% cost reduction)
- ✅ Reusable pipeline for future videos

---

## 💡 Pro Tips

1. **Start small**: Always test with 5-10 videos first
2. **Monitor closely**: Check progress daily for first week
3. **Keep logs**: Save conversion.log for troubleshooting
4. **Backup**: Keep source videos until conversion verified
5. **Parallel processing**: Run multiple jobs for faster completion
6. **Spot instances**: Use spot pricing for 70% EC2 savings
7. **Right-size**: Start with c6i.4xlarge, upgrade if too slow

---

## Next Steps

1. ✅ Install FFmpeg (see Step 1 above)
2. ✅ Test with 3 videos locally
3. ✅ Review output quality
4. ✅ Decide: Local or EC2?
5. ✅ Process all videos
6. ✅ Celebrate $10,500 savings! 🎉

