# utils.py
import os
from dotenv import load_dotenv
import boto3

load_dotenv()

AWS_REGION    = os.getenv("AWS_REGION")
BUCKET        = os.getenv("S3_BUCKET_ORIGINALS")
COLLECTION_ID = os.getenv("REKOG_COLLECTION")
CDN_DOMAIN    = os.getenv("CDN_DOMAIN")

# S3 client for presigned URLs
s3  = boto3.client("s3", region_name=AWS_REGION)
# Rekognition client for face searches
rek = boto3.client("rekognition", region_name=AWS_REGION)


def get_s3_url(key: str) -> str:
    """
    Return the public CloudFront URL for the given S3 key.
    """
    return f"https://{CDN_DOMAIN}/{key}"

def search_event_faces(
    image_bytes: bytes,
    event_id: str,
    threshold: int = 90,
    max_faces: int = 100
) -> list[str]:
    """
    Search your collection with the guest selfie, then reconstruct
    the real S3 keys for any matches in this event.
    """
    san_event = event_id.replace(" ", "_")
    resp = rek.search_faces_by_image(
        CollectionId=COLLECTION_ID,
        Image={"Bytes": image_bytes},
        FaceMatchThreshold=threshold,
        MaxFaces=max_faces,
    )

    prefix = f"{san_event}:"
    results = []
    for m in resp.get("FaceMatches", []):
        ext_id = m["Face"]["ExternalImageId"]
        if not ext_id.startswith(prefix):
            continue
        filename = ext_id.split(":", 1)[1]
        real_key = f"{event_id}/{filename}"
        results.append(real_key)

    # dedupe
    return list(dict.fromkeys(results))
