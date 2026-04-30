from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid

if TYPE_CHECKING:
    from app.models.project import Project

class ProjectDocument(Base):
    __tablename__ = "PROJECT_DOCUMENT"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("PROJECT.id"), primary_key=True)
    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="documents")
