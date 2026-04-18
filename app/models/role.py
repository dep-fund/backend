from datetime import datetime
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import DateTime, UUID, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models.user import User


class Role(Base):
    __tablename__ = "ROLE"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String(100), unique=True)
    permissions = relationship(
        "Permission",
        secondary="PERMISSION_ROLE",
        back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role"
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )