#!/usr/bin/env python3
"""
Cleanup Stale Locks - Helper Script
Removes all entries from in_progress_videos.json
Use this when workers crash and leave videos locked
"""

import json
import os

IN_PROGRESS_FILE = "in_progress_videos.json"

def cleanup_locks():
    """Clear all in-progress locks"""
    if not os.path.exists(IN_PROGRESS_FILE):
        print(f"✅ {IN_PROGRESS_FILE} doesn't exist. Nothing to clean up.")
        return
    
    # Read current state
    try:
        with open(IN_PROGRESS_FILE, 'r') as f:
            in_progress = json.load(f)
        
        if not in_progress:
            print(f"✅ {IN_PROGRESS_FILE} is already empty. Nothing to clean up.")
            return
        
        print(f"⚠️  Found {len(in_progress)} locked videos:")
        for i, video in enumerate(in_progress, 1):
            print(f"   {i}. {video}")
        
        # Clear the file
        with open(IN_PROGRESS_FILE, 'w') as f:
            json.dump([], f, indent=2)
        
        print(f"\n✅ Cleared {len(in_progress)} stale locks!")
        print(f"All videos are now available for processing.")
        
    except json.JSONDecodeError:
        print(f"❌ Error: {IN_PROGRESS_FILE} is corrupted. Resetting to empty array.")
        with open(IN_PROGRESS_FILE, 'w') as f:
            json.dump([], f, indent=2)
        print(f"✅ {IN_PROGRESS_FILE} reset successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🧹 Cleanup Stale Locks")
    print("="*60)
    cleanup_locks()
    print("="*60)

