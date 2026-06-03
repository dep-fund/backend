from typing import TYPE_CHECKING
import uuid
from sqlalchemy import UUID, DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import StandardUser
    from app.models.transaction import Transaction


class Wallet(Base):
    __tablename__ = "WALLET"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    address: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("STANDARD_USER.id"), nullable=False
    )

    user: Mapped["StandardUser"] = relationship(
        "StandardUser", back_populates="wallets"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="wallet", cascade="all, delete-orphan"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
