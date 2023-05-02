from video import Video, VideoStatus
from pathlib import Path

def test_video():
    video_config = {
        "url": 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    }

    video = Video(**video_config)

    assert video.url == video_config.get("url")
    assert video.status == VideoStatus.SUCCESS
    assert video.meta.title == "Rick Astley - Never Gonna Give You Up (Official Music Video)"
    assert video.meta.id == "dQw4w9WgXcQ"
    assert Path(video.filename).exists
    