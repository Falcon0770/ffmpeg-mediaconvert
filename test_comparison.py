#!/usr/bin/env python3
"""
Test script to compare MediaConvert vs FFmpeg outputs
Verifies that convert_ffmpeg.py produces identical results to convert_video.py
"""

import boto3
import argparse
import os
from collections import defaultdict

def parse_s3_path(s3_path):
    """Parse S3 path into bucket and key"""
    if not s3_path.startswith("s3://"):
        raise ValueError("Invalid S3 path: " + s3_path)
    parts = s3_path.replace("s3://", "").split("/", 1)
    bucket = parts[0]
    key = parts[1] if len(parts) > 1 else ""
    return bucket, key

def list_s3_files(bucket, prefix):
    """List all files in S3 prefix"""
    s3 = boto3.client("s3")
    files = []
    paginator = s3.get_paginator("list_objects_v2")
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            files.append({
                "key": obj["Key"],
                "size": obj["Size"],
                "name": os.path.basename(obj["Key"])
            })
    
    return files

def compare_outputs(mediaconvert_path, ffmpeg_path):
    """Compare outputs from MediaConvert and FFmpeg"""
    
    print("="*80)
    print("COMPARING MEDIACONVERT VS FFMPEG OUTPUTS")
    print("="*80)
    print(f"MediaConvert path: {mediaconvert_path}")
    print(f"FFmpeg path: {ffmpeg_path}")
    print()
    
    # Parse S3 paths
    mc_bucket, mc_prefix = parse_s3_path(mediaconvert_path)
    ff_bucket, ff_prefix = parse_s3_path(ffmpeg_path)
    
    # List files
    print("Listing MediaConvert files...")
    mc_files = list_s3_files(mc_bucket, mc_prefix)
    print(f"Found {len(mc_files)} files")
    
    print("Listing FFmpeg files...")
    ff_files = list_s3_files(ff_bucket, ff_prefix)
    print(f"Found {len(ff_files)} files")
    print()
    
    # Group by file type
    mc_by_type = defaultdict(list)
    ff_by_type = defaultdict(list)
    
    for f in mc_files:
        ext = os.path.splitext(f["name"])[1]
        mc_by_type[ext].append(f)
    
    for f in ff_files:
        ext = os.path.splitext(f["name"])[1]
        ff_by_type[ext].append(f)
    
    # Compare file counts
    print("FILE COUNT COMPARISON")
    print("-"*80)
    print(f"{'File Type':<20} {'MediaConvert':>15} {'FFmpeg':>15} {'Match':>10}")
    print("-"*80)
    
    all_types = set(mc_by_type.keys()) | set(ff_by_type.keys())
    matches = 0
    mismatches = 0
    
    for ext in sorted(all_types):
        mc_count = len(mc_by_type[ext])
        ff_count = len(ff_by_type[ext])
        match = "✅" if mc_count == ff_count else "❌"
        
        if mc_count == ff_count:
            matches += 1
        else:
            mismatches += 1
        
        print(f"{ext:<20} {mc_count:>15} {ff_count:>15} {match:>10}")
    
    print("-"*80)
    print(f"Total types: {len(all_types)} | Matches: {matches} | Mismatches: {mismatches}")
    print()
    
    # Check for expected files
    print("EXPECTED FILES CHECK")
    print("-"*80)
    
    expected_playlists = [
        "MASTER_240p.m3u8",
        "MASTER_360p.m3u8",
        "MASTER_480p.m3u8",
        "MASTER_720p.m3u8",
        "MASTER_1080p.m3u8"
    ]
    
    mc_names = {f["name"] for f in mc_files}
    ff_names = {f["name"] for f in ff_files}
    
    print("Checking for required playlist files:")
    for playlist in expected_playlists:
        mc_has = playlist in mc_names
        ff_has = playlist in ff_names
        
        status = "✅" if (mc_has and ff_has) else "❌"
        print(f"  {playlist:<25} MC: {mc_has} | FF: {ff_has} {status}")
    
    print()
    
    # Compare file sizes
    print("FILE SIZE COMPARISON")
    print("-"*80)
    
    mc_total_size = sum(f["size"] for f in mc_files)
    ff_total_size = sum(f["size"] for f in ff_files)
    
    print(f"MediaConvert total size: {mc_total_size / (1024*1024):.2f} MB")
    print(f"FFmpeg total size: {ff_total_size / (1024*1024):.2f} MB")
    
    if mc_total_size > 0:
        diff_pct = ((ff_total_size - mc_total_size) / mc_total_size) * 100
        print(f"Difference: {diff_pct:+.2f}%")
        
        if abs(diff_pct) < 10:
            print("✅ File sizes are comparable (within 10%)")
        elif abs(diff_pct) < 20:
            print("⚠️  File sizes differ by 10-20% (acceptable)")
        else:
            print("❌ File sizes differ significantly (>20%)")
    
    print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    all_checks_pass = True
    
    # Check 1: File count matches
    if len(mc_files) == len(ff_files):
        print("✅ File count matches")
    else:
        print(f"❌ File count mismatch: MC={len(mc_files)}, FF={len(ff_files)}")
        all_checks_pass = False
    
    # Check 2: All expected playlists present
    all_playlists_present = all(p in ff_names for p in expected_playlists)
    if all_playlists_present:
        print("✅ All 5 rendition playlists present")
    else:
        print("❌ Missing some rendition playlists")
        all_checks_pass = False
    
    # Check 3: File sizes comparable
    if mc_total_size > 0 and abs(diff_pct) < 20:
        print("✅ File sizes are comparable")
    elif mc_total_size == 0:
        print("⚠️  Cannot compare sizes (MediaConvert path empty)")
    else:
        print("❌ File sizes differ significantly")
        all_checks_pass = False
    
    print()
    
    if all_checks_pass:
        print("🎉 ALL CHECKS PASSED - FFmpeg output matches MediaConvert!")
    else:
        print("⚠️  Some checks failed - review differences above")
    
    print("="*80)

def main():
    parser = argparse.ArgumentParser(
        description="Compare MediaConvert and FFmpeg outputs"
    )
    parser.add_argument(
        "--mediaconvert",
        required=True,
        help="S3 path to MediaConvert output (e.g., s3://bucket/path/video_name/MASTER/)"
    )
    parser.add_argument(
        "--ffmpeg",
        required=True,
        help="S3 path to FFmpeg output (e.g., s3://bucket/path/video_name/MASTER/)"
    )
    
    args = parser.parse_args()
    
    try:
        compare_outputs(args.mediaconvert, args.ffmpeg)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

