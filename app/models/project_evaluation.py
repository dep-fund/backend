from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlalchemy import DateTime, ForeignKey, Text, Enum as SAEnum, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base 

from app.core.enums import ProjectState

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import AdminUser

class ProjectEvaluation(Base):
    __tablename__ = "EVALUATED_BY"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("PROJECT.id"), nullable=False)
    admin_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ADMIN_USER.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    state: Mapped[ProjectState] = mapped_column(SAEnum(ProjectState, name="project_state"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    project: Mapped["Project"] = relationship("Project", back_populates="evaluations")
    admin: Mapped["AdminUser"] = relationship("AdminUser", back_populates="evaluations")
