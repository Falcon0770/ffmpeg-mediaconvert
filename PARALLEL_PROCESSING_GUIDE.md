# 🚀 Parallel Video Processing on EC2 - Complete Guide

## 📋 Overview

This guide explains how to run 4 parallel video conversion workers on an AWS EC2 c6g.xlarge instance using `tmux`.

---

## 🖥️ EC2 Instance Setup

### **1. Launch EC2 Instance**

- **Instance Type**: `c6g.xlarge` (ARM64, 4 vCPUs, 8GB RAM)
- **AMI**: Amazon Linux 2023 (ARM64)
- **Storage**: At least 50GB (for temporary video processing)
- **Security Group**: Allow SSH (port 22) from your IP

### **2. Connect via SSH**

```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

### **3. Run Setup Script**

```bash
# Upload the setup script
scp -i your-key.pem setup_ec2.sh ec2-user@your-instance-ip:~

# SSH into EC2
ssh -i your-key.pem ec2-user@your-instance-ip

# Make it executable and run
chmod +x setup_ec2.sh
./setup_ec2.sh
```

This will install:
- ✅ FFmpeg (ARM64 optimized)
- ✅ Python 3 + boto3
- ✅ AWS CLI v2
- ✅ tmux

### **4. Configure AWS Credentials**

```bash
aws configure
```

Enter:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key
- **Default region**: `us-east-1`
- **Default output format**: `json`

### **5. Upload Your Scripts**

```bash
# From your local machine
scp -i your-key.pem convert_ffmpeg.py ec2-user@your-instance-ip:~/
scp -i your-key.pem processed_videos.json ec2-user@your-instance-ip:~/

# Or clone from GitHub if you have a repo
```

---

## 🎬 tmux Setup for 4 Parallel Workers

### **Step 1: Create tmux Session**

```bash
tmux new -s video_conversion
```

### **Step 2: Split into 4 Panes**

Execute these commands **inside tmux**:

1. Split horizontally (top/bottom):
   ```
   Ctrl+B then "
   ```

2. Move to **top pane**:
   ```
   Ctrl+B then ↑
   ```

3. Split top pane vertically (left/right):
   ```
   Ctrl+B then %
   ```

4. Move to **bottom pane**:
   ```
   Ctrl+B then ↓
   ```

5. Split bottom pane vertically (left/right):
   ```
   Ctrl+B then %
   ```

You now have **4 panes**:

```
┌─────────────┬─────────────┐
│   Pane 1    │   Pane 2    │
├─────────────┼─────────────┤
│   Pane 3    │   Pane 4    │
└─────────────┴─────────────┘
```

### **Step 3: Navigate Between Panes**

```
Ctrl+B then ↑  # Move up
Ctrl+B then ↓  # Move down
Ctrl+B then ←  # Move left
Ctrl+B then →  # Move right
```

### **Step 4: Run Script in Each Pane**

Navigate to each pane and run:

```bash
python3 convert_ffmpeg.py \
  "AI CERTs/Synthesia V3 Videos/AI+ Writer/" \
  cdn.netcomplus.com \
  cdn.netcomplus.com \
  "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/"
