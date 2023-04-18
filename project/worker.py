import os
import time
import uuid
import json

from celery import Celery
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from redis import Redis
from minio import Minio


db = Redis(
    host=os.environ.get(
        "REDDIS_URL", 'localhost'), 
    port=os.environ.get(
        "REDDIS_PORT", 6379), 
    db=0)


storage = Minio(
    endpoint=os.environ.get(
        "MINIO_URL", 'localhost:9000'),
    access_key=os.environ.get(
        "MINIO_ACCESS_KEY", "K5Uj7tTYNX2zdyPU"),
    secret_key=os.environ.get(
        "MINIO_SECRET_KEY", "BBFufL13fafNSWL9L6oNugkWghNUQzSs"),
    secure=False
)
video_bucket = os.environ.get(
    "MINIO_BUCKET_VIDEO", "video")


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"]
)


@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


class AutoClipVideo(BaseModel):
    source: str
    uri: str | None = ""
    meta: str | None = None
    id: str | None = str(uuid.uuid4())


@celery.task(name="download_url")
def download_url(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(id)s.%(ext)s',
        'remux_video': True,
        'nooverwrites': True,
        'quiet': True,
        'forcefilename': True,
        'writethumbnail': True,
        'writeinfojson': True,  # enable metadata download
        'writesubtitles': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info_dict)
        video_id = info_dict.get("id", None)

    print(f"Done downloading video from: {url} to {filepath}")

    # Upload the video to MinIO
    bucket_name = video_bucket
    object_name = video_id
    file_path = filepath
    storage_url = None
    try:
        with open(file_path, "rb") as file_data:
            storage.put_object(bucket_name, object_name,
                               file_data, os.stat(file_path).st_size)
        storage_url = storage.presigned_get_object(bucket_name, object_name)
        print(f"Video uploaded successfully!\n{storage_url}")
    except Exception as err:
        print(err)
        

    # Upload the meta to MinIO
    bucket_name = video_bucket
    object_name = video_id
    file_path = f"{video_id}.info.json"
    meta_url = None
    try:
        with open(file_path, "rb") as file_data:
            storage.put_object(bucket_name, object_name,
                               file_data, os.stat(file_path).st_size)
        meta_url = storage.presigned_get_object(bucket_name, object_name)
        print(f"Metadata uploaded successfully!\n{meta_url}")
    except Exception as err:
        print(err)

    video = AutoClipVideo(
        source=url,
        uri=storage_url,
        meta=meta_url)

    try:
        db.hmset(video.id, video.dict())
        print(f"Saved to DB successfully!\n{video.dict()}")
    except Exception as err:
        print(err)

    return video.id
