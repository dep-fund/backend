from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Numeric, String, DateTime, ForeignKey, Text, Enum as SAEnum, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base 
import uuid

from app.core.enums import ProjectState
from app.models.category_project import CategoryProject

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category

from app.models.project_document import ProjectDocument
from app.models.project_advance import ProjectAdvance
class Project(Base):
    __tablename__ = "PROJECT"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    state: Mapped[ProjectState] = mapped_column(
        SAEnum(ProjectState, name="project_state"), nullable=False, default=ProjectState.PENDING
    )
    ubication: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("USER.id"),
        nullable=False
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="projects"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary=CategoryProject.__table__,
        back_populates="projects"
    )
    documents: Mapped[list["ProjectDocument"]] = relationship(
        "ProjectDocument",
        back_populates="project")
    advances: Mapped[list["ProjectAdvance"]] = relationship(
        "ProjectAdvance",
        back_populates="project"
    )