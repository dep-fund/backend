import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from app.services.project_advance_service import ProjectAdvanceService
from app.models.project_advance import ProjectAdvance
from app.core.enums import ProjectState
from app.exceptions.project_advance import (
    AdvanceNotFound,
    UnauthorizedAdvanceAccess,
)


def make_project(owner_id, state=ProjectState.PENDING):
    project = MagicMock()
    project.user_id = owner_id
    project.state = state
    return project


@pytest.mark.asyncio
async def test_create_advance_success(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    service = ProjectAdvanceService(mock_session)
    service._project_service = mock_project_service

    response = await service.create(
        project_id,
        user_id,
        description="advance 1",
        url="http://test.com/file.pdf",
    )

    assert response.url == "http://test.com/file.pdf"
    assert response.description == "advance 1"


@pytest.mark.asyncio
async def test_create_advance_unauthorized(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(uuid4()))

    service = ProjectAdvanceService(mock_session)
    service._project_service = mock_project_service

    with pytest.raises(UnauthorizedAdvanceAccess):
        await service.create(
            project_id,
            user_id,
            description="advance 1",
            url="http://test.com/file.pdf",
        )


@pytest.mark.asyncio
async def test_list_by_project(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    adv = ProjectAdvance(
        project_id=project_id,
        number=1,
        description="adv",
        url="http://test.com",
    )

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_result = MagicMock()
    mock_result.all.return_value = [adv]

    mock_session.scalars = AsyncMock(return_value=mock_result)

    service = ProjectAdvanceService(mock_session)
    service._project_service = mock_project_service

    result = await service.list_by_project(project_id)

    assert len(result) == 1
    assert result[0].url == "http://test.com"


@pytest.mark.asyncio
async def test_get_by_project_and_number_not_found(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_session.scalar = AsyncMock(return_value=None)

    service = ProjectAdvanceService(mock_session)
    service._project_service = mock_project_service

    with pytest.raises(AdvanceNotFound):
        await service.get_by_project_and_number(project_id, 1)


@pytest.mark.asyncio
async def test_delete_advance_success(mock_session):
    project_id = uuid4()
    user_id = uuid4()

    adv = MagicMock()

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(user_id))

    mock_session.scalar = AsyncMock(return_value=adv)
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    service = ProjectAdvanceService(mock_session)
    service._project_service = mock_project_service

    await service.delete(project_id, 1, user_id)

    mock_session.delete.assert_called_once_with(adv)


@pytest.mark.asyncio
async def test_admin_list_by_project(mock_session):
    project_id = uuid4()

    adv = ProjectAdvance(
        project_id=project_id,
        number=1,
        description="adv",
        url="http://test.com",
    )

    mock_project_service = MagicMock()
    mock_project_service._get_project = AsyncMock(return_value=make_project(uuid4()))

    mock_result = MagicMock()
    mock_result.all.return_value = [adv]

    mock_session.scalars = AsyncMock(return_value=mock_result)

    service = ProjectAdvanceService(mock_session)
    service._project_service = mock_project_service

    result = await service.admin_list_by_project(project_id)

    assert len(result) == 1
    assert result[0].url == "http://test.com"
