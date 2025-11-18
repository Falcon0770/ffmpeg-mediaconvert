# 🛡️ Interrupt Handling & Stale Lock Cleanup Guide

## 📋 What Was Fixed

The parallel processing system had a critical issue: **when workers were interrupted with `Ctrl+C`, they left videos permanently locked** in `in_progress_videos.json`, preventing those videos from ever being processed.

---

## ✅ New Features

### 1. **Graceful Interrupt Handling**

The `convert_ffmpeg.py` script now:
- ✅ **Catches `Ctrl+C` signals** (SIGINT)
- ✅ **Catches termination signals** (SIGTERM)
- ✅ **Automatically releases video locks** before exiting
- ✅ **Shows cleanup messages** so you know what happened

### 2. **Stale Lock Cleanup Script**

A new helper script `cleanup_stale_locks.py` to manually clear all locks.

---

## 🎯 How It Works Now

### **When You Press `Ctrl+C`:**

**Before (OLD behavior):**
```
❌ Worker crashes immediately
❌ Video stays locked forever in in_progress_videos.json
❌ No other worker can pick it up
❌ You have to manually edit the JSON file
```

**After (NEW behavior):**
```
✅ Worker catches the interrupt
✅ Displays: "⚠️  Interrupt received! Cleaning up..."
✅ Releases the video lock automatically
✅ Displays: "🔓 Releasing lock on: [video path]"
✅ Exits cleanly
✅ Video becomes available for other workers
```

---

## 🔧 Usage

### **Normal Operation (No Changes Needed)**

Just use `Ctrl+C` as usual to stop a worker. The script will:
1. Catch the signal
2. Release its current video
3. Exit cleanly

Example output:
```
^C
⚠️  Interrupt received! Cleaning up...
🔓 Releasing lock on: Soft Skills/Video.mp4
✅ Cleanup complete. Exiting.
```

---

### **Manual Cleanup (If Something Goes Wrong)**

If workers crash without cleanup (power loss, kill -9, etc.), use the cleanup script:

```bash
python3 cleanup_stale_locks.py
```

**Output:**
```
============================================================
🧹 Cleanup Stale Locks
============================================================
⚠️  Found 11 locked videos:
   1. Soft Skills/Video1.mp4
   2. Soft Skills/Video2.mp4
   ...
   11. Soft Skills/Video11.mp4

✅ Cleared 11 stale locks!
All videos are now available for processing.
============================================================
```

---

## 🚨 Emergency Cleanup on EC2

If you have too many stale locks and need to restart:

```bash
# Option 1: Use the cleanup script
cd ~/ffmpeg-mediaconvert
python3 cleanup_stale_locks.py

# Option 2: Manual reset (fastest)
echo "[]" > ~/ffmpeg-mediaconvert/in_progress_videos.json

# Then restart workers
tmux kill-session -t video_conversion
./start_4_workers.sh
```

---

## 📊 Checking Lock Status

### **See currently locked videos:**
```bash
cat in_progress_videos.json
```

### **Count locks:**
```bash
cat in_progress_videos.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)))"
```

### **See completed videos:**
```bash
cat processed_videos.json
```

---

## 🛠️ Technical Details

### **Signal Handlers Registered:**

1. **SIGINT** (`Ctrl+C`) - User interrupt
2. **SIGTERM** - Termination request (from `kill` command)

### **Code Changes:**

1. Added `import signal` at the top
2. Added global variable `CURRENT_VIDEO_KEY` to track current video
3. Created `signal_handler()` function to handle interrupts
4. Registered handlers in main execution
5. Update `CURRENT_VIDEO_KEY` when starting each video
6. Clear `CURRENT_VIDEO_KEY` when done with each video

### **What Still Causes Stale Locks:**

These situations **won't** trigger cleanup (use `cleanup_stale_locks.py`):
- ❌ `kill -9` (force kill)
- ❌ System crash / power loss
- ❌ EC2 instance termination without warning
- ❌ Python segfault / fatal errors

---

## ✅ Best Practices

### **Stopping a Worker:**

**Good:**
```bash
# Press Ctrl+C in the tmux pane
# Worker will clean up automatically
```

**Also Good:**
```bash
# Graceful termination
kill [worker_pid]
```

**Bad:**
```bash
# Force kill (no cleanup!)
kill -9 [worker_pid]
```

### **Restarting All Workers:**

**Recommended approach:**
```bash
# 1. Kill tmux session (sends SIGTERM to all workers)
tmux kill-session -t video_conversion

# 2. Clean up any stale locks (just to be safe)
python3 cleanup_stale_locks.py

# 3. Start fresh
./start_4_workers.sh
```

---

## 📝 Files Modified

1. **`convert_ffmpeg.py`**
   - Added signal handling
   - Added graceful cleanup on interrupt
   
2. **`cleanup_stale_locks.py`** (NEW)
   - Helper script for manual cleanup

3. **`INTERRUPT_HANDLING_GUIDE.md`** (NEW)
   - This guide

---

## 🎯 Summary

**Problem:** Workers left videos locked when interrupted

**Solution:** Automatic cleanup on `Ctrl+C` + manual cleanup script

**Result:** No more permanent locks! 🎉

---

## 🆘 Need Help?

If you see stuck videos:
1. Run `python3 cleanup_stale_locks.py`
2. Restart workers with `./start_4_workers.sh`
3. Monitor with `cat in_progress_videos.json`

That's it! Your parallel processing is now **interrupt-safe**! 🛡️

