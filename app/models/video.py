import enum
from typing import Optional, List
from sqlalchemy import String, Text, Enum as SQLAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VideoStatus(enum.Enum):
    pending = "pending"
    success = "success"
    error = "error"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)

    status: Mapped[VideoStatus] = mapped_column(
        SQLAEnum(VideoStatus, name="video_status", create_constraint=True),
        nullable=False,
        index=True,
        default=VideoStatus.pending,
    )

    image_paths: Mapped[List[str]] = mapped_column(JSON, nullable=False)

    video_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"Video(id={self.id}, status={self.status.value}, video_path={self.video_path})"

