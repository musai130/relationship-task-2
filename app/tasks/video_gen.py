from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends
from task_queue import broker
from models import db_helper, Video, VideoStatus
from pathlib import Path
from moviepy import ImageClip, concatenate_videoclips
import uuid

MEDIA_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
VIDEOS_DIR = MEDIA_DIR / "videos"
IMAGES_DIR = MEDIA_DIR / "images"


@broker.task
async def generate_video(
    video_id: int,
    session: Annotated[
        AsyncSession,
        TaskiqDepends(db_helper.session_getter),
    ],
) -> None:
    video = await session.get(Video, video_id)
    if not video:
        return

    try:
        VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

        clips = []
        for image_path in video.image_paths:
            full_image_path = MEDIA_DIR / image_path
            if not full_image_path.exists():
                raise FileNotFoundError(f"Изображение не найдено: {full_image_path}")

            clip = ImageClip(str(full_image_path), duration=2)
            clips.append(clip)

        if not clips:
            raise ValueError("Нет изображений для создания видео")

        final_clip = concatenate_videoclips(clips, method="compose")

        video_filename = f"{uuid.uuid4()}.mp4"
        video_file_path = VIDEOS_DIR / video_filename
        relative_video_path = f"videos/{video_filename}"

        final_clip.write_videofile(
            str(video_file_path),
            fps=24,
            codec="libx264",
            audio=False,
        )

        final_clip.close()
        for clip in clips:
            clip.close()

        video.video_path = relative_video_path
        video.status = VideoStatus.success
        video.error_message = None

    except Exception as e:
        video.status = VideoStatus.error
        video.error_message = str(e)

    await session.commit()

