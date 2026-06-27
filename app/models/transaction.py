from typing import TYPE_CHECKING, Optional
import uuid
from sqlalchemy import UUID, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import TransactionType

from datetime import datetime
from sqlalchemy import DateTime, func


if TYPE_CHECKING:
    from app.models.wallet import Wallet
    from app.models.project import Project


class Transaction(Base):
    __tablename__ = "TRANSACTION"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tx_hash: Mapped[str] = mapped_column(String(66), unique=True, nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name="transaction_type"), nullable=False
    )
    wallet_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("WALLET.id"), nullable=False
    )
    project_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("PROJECT.id"), nullable=True
    )

    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")
    project: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="transactions"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
