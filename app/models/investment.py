from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Numeric, DateTime, ForeignKey, UUID, Boolean, Enum as SAEnum, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.enums import InvestmentSource

import uuid

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.token import Token


class Investment(Base):
    __tablename__ = "INVESTMENT"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("USER.id"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("PROJECT.id"), nullable=False
    )
    token_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("TOKEN.id"), nullable=False
    )
    token_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    source: Mapped[InvestmentSource] = mapped_column(
        SAEnum(InvestmentSource, name="investment_source"),
        nullable=False,
        default=InvestmentSource.offering,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tx_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="investments")
    project: Mapped["Project"] = relationship("Project", back_populates="investments")
    token: Mapped["Token"] = relationship("Token", back_populates="investments")

    @property
    def total_amount(self) -> Decimal:
        return self.token_quantity * self.unit_price