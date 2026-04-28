from datetime import datetime
import uuid
from sqlalchemy import DateTime, UUID, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.permission_role import PermissionRole


class Permission(Base):
    __tablename__ = "PERMISSION"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(100), unique=True)
    roles = relationship(
        "Role",
        secondary=PermissionRole.__table__,
        back_populates="permissions"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )