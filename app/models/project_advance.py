from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import uuid
from typing import Optional

if TYPE_CHECKING:
    from app.models.project import Project

class ProjectAdvance(Base):
    __tablename__ = "PROJECT_ADVANCE"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("PROJECT.id"), primary_key=True)
    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(500), nullable = False)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="advances")
