from typing import Annotated, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from config import settings
from models import VideoStatus, db_helper, Video
from video_schema import VideoUploadResponse, VideoRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import uuid

router = APIRouter(
    tags=["Videos"],
    prefix=settings.url.videos,
)

MEDIA_DIR = Path(__file__).resolve().parents[1] / "static" / "uploads"
IMAGES_DIR = MEDIA_DIR / "images"


@router.post(
    "/upload",
    response_model=VideoUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_images(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    files: List[UploadFile] = File(...),
) -> VideoUploadResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо загрузить хотя бы одно изображение",
        )

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Файл должен быть изображением. Получен тип: {file.content_type}",
            )

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    image_paths = []
    for file in files:
        original_extension = Path(file.filename or "image.jpg").suffix
        unique_filename = f"{uuid.uuid4()}{original_extension}"
        file_path = IMAGES_DIR / unique_filename
        relative_path = f"images/{unique_filename}"

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        image_paths.append(relative_path)

    video = Video(
        status=VideoStatus.pending,
        image_paths=image_paths,
        video_path=None,
        error_message=None,
    )
    session.add(video)
    await session.commit()
    await session.refresh(video)

    from tasks.video_gen import generate_video
    await generate_video.kiq(video_id=video.id)

    return VideoUploadResponse(
        id=video.id,
        status=video.status.value,
        image_paths=video.image_paths,
    )


@router.get("", response_model=List[VideoRead])
async def get_all_videos(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> List[VideoRead]:
    result = await session.execute(select(Video).order_by(Video.id))
    videos = result.scalars().all()
    return [VideoRead.model_validate(video) for video in videos]


@router.get("/{video_id}", response_model=VideoRead)
async def get_video(
    video_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> VideoRead:
    video = await session.get(Video, video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Видео с id {video_id} не найдено",
        )
    return VideoRead.model_validate(video)

