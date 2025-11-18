# ✅ EC2 Deployment Checklist - Parallel Video Processing

Use this checklist to deploy your parallel video processing system on AWS EC2.

---

## 📋 Pre-Deployment (On Your Local Machine)

### **1. Prepare Files**
- [ ] Ensure you have `convert_ffmpeg.py` with parallel processing support
- [ ] Ensure you have `setup_ec2.sh`
- [ ] Ensure you have `start_4_workers.sh`
- [ ] Have your AWS credentials ready (Access Key ID + Secret Access Key)
- [ ] Have your SSH key pair (.pem file) ready

### **2. Test Locally (Optional but Recommended)**
```bash
# Test file locking on your local machine
python test_parallel_local.py --reset

# In another terminal
python test_parallel_local.py

# Verify they pick different videos ✅
```

---

## 🚀 EC2 Launch

### **1. Launch EC2 Instance**
- [ ] Go to AWS EC2 Console → Launch Instance
- [ ] **Name**: `video-conversion-worker`
- [ ] **AMI**: Amazon Linux 2023 (ARM64)
- [ ] **Instance Type**: `c6g.xlarge` (4 vCPUs, 8GB RAM)
- [ ] **Key Pair**: Select or create new key pair
- [ ] **Storage**: 50GB gp3 (or more if processing large videos)
- [ ] **Security Group**: Allow SSH (port 22) from your IP
- [ ] Click **Launch Instance**
- [ ] Wait for **Status: Running** ✅

### **2. Note Instance Details**
```
Public IP: _________________
Instance ID: _________________
Key Pair: _________________
```

---

## 🔧 EC2 Setup

### **1. Upload Files to EC2**
```bash
# From your local machine, in the project directory
scp -i your-key.pem convert_ffmpeg.py ec2-user@YOUR-INSTANCE-IP:~/
scp -i your-key.pem setup_ec2.sh ec2-user@YOUR-INSTANCE-IP:~/
scp -i your-key.pem start_4_workers.sh ec2-user@YOUR-INSTANCE-IP:~/
scp -i your-key.pem processed_videos.json ec2-user@YOUR-INSTANCE-IP:~/
```
- [ ] Files uploaded successfully

### **2. SSH into EC2**
```bash
ssh -i your-key.pem ec2-user@YOUR-INSTANCE-IP
```
- [ ] Connected successfully

### **3. Run Setup Script**
```bash
chmod +x setup_ec2.sh
./setup_ec2.sh
```
- [ ] FFmpeg installed ✅
- [ ] Python 3 installed ✅
- [ ] AWS CLI installed ✅
- [ ] tmux installed ✅
- [ ] boto3 installed ✅

### **4. Configure AWS Credentials**
```bash
aws configure
```
Enter:
- [ ] AWS Access Key ID
- [ ] AWS Secret Access Key
- [ ] Default region: `us-east-1`
- [ ] Default output format: `json`

**Test credentials:**
```bash
aws sts get-caller-identity
```
- [ ] Credentials working ✅

---

## 🎬 Start Processing

### **Method 1: Automatic (Recommended)**

```bash
chmod +x start_4_workers.sh
./start_4_workers.sh
```
- [ ] 4 workers started in tmux

**Attach to view progress:**
```bash
tmux attach -t video_conversion
```
- [ ] Can see all 4 panes ✅

**Detach (keep running):**
```
Press: Ctrl+B then d
```
- [ ] Detached successfully (workers still running in background)

### **Method 2: Manual**

```bash
# Start tmux session
tmux new -s video_conversion

# Split into 4 panes (see PARALLEL_PROCESSING_GUIDE.md for details)
# Then in each pane, run:
python3 convert_ffmpeg.py \
  "AI CERTs/Synthesia V3 Videos/AI+ Writer/" \
  cdn.netcomplus.com \
  cdn.netcomplus.com \
  "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/"
```
- [ ] All 4 workers running

---

## 📊 Monitoring

### **1. Check Initial Status**
After starting workers, you should see:
```
📊 Status:
   Total videos in S3: XX
   Already processed: XX
   Currently in progress: 4
   Available to process: XX

✅ File locking enabled - safe for parallel processing
```
- [ ] Status looks correct

### **2. Monitor Progress**

**Attach to tmux:**
```bash
tmux attach -t video_conversion
```

**Navigate between panes:**
```
Ctrl+B then ↑↓←→  # Arrow keys
```

**Each pane should show:**
```
🎬 Acquired video: AI CERTs/.../video.mp4
   Processing...
📊 Overall Progress:
   ✅ Completed: XX/XX
   🔄 In Progress: 4
   ⏳ Remaining: XX
```
- [ ] All 4 workers processing different videos ✅

