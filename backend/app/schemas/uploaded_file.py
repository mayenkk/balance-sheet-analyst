from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.auth import UserResponse


class UploadedFileBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    is_processed: bool
    processing_status: str
    error_message: Optional[str] = None


class UploadedFileCreate(UploadedFileBase):
    user_id: int
    file_path: str


class UploadedFileResponse(UploadedFileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class UploadedFileList(BaseModel):
    files: list[UploadedFileResponse]
    total: int 