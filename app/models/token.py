from typing import TYPE_CHECKING
import uuid
from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.token_project import TokenProject


class Token(Base):
    __tablename__ = "TOKEN"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    suffix: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    contract_address: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )

    token_projects: Mapped[list["TokenProject"]] = relationship(
        "TokenProject", back_populates="token"
    )
