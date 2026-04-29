from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Enum, Integer, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

import enum
from app.core.database import Base 



class ProjectState(str, enum.Enum):
    PENDING = "PENDIENTE"
    APROBADO = "APROBADO"
    CANCELED = "CANCELADO"

class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    total_amount = Column(Float, nullable=False)
    state = Column(Enum(ProjectState), server_default=ProjectState.PENDING)
    ubication = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con el Usuario:
    user_id = Column(UUID(as_uuid=True), ForeignKey("USER.id"), nullable=False)
    user = relationship("User", back_populates="project")