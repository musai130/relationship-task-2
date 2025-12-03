from typing import List, Optional
from pydantic import BaseModel, computed_field
from config import settings


class VideoUploadResponse(BaseModel):
    id: int
    status: str
    image_paths: List[str]

    @computed_field
    @property
    def image_urls(self) -> List[str]:
        return [f"{settings.run.app_url}/static/uploads/{path}" for path in self.image_paths]

    class Config:
        from_attributes = True


class VideoRead(BaseModel):
    id: int
    status: str
    image_paths: List[str]
    video_path: Optional[str] = None
    error_message: Optional[str] = None

    @computed_field
    @property
    def image_urls(self) -> List[str]:
        return [f"{settings.run.app_url}/static/uploads/{path}" for path in self.image_paths]

    @computed_field
    @property
    def video_url(self) -> Optional[str]:
        if self.video_path:
            return f"{settings.run.app_url}/static/uploads/{self.video_path}"
        return None

    class Config:
        from_attributes = True

