# 🛡️ Handling Corrupted and Invalid Files

## 🔍 Problem Identified

Some videos in your S3 bucket are **corrupted or invalid**:

### Common Issues:
1. **macOS metadata files** (files starting with `._`)
   - Created by macOS Finder
   - Size: 0 KB or very small
   - Not actual video files
   - Example: `._10.1.3 Manage items.mp4`

2. **Incomplete uploads**
   - Files with 0 bytes
   - Corrupted MP4 structure (missing "moov atom")

3. **Partial downloads**
   - Files smaller than expected

---

## ✅ Solution Implemented

The script now **automatically skips** these problematic files:

### 1. **In `list_s3_video_objects()` function:**
```python
# Skip macOS metadata files (._filename)
if filename.startswith('._'):
    continue

# Skip files smaller than 1KB (likely corrupted)
if obj.get('Size', 0) < 1024:
    continue
```

### 2. **In `download_from_s3()` function:**
```python
# Double-check file size before downloading
if file_size < 1024:  # Less than 1KB
    print(f"⚠️  Skipping file - too small ({file_size} bytes)")
    return False
```

---

## 📊 What You'll See

### Before (with errors):
```
⬇️  Downloading: ._10.1.3 Manage items.mp4
   File size: 0.00 MB
❌ Error: moov atom not found
```

### After (automatically skipped):
```
📊 Status:
   Total videos in S3: 14380
   Skipped (corrupted/metadata): 125
   Available to process: 14255
```

---

## 🎯 Benefits

1. ✅ **No more FFmpeg errors** from corrupted files
2. ✅ **Automatic filtering** - no manual intervention needed
3. ✅ **Cleaner logs** - only valid videos are processed
4. ✅ **Faster processing** - skips problematic files immediately

---

## 🔧 Manual Cleanup (Optional)

If you want to **remove these files from S3**:

### Option 1: List them first
```bash
aws s3 ls s3://cdn.netcomplus.com/ --recursive | grep "/\._"
```

### Option 2: Delete all `._` files (BE CAREFUL!)
```bash
# DRY RUN first (safe - just shows what would be deleted)
aws s3 rm s3://cdn.netcomplus.com/ --recursive --dryrun --exclude "*" --include "*/._*"

# Actual deletion (only run after verifying dry run!)
aws s3 rm s3://cdn.netcomplus.com/ --recursive --exclude "*" --include "*/._*"
```

### Option 3: Delete files smaller than 1KB
```bash
# This requires a script - let me know if you need it
```

---

## 📝 Notes

- **The script will now skip these automatically** - no action needed!
- Failed files are marked as "FAILED" and can be retried later
- Your workers will continue processing valid videos
- The progress counter will show accurate numbers

---

## 🚀 Next Steps

1. **Upload the updated script** to your EC2 instance
2. **Restart the workers** - they'll automatically skip corrupted files
3. **Monitor the logs** - you'll see "⚠️ Skipping file" messages

---

**Your workers are now smarter and will handle these issues automatically!** ✨