```

**All 4 workers will now run in parallel!** 🎉

---

## 🔒 How File Locking Works

### **Parallel Processing Safety**

The updated `convert_ffmpeg.py` uses **file locking** to ensure:

1. ✅ **No duplicate processing** - Each worker picks a different video
2. ✅ **Thread-safe** - Multiple processes can run simultaneously
3. ✅ **Resume capability** - Failed videos can be retried later

### **State Files**

- `processed_videos.json` - Videos that have been successfully processed
- `in_progress_videos.json` - Videos currently being processed

### **How It Works**

1. Worker 1 **locks** the file, picks Video A, marks it "in progress", **unlocks**
2. Worker 2 **locks** the file, sees Video A is taken, picks Video B, **unlocks**
3. Worker 3 picks Video C, Worker 4 picks Video D
4. When Worker 1 finishes, Video A moves from "in progress" to "processed"
5. Worker 1 then picks the next available video (Video E)

---

## 🛠️ tmux Essential Commands

### **Detach from Session (Keep Running in Background)**

```
Ctrl+B then d
```

- Your workers **keep running** even after you close SSH!
- You can safely close your local machine

### **Reattach to Session**

```bash
tmux attach -t video_conversion
```

### **List All Sessions**

```bash
tmux ls
```

### **Kill a Session**

```bash
tmux kill-session -t video_conversion
```

### **Scroll/View History in a Pane**

```
Ctrl+B then [
# Use arrow keys or Page Up/Down
# Press Q to exit scroll mode
```

### **Stop a Worker in One Pane**

```
Ctrl+C
```

---

## 📊 Monitoring Progress

### **In Each Pane**

You'll see:
```
📊 Overall Progress:
   ✅ Completed: 25/89
   🔄 In Progress (all workers): 4
   ⏳ Remaining: 60
   This worker: ✅ 6 | ❌ 0
```

### **Check Status from Another Terminal**

```bash
# SSH in a separate window
ssh -i your-key.pem ec2-user@your-instance-ip

# Check processed videos
cat processed_videos.json | grep -c "mp4"

# Check in-progress videos
cat in_progress_videos.json
```

---

## 🔧 Troubleshooting

### **Worker Says "No more videos to process" Immediately**

- Check if all videos are already in `processed_videos.json`
- Or they might be stuck in `in_progress_videos.json`

**Solution**: Clear in-progress list:
```bash
echo "[]" > in_progress_videos.json
```

### **Worker Gets Stuck**

- Press `Ctrl+C` to stop it
- The video will be removed from "in progress" and can be retried
- Start the worker again

### **Disk Space Full**

```bash
df -h  # Check disk usage
```

The script uses `/tmp/` for temporary files. If needed:
```bash
sudo rm -rf /tmp/ffmpeg_convert_*
```

### **AWS Credentials Error**

```bash
aws sts get-caller-identity  # Test credentials
aws configure  # Reconfigure if needed
```

---

## 🎯 Best Practices

### **1. Start with 1-2 Workers First**

Test with fewer workers to ensure everything works:
- Start 1 worker
- Wait for 1 video to complete
- Then start the other 3 workers

### **2. Monitor CPU/Memory**

```bash
htop  # Install: sudo yum install -y htop
```

- c6g.xlarge has 4 vCPUs → Perfect for 4 workers
- Each worker uses ~1 CPU during FFmpeg conversion

### **3. Use Screen Instead of tmux (Alternative)**

If you prefer `screen`:
```bash
sudo yum install -y screen
screen -S video_conversion
# Ctrl+A then C to create new window
# Ctrl+A then " to list windows
```

### **4. Log Output to Files**

```bash
python3 convert_ffmpeg.py ... > worker1.log 2>&1
```

---

## 🧹 Cleanup After Processing

### **1. Verify All Videos Processed**

```bash
python3 -c "
import json
with open('processed_videos.json', 'r') as f:
    videos = json.load(f)
print(f'Total processed: {len(videos)}')
"
```

### **2. Download Logs (if needed)**

```bash
# From your local machine
scp -i your-key.pem ec2-user@your-instance-ip:~/worker*.log .
```

### **3. Stop EC2 Instance**

- **Stop** (keeps storage, can restart later)
- **Terminate** (deletes everything, saves cost)

---

## 💰 Cost Estimation

### **c6g.xlarge Pricing** (us-east-1)
- **On-Demand**: ~$0.136/hour
- **Spot Instance**: ~$0.04-0.06/hour (70% cheaper!)

### **Example Cost**
- **100 videos** × 5 min each = 500 minutes = 8.3 hours
- **4 parallel workers** = 8.3 ÷ 4 = **2.08 hours**
- **Cost**: 2.08 × $0.136 = **$0.28**

💡 **Tip**: Use Spot Instances to save 70%!

---

## 📞 Support

If you encounter issues:
1. Check `processed_videos.json` and `in_progress_videos.json`
2. Review worker logs in tmux panes
3. Test with `--force` flag to reprocess:
   ```bash
   python3 convert_ffmpeg.py ... --force
   ```

---

## 🎉 Summary

✅ **Setup**: Run `setup_ec2.sh` once  
✅ **Start**: `tmux new -s video_conversion`  
✅ **Split**: Create 4 panes  
✅ **Run**: Same command in each pane  
✅ **Detach**: `Ctrl+B then d`  
✅ **Reattach**: `tmux attach -t video_conversion`  
✅ **Monitor**: Check overall progress in any pane  

**Your videos will process in parallel, safely, even after you close SSH!** 🚀

