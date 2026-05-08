import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from app.services.project_document_service import ProjectDocumentService
from app.schemas.project_document import ProjectDocumentCreate
from app.models.project_document import ProjectDocument
from app.core.enums import ProjectState
from app.exceptions.project_document import (
    DocumentNotFound,
    UnauthorizedDocumentAccess,
    DocumentNotDeleted
)

def make_project(owner_id, state=ProjectState.PENDING):
    project = MagicMock()
    project.user_id = owner_id
    project.state = state
    return project


@pytest.mark.asyncio
async def test_create_document_success(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_session.scalar = AsyncMock(return_value=1)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    service = ProjectDocumentService(mock_session)
    service._project_service = mock_project_service

    data = ProjectDocumentCreate(url="http://test.com")

    response = await service.create(project_id, user_id, data)

    assert response.url == "http://test.com"


@pytest.mark.asyncio
async def test_create_document_unauthorized(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(uuid4()))

    service = ProjectDocumentService(mock_session)
    service._project_service = mock_project_service

    data = ProjectDocumentCreate(url="http://test.com")

    with pytest.raises(UnauthorizedDocumentAccess):
        await service.create(project_id, user_id, data)


@pytest.mark.asyncio
async def test_list_by_project(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    now = datetime.now(timezone.utc)

    doc = ProjectDocument(
        project_id=project_id,
        number=1,
        url="http://test.com"
    )

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_result = MagicMock()
    mock_result.all.return_value = [doc]

    mock_session.scalars = AsyncMock(return_value=mock_result)

    service = ProjectDocumentService(mock_session)
    service._project_service = mock_project_service

    result = await service.list_by_project(project_id, user_id)

    assert len(result) == 1
    assert result[0].url == "http://test.com"


@pytest.mark.asyncio
async def test_get_by_project_and_number_not_found(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_session.scalar = AsyncMock(return_value=None)

    service = ProjectDocumentService(mock_session)
    service._project_service = mock_project_service

    with pytest.raises(DocumentNotFound):
        await service.get_by_project_and_number(project_id, 1, user_id)


@pytest.mark.asyncio
async def test_delete_document_success(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    project = make_project(user_id, ProjectState.PENDING)

    doc = MagicMock()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=project)

    mock_session.scalar = AsyncMock(return_value=doc)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    service = ProjectDocumentService(mock_session)
    service._project_service = mock_project_service

    await service.delete(project_id, 1, user_id)

    mock_session.delete.assert_called_once_with(doc)


@pytest.mark.asyncio
async def test_delete_document_blocked_if_approved(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    project = make_project(user_id, ProjectState.APPROVED)

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=project)

    service = ProjectDocumentService(mock_session)
    service._project_service = mock_project_service

    with pytest.raises(DocumentNotDeleted):
        await service.delete(project_id, 1, user_id)