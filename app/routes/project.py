# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.core.database import get_db # Ajustar según donde tengan el generador de sesión
# from app.models.project import Project
# from app.schemas.project import ProjectCreate, ProjectResponse
# from app.core.database import get_session as get_db


# router = APIRouter(prefix="/project", tags=["Projects"])
# router = APIRouter(prefix="/projects", tags=["Projects"])

# @router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
# def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
#     new_project = Project(**project_in.model_dump())
#     db.add(new_project)
#     db.commit()
#     db.refresh(new_project)
#     return new_project


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session  # <--- Cambiamos get_db por get_session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/project", tags=["Project"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_session)): # <--- Usamos get_session acá también
    new_project = Project(**project_in.model_dump())
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project