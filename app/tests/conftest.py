import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from fastapi import BackgroundTasks

@pytest.fixture
def mock_session():
    session = MagicMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    
    async def side_effect_refresh(obj, attribute_names=None):
        if hasattr(obj, "id") and obj.id is None:
            obj.id = uuid4()
        if hasattr(obj, "activated") and obj.activated is None:
            obj.activated = True
        if hasattr(obj, "blocked") and obj.blocked is None:
            obj.blocked = False
        if hasattr(obj, "created_at") and obj.created_at is None:
            obj.created_at = datetime.now()
        if hasattr(obj, "updated_at") and obj.updated_at is None:
            obj.updated_at = datetime.now()
    
    session.refresh = AsyncMock(side_effect=side_effect_refresh)
    session.delete = AsyncMock()
    return session

@pytest.fixture
def background_tasks():
    return MagicMock(spec=BackgroundTasks)
