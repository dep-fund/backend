import asyncio
from dataclasses import dataclass
from datetime import date
from uuid import UUID

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.enums import FileFolder
from app.exceptions.file import FileExceedsLimit, FileTypeNotAllowed


@dataclass(frozen=True)
class UploadResult:
    url: str
    public_id: str


class FileService:
    IMAGES = frozenset({"image/jpeg", "image/png", "image/webp"})
    DOCUMENTS = frozenset({"application/pdf"})

    def _build_folder(self, folder: FileFolder, entity_id: UUID | None) -> str:
        parts = [folder.value]
        if entity_id:
            parts.append(str(entity_id))
        parts.append(str(date.today()))
        return "/".join(parts)

    def _validate_type(
        self, content_type: str | None, allowed: frozenset[str] | None
    ) -> None:
        if allowed and content_type not in allowed:
            raise FileTypeNotAllowed()

    def _validate_size(self, contents: bytes, max_mb: int) -> None:
        if len(contents) > max_mb * 1024 * 1024:
            raise FileExceedsLimit()

    async def upload(
        self,
        file: UploadFile,
        *,
        folder: FileFolder,
        entity_id: UUID | None = None,
        allowed_types: frozenset[str] | None = None,
        resource_type: str = "auto",
        max_size_mb: int = 12,
    ) -> UploadResult:
        self._validate_type(file.content_type, allowed_types)
        contents = await file.read()
        self._validate_size(contents, max_size_mb)

        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            contents,
            folder=self._build_folder(folder, entity_id),
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
        )

        return UploadResult(url=result["secure_url"], public_id=result["public_id"])

    async def delete(self, public_id: str, *, resource_type: str = "image") -> None:
        await asyncio.to_thread(
            cloudinary.uploader.destroy,
            public_id,
            resource_type=resource_type,
        )
