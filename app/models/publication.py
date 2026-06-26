from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
import uuid
from sqlalchemy import UUID, DateTime, Enum as SAEnum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, func

from app.core.database import Base
from app.core.enums import PublicationStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.token import Token
    from app.models.trade import Trade


class Publication(Base):
    __tablename__ = "PUBLICATION"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    token_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("TOKEN.id"), nullable=False
    )
    seller_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("USER.id"), nullable=False
    )
    status: Mapped[PublicationStatus] = mapped_column(
        SAEnum(PublicationStatus, name="publication_status"),
        nullable=False,
        default=PublicationStatus.active,
    )
    total: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    available: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    price_per_token: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    listing_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token: Mapped["Token"] = relationship("Token", back_populates="publications")
    seller: Mapped["User"] = relationship("User", back_populates="publications")
    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="publication")