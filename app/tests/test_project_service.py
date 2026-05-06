from datetime import datetime
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from app.services.project_service import ProjectService
from app.core.enums import ProjectState
from app.exceptions.project import (
    ProjectNotFound,
    ProjectNotPending,
    MissingMandatoryProjectInfo,
)
from app.models.project import Project

from app.models.category import Category


def create_valid_project():
    project = Project(
        id=uuid4(),
        name="Test Project",
        description="Test Description",
        total_amount=Decimal("1000.00"),
        ubication="Test Location",
        state=ProjectState.PENDING,
        user_id=uuid4(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    project.categories = []
    project.user = MagicMock()
    project.user.email = "owner@example.com"
    return project

@patch("app.services.project_service.MailService")
@pytest.mark.asyncio
async def test_evaluate_approve_success(MockMailService, mock_session):
    # Setup
    project = create_valid_project()
    category = Category(
        id=uuid4(),
        name="Technology",
        description="Tech projects",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    project.categories = [category]
    
    mock_session.scalar.return_value = project
    
    service = ProjectService(mock_session)
    
    # Execute
    response = await service.evaluate(project.id, uuid4(), is_approved=True)
    
    # Assert
    assert project.state == ProjectState.APPROVED
    assert response.state == ProjectState.APPROVED
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    MockMailService.return_value.send_project_status_email.assert_called_once()

@patch("app.services.project_service.MailService")
@pytest.mark.asyncio
async def test_evaluate_reject_success(MockMailService, mock_session):
    # Setup
    project = create_valid_project()
    
    mock_session.scalar.return_value = project
    
    service = ProjectService(mock_session)
    
    # Execute
    response = await service.evaluate(project.id, uuid4(), is_approved=False, reason="Insufficient details")
    
    # Assert
    assert project.state == ProjectState.REJECTED
    assert response.state == ProjectState.REJECTED
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_evaluate_project_not_found(mock_session):
    # Setup
    mock_session.scalar.return_value = None
    
    service = ProjectService(mock_session)
    
    # Execute & Assert
    with pytest.raises(ProjectNotFound):
        await service.evaluate(uuid4(), uuid4(), is_approved=True)

@pytest.mark.asyncio
async def test_evaluate_project_not_pending(mock_session):
    # Setup
    project = create_valid_project()
    project.state = ProjectState.APPROVED
    mock_session.scalar.return_value = project
    
    service = ProjectService(mock_session)
    
    # Execute & Assert
    with pytest.raises(ProjectNotPending):
        await service.evaluate(uuid4(), uuid4(), is_approved=True)

@pytest.mark.asyncio
async def test_evaluate_approve_missing_info(mock_session):
    # Setup
    project = create_valid_project()
    project.name = "" # Missing mandatory info
    mock_session.scalar.return_value = project
    
    service = ProjectService(mock_session)
    
    # Execute & Assert
    with pytest.raises(MissingMandatoryProjectInfo):
        await service.evaluate(uuid4(), uuid4(), is_approved=True)
