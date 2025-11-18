# 🚀 FFmpeg Video Converter - Parallel Processing Edition

## ✨ What's New?

This version supports **safe parallel processing** across multiple workers using file locking!

### Key Features:
- ✅ **File Locking** - No duplicate processing
- ✅ **4 Parallel Workers** - Process videos 4x faster
- ✅ **Resume Support** - Failed videos can be retried
- ✅ **Real-time Progress** - See overall status across all workers
- ✅ **EC2 Optimized** - Works perfectly on ARM64 (c6g instances)

---

## 🎯 Quick Start

### **On EC2 (Recommended)**

```bash
# 1. Setup (one-time)
chmod +x setup_ec2.sh
./setup_ec2.sh
aws configure

# 2. Upload your scripts
# (Use scp or git clone)

# 3. Start 4 workers automatically
chmod +x start_4_workers.sh
./start_4_workers.sh

# 4. Attach to see progress
tmux attach -t video_conversion

# 5. Detach (keep running in background)
# Press: Ctrl+B then d
```

### **Manual Startup**

```bash
# In each terminal/pane, run:
python3 convert_ffmpeg.py \
  "AI CERTs/Synthesia V3 Videos/AI+ Writer/" \
  cdn.netcomplus.com \
  cdn.netcomplus.com \
  "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/"
```

---

## 📚 Files Included

| File | Purpose |
|------|---------|
| `convert_ffmpeg.py` | Main conversion script (with parallel support) |
| `setup_ec2.sh` | One-time EC2 setup (FFmpeg, Python, tmux, AWS CLI) |
| `start_4_workers.sh` | Automatically start 4 workers in tmux |
| `PARALLEL_PROCESSING_GUIDE.md` | Complete step-by-step guide |
| `test_parallel_local.py` | Test locking mechanism locally |
| `processed_videos.json` | Videos successfully processed |
| `in_progress_videos.json` | Videos currently being processed |

---

## 🔒 How Parallel Processing Works

1. **Worker 1** locks the file → picks Video A → marks "in progress" → unlocks
2. **Worker 2** locks the file → sees Video A is taken → picks Video B → unlocks
3. **Worker 3** picks Video C, **Worker 4** picks Video D
4. All 4 workers process simultaneously ✅
5. When finished, videos move from "in progress" to "processed"

**No conflicts. No duplicates. Safe and efficient!**

---

## 📊 Progress Monitoring

Each worker shows:

```
📊 Overall Progress:
   ✅ Completed: 25/89        ← All workers combined
   🔄 In Progress: 4          ← Currently processing
   ⏳ Remaining: 60           ← Videos left
   This worker: ✅ 6 | ❌ 0   ← This worker's stats
```

---

## 🛠️ Testing Locally

Before running on EC2, test the locking mechanism:

```bash
# Terminal 1
python3 test_parallel_local.py --reset

# Terminal 2
python3 test_parallel_local.py

# Terminal 3
python3 test_parallel_local.py

# Watch them pick different videos! ✅
```

---

## 💡 Usage Examples

### **Process All Videos**
```bash
python3 convert_ffmpeg.py \
  "AI CERTs/Videos/" \
  input-bucket \
  output-bucket \
  "streams/output/"
```

### **Force Reprocess Everything**
```bash
python3 convert_ffmpeg.py \
  "AI CERTs/Videos/" \
  input-bucket \
  output-bucket \
  "streams/output/" \
  --force
```

### **Resume Failed Videos**
```bash
# Just run the same command again!
# It will automatically skip completed videos
# and retry any that failed before
```

---

## 🧹 Troubleshooting

### **Workers say "No more videos"**

Check status:
```bash
cat processed_videos.json | grep -c "mp4"
cat in_progress_videos.json
```

Clear stuck in-progress:
```bash
echo "[]" > in_progress_videos.json
```

### **Worker crashed**

The video is automatically removed from "in progress" and can be retried.

### **Reset everything**

```bash
rm processed_videos.json in_progress_videos.json
echo "[]" > processed_videos.json
echo "[]" > in_progress_videos.json
```

---

## 🎯 Performance

### **c6g.xlarge (4 vCPUs)**
- **1 Worker**: ~5 min per video
- **4 Workers**: ~5 min per 4 videos (4x faster!)

### **Cost Example**
- **100 videos** = 125 minutes (4 workers) = 2.08 hours
- **Cost**: $0.136/hour × 2.08 = **$0.28**

---

## 🔐 Platform Support

| Platform | File Locking | Parallel Support |
|----------|--------------|------------------|
| Linux (EC2) | ✅ Yes | ✅ Safe |
| macOS | ✅ Yes | ✅ Safe |
| Windows | ⚠️ No | ⚠️ Not recommended |

**Windows users**: Run on EC2 for parallel processing, or run single worker locally.

---

## 📖 Full Documentation

👉 **See `PARALLEL_PROCESSING_GUIDE.md`** for complete setup instructions, tmux guide, and best practices.

---

## 🎉 Summary

✅ Modified `convert_ffmpeg.py` with file locking  
✅ Safe for 4+ parallel workers  
✅ Works on EC2 ARM64 (c6g instances)  
✅ Automatic resume capability  
✅ Real-time progress monitoring  
✅ Easy setup with provided scripts  

**Run multiple workers. Process videos 4x faster. Save time and money!** 🚀

