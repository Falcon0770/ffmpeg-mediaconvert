#!/usr/bin/env python3
"""
Test script to verify parallel processing file locking works correctly
Run this multiple times simultaneously to test the locking mechanism
"""

import json
import time
import sys
import os

# Import the functions from convert_ffmpeg
sys.path.insert(0, os.path.dirname(__file__))

try:
    from convert_ffmpeg import (
        acquire_next_video,
        mark_video_complete,
        mark_video_failed,
        load_processed_videos,
        load_in_progress_videos,
        save_processed_videos,
        save_in_progress_videos,
        LOCK_AVAILABLE
    )
except ImportError as e:
    print(f"❌ Error importing from convert_ffmpeg.py: {e}")
    sys.exit(1)

def test_parallel_processing():
    """
    Simulates parallel video processing
    """
    # Create test video list
    test_videos = [
        f"test_video_{i}.mp4" for i in range(1, 21)  # 20 test videos
    ]
    
    print("="*60)
    print("🧪 Testing Parallel Processing File Locking")
    print("="*60)
    print(f"Lock available: {LOCK_AVAILABLE}")
    print(f"Test videos: {len(test_videos)}")
    print(f"Worker ID: Process-{os.getpid()}")
    print("="*60)
    
    worker_success = 0
    worker_failed = 0
    
    while True:
        # Try to acquire next video
        video, should_continue = acquire_next_video(test_videos)
        
        if not should_continue or video is None:
            print("\n✅ No more videos to process")
            break
        
        print(f"\n🎬 Acquired: {video}")
        
        # Simulate processing (2-5 seconds)
        import random
        processing_time = random.uniform(2, 5)
        print(f"   Processing for {processing_time:.1f}s...")
        time.sleep(processing_time)
        
        # Randomly simulate success/failure (90% success rate)
        success = random.random() > 0.1
        
        if success:
            mark_video_complete(video)
            worker_success += 1
            print(f"   ✅ SUCCESS")
        else:
            mark_video_failed(video)
            worker_failed += 1
            print(f"   ❌ FAILED (will retry)")
        
        # Show progress
        processed = load_processed_videos()
        in_progress = load_in_progress_videos()
        remaining = [v for v in test_videos if v not in processed and v not in in_progress]
        
        print(f"\n📊 Progress:")
        print(f"   ✅ Completed: {len(processed)}/{len(test_videos)}")
        print(f"   🔄 In Progress: {len(in_progress)}")
        print(f"   ⏳ Remaining: {len(remaining)}")
        print(f"   This worker: ✅ {worker_success} | ❌ {worker_failed}")
    
    print("\n" + "="*60)
    print("🏁 Worker Finished!")
    print("="*60)
    print(f"This worker processed:")
    print(f"   ✅ Successful: {worker_success}")
    print(f"   ❌ Failed: {worker_failed}")
    print(f"   📋 Total: {worker_success + worker_failed}")
    print("="*60)

def reset_test_files():
    """Reset test files to start fresh"""
    if os.path.exists('processed_videos.json'):
        os.remove('processed_videos.json')
    if os.path.exists('in_progress_videos.json'):
        os.remove('in_progress_videos.json')
    
    # Create empty files
    save_processed_videos(set())
    save_in_progress_videos(set())
    print("✅ Test files reset")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test parallel processing file locking")
    parser.add_argument("--reset", action="store_true", help="Reset test files before running")
    args = parser.parse_args()
    
    if args.reset:
        reset_test_files()
    
    try:
        test_parallel_processing()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)

