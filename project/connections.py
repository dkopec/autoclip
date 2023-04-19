from datetime import timedelta
import os
import json
from pathlib import Path

from redis import Redis
from minio import Minio

reddis_port = os.environ.get("REDDIS_PORT", 6379)

db = Redis.from_url(
    url=os.environ.get(
        "REDDIS_URL", f'rediss://localhost:{reddis_port}/0'),
    db=0
)

db_id = __name__

def db_get(id):
    db_key = f"{db_id}-{id}"
    raw_db_string = db.get(db_key)
    result = json.loads(raw_db_string)
    return result


def db_set(id, value):
    db_key = f"{db_id}-{id}"
    db_value = json.dumps(value)
    db.set(db_key, db_value)


bucket = os.environ.get(
    "MINIO_BUCKET_VIDEO", "video")

storage = Minio(
    endpoint=os.environ.get(
        "MINIO_URL", 'localhost:9000'),
    access_key=os.environ.get(
        "MINIO_ACCESS_KEY", "K5Uj7tTYNX2zdyPU"),
    secret_key=os.environ.get(
        "MINIO_SECRET_KEY", "BBFufL13fafNSWL9L6oNugkWghNUQzSs"),
    secure=False
)

def storage_set(file_path):
    meta_object_name = Path(file_path).name
    with open(file_path, "rb") as file_data:
        storage.put_object(bucket, meta_object_name,
                           file_data, os.stat(file_path).st_size)
    return {"filename":meta_object_name, "bucket": bucket}

def storage_get_url(file_name):
    file_url= storage.presigned_get_object(bucket, file_name)
    return file_url