### **3. Check from Another Terminal**

```bash
# Open another SSH session
ssh -i your-key.pem ec2-user@YOUR-INSTANCE-IP

# Check processed count
cat processed_videos.json | grep -c "mp4"

# Check in-progress count
cat in_progress_videos.json
```

---

## 🧪 Verification

### **After First Video Completes**

- [ ] Video appears in `processed_videos.json`
- [ ] Video removed from `in_progress_videos.json`
- [ ] Files uploaded to S3 correctly
- [ ] MASTER.m3u8 exists with correct content
- [ ] All rendition playlists exist (240p, 360p, 480p, 720p, 1080p)
- [ ] Segment files (.ts) uploaded

**Test playback:**
- [ ] Copy S3 URL and test in video player
- [ ] Video plays correctly

---

## ⏸️ Safe Shutdown

### **If You Need to Stop**

**In tmux:**
```
Ctrl+C  # In each pane to stop workers
```

**Or detach and let it run:**
```
Ctrl+B then d
```
- [ ] Workers continue in background

**To check if still running:**
```bash
tmux ls
```

**To reattach later:**
```bash
tmux attach -t video_conversion
```

---

## 🔍 Troubleshooting

### **Problem: Worker says "No more videos"**

**Check:**
```bash
cat processed_videos.json | grep -c "mp4"
cat in_progress_videos.json
```

**Solution: Clear stuck in-progress:**
```bash
echo "[]" > in_progress_videos.json
```
- [ ] Fixed

### **Problem: Workers picking same video**

**Check file locking:**
```bash
python3 -c "from convert_ffmpeg import LOCK_AVAILABLE; print(LOCK_AVAILABLE)"
```
- [ ] Should return `True` on Linux

### **Problem: Disk space full**

**Check disk usage:**
```bash
df -h
```

**Clean temp files:**
```bash
sudo rm -rf /tmp/ffmpeg_convert_*
```
- [ ] Disk space freed

### **Problem: AWS credentials error**

```bash
aws sts get-caller-identity
```
- [ ] If fails, run `aws configure` again

---

## 🏁 Completion

### **When All Videos Done**

**Check final status:**
```bash
cat processed_videos.json | grep -c "mp4"
```

**Verify S3:**
```bash
aws s3 ls s3://cdn.netcomplus.com/streams/AI\ CERTs/Synthesia\ V3\ Videos/AI+\ Writer/ --recursive
```
- [ ] All videos in S3 ✅

**Stop workers:**
```bash
tmux kill-session -t video_conversion
```

**Download logs (optional):**
```bash
# From your local machine
scp -i your-key.pem ec2-user@YOUR-INSTANCE-IP:~/processed_videos.json .
```

---

## 💰 Cost Management

### **Stop Instance When Done**
- [ ] Go to EC2 Console
- [ ] Select your instance
- [ ] Instance State → **Stop** (or **Terminate** if completely done)

**Note:** 
- **Stop** = Keeps storage, can restart later
- **Terminate** = Deletes everything, saves maximum cost

---

## 📝 Post-Deployment Notes

### **Performance Metrics**

**Record these for reference:**
```
Total videos: _______
Processing time: _______ hours
Cost: $_______ 
Average time per video: _______ minutes
Workers used: 4
```

### **Issues Encountered**
```
(Note any problems and solutions here)
```

---

## ✅ Success Criteria

All of these should be checked:

- [ ] EC2 instance launched successfully
- [ ] All dependencies installed (FFmpeg, Python, AWS CLI, tmux)
- [ ] AWS credentials configured
- [ ] 4 workers running in parallel
- [ ] Each worker processing different videos (no duplicates)
- [ ] Videos successfully uploaded to S3
- [ ] Playback tested and working
- [ ] All videos processed
- [ ] EC2 instance stopped/terminated

---

## 🎉 Congratulations!

If all items are checked, you've successfully deployed parallel video processing on EC2!

**Next time:** Just upload new videos to S3 and run `./start_4_workers.sh` again! ✨

---

## 📞 Quick Reference

**Start workers:**
```bash
./start_4_workers.sh
```

**Attach to session:**
```bash
tmux attach -t video_conversion
```

**Detach (keep running):**
```
Ctrl+B then d
```

**Stop workers:**
```bash
tmux kill-session -t video_conversion
```

**Check status:**
```bash
cat processed_videos.json | grep -c "mp4"
```

---

**Good luck with your video processing!** 🚀🎬

