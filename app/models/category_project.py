from datetime import datetime
import uuid
from sqlalchemy import DateTime, UUID, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CategoryProject(Base):
    __tablename__ = "CATEGORY_PROJECT"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("PROJECT.id"),primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("CATEGORY.id"),primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
