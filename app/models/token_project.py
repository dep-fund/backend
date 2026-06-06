from typing import TYPE_CHECKING
import uuid
from decimal import Decimal
from sqlalchemy import UUID, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.token import Token
    from app.models.project import Project


class TokenProject(Base):
    __tablename__ = "TOKEN_PROJECT"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    token_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("TOKEN.id"), nullable=False
    )
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("PROJECT.id"), nullable=False, unique=True
    )
    total_supply: Mapped[Decimal] = mapped_column(Numeric(20, 0), nullable=False)
    available_supply: Mapped[Decimal] = mapped_column(Numeric(20, 0), nullable=False)

    token: Mapped["Token"] = relationship("Token", back_populates="token_projects")
    project: Mapped["Project"] = relationship("Project", back_populates="token_project")
