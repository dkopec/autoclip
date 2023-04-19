import os
import time
import uuid

from celery import Celery
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from connections import storage_set, db_set


download_path = os.environ.get("YTDL_DOWNLOAD_PATH", "/data")

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
    info: dict | None = {}
    uri: str | None = ""
    meta: str | None = None
    id: str | None = str(uuid.uuid4())


@celery.task(name="download_url", max_retries=3, retry_backoff=True)
def download_url(url):
    try:
        ydl_opts = {
            'outtmpl': f'{download_path}/%(id)s.%(ext)s',
            'nooverwrites': True,
            'quiet': True,
            'writeinfojson': True,  # enable metadata download
        }
        info_dict = {}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info_dict)
            video_id = info_dict.get("id", None)
        print(f"Done downloading video from: {url} to {filepath}")

        # Upload the video to MinIO
        video_file_path = filepath
        video_storage_object = storage_set(video_file_path)
        print(f"Video uploaded successfully!")
        

        # Upload the meta to MinIO        
        meta_file_path = f"{download_path}/{video_id}.info.json"
        meta_storage_object = storage_set(meta_file_path)
        print(f"Metadata uploaded successfully!")


        video = {
            "id": video_id,
            "source": url,
            "storage_bucket": video_storage_object["bucket"],
            "video_filename": video_storage_object["filename"],
            "meta_filename": meta_storage_object["filename"],
            "title": info_dict["title"],
            "description": info_dict["description"],
            "uploader": info_dict["uploader"],
            "tags": info_dict["tags"],
            "duration": info_dict["duration"],
            "duration_string": info_dict["duration_string"],
            "format": info_dict["format"],
            "ext": info_dict["ext"],
            "width": info_dict["width"],
            "height": info_dict["height"],
            "resolution": info_dict["resolution"],
        }

        db_set(video["id"], video)
        print(f"Saved to DB successfully!")
    except Exception as err:
        print(err)
        download_url.retry(exc=err)

    return video["id"]
