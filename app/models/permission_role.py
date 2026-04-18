from datetime import datetime
import uuid
from sqlalchemy import DateTime, UUID, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PermissionRole(Base):
    __tablename__ = "PERMISSION_ROLE"

    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("ROLE.id"),primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("PERMISSION.id"),primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
