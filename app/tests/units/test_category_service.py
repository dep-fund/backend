import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from app.services.category_service import CategoryService
from app.models.category import Category
from unittest.mock import AsyncMock

from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
)

from app.exceptions.category import CategoryNotFound
from datetime import datetime, timezone

# --- Create Tests ---


@pytest.mark.asyncio
async def test_category_create(mock_session):
    service = CategoryService(mock_session)

    data = CategoryCreateRequest(
        name="Football", description="Football related category"
    )

    response = await service.create(data)

    assert response.name == "Football"
    assert response.description == "Football related category"

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


# --- Update Tests ---


@pytest.mark.asyncio
async def test_category_update_success(mock_session):
    category_id = uuid4()

    category = Category(
        id=category_id, name="Football", description="Old football Test"
    )

    mock_session.scalar.return_value = category

    service = CategoryService(mock_session)

    data = CategoryUpdateRequest(name="Basketball", description="Basketball category")

    response = await service.update(category_id, data)

    assert response.name == "Basketball"
    assert response.description == "Basketball category"

    assert category.name == "Basketball"
    assert category.description == "Basketball category"

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_category_update_not_found(mock_session):
    mock_session.scalar.return_value = None

    service = CategoryService(mock_session)

    data = CategoryUpdateRequest(name="Tennis")

    with pytest.raises(CategoryNotFound):
        await service.update(uuid4(), data)


# --- Get By ID Tests ---


@pytest.mark.asyncio
async def test_category_get_by_id_success(mock_session):
    category_id = uuid4()

    category = Category(
        id=category_id,
        name="Volleyball",
        description="Volleyball category",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_session.scalar = AsyncMock(return_value=category)

    service = CategoryService(mock_session)

    response = await service.get_by_id(category_id)

    assert response.name == "Volleyball"
    assert response.description == "Volleyball category"


@pytest.mark.asyncio
async def test_category_get_by_id_not_found(mock_session):
    mock_session.scalar.return_value = None

    service = CategoryService(mock_session)

    with pytest.raises(CategoryNotFound):
        await service.get_by_id(uuid4())


# --- Get Categories By IDs Tests ---


@pytest.mark.asyncio
async def test_get_categories_by_ids(mock_session):
    categories = [
        Category(id=uuid4(), name="Football", description="Football category"),
        Category(id=uuid4(), name="Basketball", description="Basketball category"),
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = categories

    mock_session.scalars.return_value = mock_scalars

    service = CategoryService(mock_session)

    response = await service.get_categories_by_ids([uuid4(), uuid4()])

    assert len(response) == 2
    assert response[0].name == "Football"
    assert response[1].name == "Basketball"


# --- List Tests ---


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_category_list(mock_session):
    now = datetime.now(timezone.utc)

    categories = [
        Category(
            id=uuid4(),
            name="Football",
            description="Football category",
            created_at=now,
            updated_at=now,
        ),
        Category(
            id=uuid4(),
            name="Basketball",
            description="Basketball category",
            created_at=now,
            updated_at=now,
        ),
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = categories

    mock_session.scalar = AsyncMock(return_value=2)
    mock_session.scalars = AsyncMock(return_value=mock_scalars)

    service = CategoryService(mock_session)

    total, response = await service.list()

    assert total == 2
    assert len(response) == 2
    assert response[0].name == "Football"
    assert response[1].name == "Basketball"


@pytest.mark.asyncio
async def test_category_list_with_search(mock_session):
    now = datetime.now(timezone.utc)

    categories = [
        Category(
            id=uuid4(),
            name="Football",
            description="Football category",
            created_at=now,
            updated_at=now,
        )
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = categories

    mock_session.scalar = AsyncMock(return_value=1)
    mock_session.scalars = AsyncMock(return_value=mock_scalars)

    service = CategoryService(mock_session)

    total, response = await service.list(search="Foot")

    assert total == 1
    assert len(response) == 1
    assert response[0].name == "Football"


@pytest.mark.asyncio
async def test_category_list_empty(mock_session):
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []

    mock_session.scalar.return_value = 0
    mock_session.scalars.return_value = mock_scalars

    service = CategoryService(mock_session)

    total, response = await service.list()

    assert total == 0
    assert response == []
