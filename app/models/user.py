from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
import uuid
from sqlalchemy import (
    Date,
    Enum as SAEnum,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.enums import AuthProvider, UserType

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.project import Project
    from app.models.project_evaluation import ProjectEvaluation
    from app.models.wallet import Wallet
    from app.models.publication import Publication
    from app.models.trade import Trade


class User(Base):
    __tablename__ = "USER"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activated: Mapped[bool] = mapped_column(Boolean, default=True)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    google_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True
    )
    auth_provider: Mapped[AuthProvider] = mapped_column(
        SAEnum(AuthProvider, name="auth_provider_type"), default=AuthProvider.LOCAL
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
    type: Mapped[UserType] = mapped_column(
        SAEnum(UserType, name="user_type"), nullable=False
    )
    role_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ROLE.id"), nullable=False
    )
    standard: Mapped[Optional["StandardUser"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    admin: Mapped[Optional["AdminUser"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user")
    publications: Mapped[list["Publication"]] = relationship(
        "Publication", back_populates="seller", foreign_keys="Publication.seller_id"
    )
    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="buyer", foreign_keys="Trade.buyer_id"
    )


class StandardUser(Base):
    __tablename__ = "STANDARD_USER"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("USER.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="standard")
    wallets: Mapped[list["Wallet"]] = relationship(
        "Wallet", back_populates="user", cascade="all, delete-orphan"
    )


class AdminUser(Base):
    __tablename__ = "ADMIN_USER"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("USER.id"), primary_key=True
    )
    user: Mapped["User"] = relationship(back_populates="admin")
    evaluations: Mapped[list["ProjectEvaluation"]] = relationship(
        "ProjectEvaluation", back_populates="admin"
    )
