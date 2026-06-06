from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Numeric, String, DateTime, ForeignKey, Text, Enum as SAEnum, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base

from app.core.enums import RiskLevel

import uuid

from app.core.enums import ProjectState
from app.models.category_project import CategoryProject
from app.models.project_image import ProjectImage

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.project_evaluation import ProjectEvaluation
    from app.models.transaction import Transaction
    from app.models.token_project import TokenProject


from app.models.project_document import ProjectDocument
from app.models.project_advance import ProjectAdvance


class Project(Base):
    __tablename__ = "PROJECT"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    state: Mapped[ProjectState] = mapped_column(
        SAEnum(ProjectState, name="project_state"),
        nullable=False,
        default=ProjectState.PENDING,
    )
    min_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    risk: Mapped[RiskLevel | None] = mapped_column(
        SAEnum(RiskLevel, name="risk_level"), nullable=True
    )

    annual_expenses: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    annual_gross_profit: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    roi: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    annual_benefits: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    suffix: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ubication: Mapped[str] = mapped_column(String(255), nullable=True)
    estimated_development_days: Mapped[int | None] = mapped_column(nullable=True)
    dividend_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    offering_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("USER.id"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="projects")
    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary=CategoryProject.__table__, back_populates="projects"
    )
    images: Mapped[list["ProjectImage"]] = relationship(
        "ProjectImage", back_populates="project"
    )
    documents: Mapped[list["ProjectDocument"]] = relationship(
        "ProjectDocument", back_populates="project"
    )
    advances: Mapped[list["ProjectAdvance"]] = relationship(
        "ProjectAdvance", back_populates="project"
    )
    evaluations: Mapped[list["ProjectEvaluation"]] = relationship(
        "ProjectEvaluation", back_populates="project"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="project"
    )
    token_project: Mapped[Optional["TokenProject"]] = relationship(
        "TokenProject", back_populates="project", uselist=False
    )
