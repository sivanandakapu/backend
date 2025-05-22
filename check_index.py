import os, boto3
from dotenv import load_dotenv

load_dotenv()
AWS_REGION = os.getenv("AWS_REGION")
BUCKET     = os.getenv("S3_BUCKET_ORIGINALS")
COLL       = os.getenv("REKOG_COLLECTION")
PREFIX     = "graduation 2/"
SAN_EVENT  = PREFIX.rstrip("/").replace(" ", "_")  # "graduation_2"

s3  = boto3.client("s3", region_name=AWS_REGION)
rek = boto3.client("rekognition", region_name=AWS_REGION)

# count S3 images
s3_count = sum(
    1
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=PREFIX)
    for obj in page.get("Contents", [])
    if obj["Key"].lower().endswith((".jpg", ".jpeg", ".png"))
)

# count Rekognition faces indexed
rek_count = sum(
    1
    for page in rek.get_paginator("list_faces").paginate(CollectionId=COLL)
    for face in page.get("Faces", [])
    if face["ExternalImageId"].startswith(f"{SAN_EVENT}:")
)

print(f"S3 images : {s3_count}")
print(f"Indexed    : {rek_count}")
if s3_count == rek_count:
    print("✅ All images indexed!")
else:
    print(f"⚠️ Missing {s3_count - rek_count} indexed entries.")
