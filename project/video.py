import logging
import os
import uuid
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from yt_dlp import YoutubeDL

download_path = os.environ.get("VIDEO_DOWNLOAD_PATH", "./data")
logging_path = os.environ.get("VIDEO_LOGGING_PATH", "./logs")

logging_file_path = f'{logging_path}/video_downloader.log'
os.makedirs(os.path.dirname(logging_file_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename=logging_file_path,
    filemode='a'
)


class VideoMetadata(BaseModel):
    filename: str | None = ""
    id: str
    title: Optional[str]
    description: Optional[str]
    uploader: Optional[str]
    tags: Optional[list[str]]
    duration: Optional[float]
    duration_string: Optional[str]
    format: Optional[str]
    ext: Optional[str]
    width: Optional[int]
    height: Optional[int]
    resolution: Optional[str]


class VideoStatus(Enum):
    FAILURE = 0
    PENDING = 1
    RECEIVED = 2
    RETRY = 3
    REVOKED = 4
    STARTED = 5
    SUCCESS = 6


class Video(BaseModel):
    id: str | None = str(uuid.uuid4())
    url: str
    status: VideoStatus | None = VideoStatus.PENDING
    filename: Optional[str]
    meta: Optional[VideoMetadata]

    def __init__(self, url: str):
        super().__init__(url=url)
        self.status = VideoStatus.RECEIVED
        try:
            ydl_opts = {
                'outtmpl': f'{download_path}/%(id)s.%(ext)s',
                'nooverwrites': True,
                'quiet': True,
                'writeinfojson': True,  # enable metadata download
            }
            info_dict = {}
            with YoutubeDL(ydl_opts) as ydl:
                logging.info(f"Started downloading video from: {self.url}")
                self.status = VideoStatus.STARTED
                info_dict = ydl.extract_info(self.url, download=True)
                self.filename = ydl.prepare_filename(info_dict)
                video_id = info_dict.get("id", None)
                meta_file_path = f"{download_path}/{video_id}.info.json"
            self.status = VideoStatus.SUCCESS
            logging.info(f"Finished downloading video from: {self.url} to {self.filename}")
            self.meta = VideoMetadata(**info_dict)
            self.meta.filename = meta_file_path
            logging.info(f"Finished downloading metadata from: {self.url} to {meta_file_path}")
        except Exception as err:
            self.status = VideoStatus.FAILURE
            logging.error(f"Error downloading video from {self.url}: {err}")
            raise err
