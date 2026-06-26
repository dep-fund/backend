from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
import uuid
from sqlalchemy import UUID, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import TradeStatus

if TYPE_CHECKING:
    from app.models.publication import Publication
    from app.models.user import User


class Trade(Base):
    __tablename__ = "TRADE"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("PUBLICATION.id"), nullable=False
    )
    buyer_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("USER.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    status: Mapped[TradeStatus] = mapped_column(
        SAEnum(TradeStatus, name="trade_status"),
        nullable=False,
        default=TradeStatus.pending,
    )
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    publication: Mapped["Publication"] = relationship(
        "Publication", back_populates="trades"
    )
    buyer: Mapped["User"] = relationship("User", back_populates="trades")