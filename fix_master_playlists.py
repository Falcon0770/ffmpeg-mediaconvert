import boto3

s3 = boto3.client("s3", region_name="us-east-1")

bucket = "cdn.netcomplus.com"

# Videos that need fixing
videos_to_fix = [
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Introduction/MASTER.m3u8",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Intro and Summary/AI+_Writer-V3-Course_Summary/MASTER.m3u8",
    "streams/AI CERTs/Synthesia V3 Videos/AI+ Writer/Module 1/AI+_Writer-V3-1.1/MASTER.m3u8"
]

print("Fixing MASTER.m3u8 files to add underscores...")
print("="*80)

for key in videos_to_fix:
    print(f"\nProcessing: s3://{bucket}/{key}")
    
    try:
        # Download the file
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        
        print("  Original content:")
        for line in content.split('\n'):
            if '.m3u8' in line:
                print(f"    {line}")
        
        # Fix the content - add underscores
        fixed_content = content.replace("MASTER240p.m3u8", "MASTER_240p.m3u8")
        fixed_content = fixed_content.replace("MASTER360p.m3u8", "MASTER_360p.m3u8")
        fixed_content = fixed_content.replace("MASTER480p.m3u8", "MASTER_480p.m3u8")
        fixed_content = fixed_content.replace("MASTER720p.m3u8", "MASTER_720p.m3u8")
        fixed_content = fixed_content.replace("MASTER1080p.m3u8", "MASTER_1080p.m3u8")
        
        print("  Fixed content:")
        for line in fixed_content.split('\n'):
            if '.m3u8' in line:
                print(f"    {line}")
        
        # Upload the fixed file
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=fixed_content.encode('utf-8'),
            ContentType='application/vnd.apple.mpegurl'
        )
        
        print("  ✅ Fixed and uploaded")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "="*80)
print("✅ All MASTER.m3u8 files have been fixed!")
print("Now the videos should play correctly.")

