import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION    = os.getenv("AWS_REGION")
BUCKET        = os.getenv("S3_BUCKET_ORIGINALS")   # photos--db
COLLECTION_ID = os.getenv("REKOG_COLLECTION")      # event-spotter-collection
PREFIX        = "graduation 2/"                    # your S3 folder
SAN_EVENT     = PREFIX.rstrip("/").replace(" ", "_")  # "graduation_2"

s3  = boto3.client("s3", region_name=AWS_REGION)
rek = boto3.client("rekognition", region_name=AWS_REGION)

count = 0
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        name = os.path.basename(key)
        # only index jpg/png, skip system files
        if not name.lower().endswith((".jpg", ".jpeg", ".png")) or name.startswith("."):
            continue

        ext_id = f"{SAN_EVENT}:{name}"
        print(f"Indexing {key!r} as {ext_id!r} …", end=" ")
        rek.index_faces(
            CollectionId=COLLECTION_ID,
            Image={"S3Object": {"Bucket": BUCKET, "Name": key}},
            ExternalImageId=ext_id,
            DetectionAttributes=["DEFAULT"]
        )
        print("✓")
        count += 1

print(f"\n✅ Indexed {count} images from '{PREFIX}'.")
