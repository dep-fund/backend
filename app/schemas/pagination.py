from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    total_pages: Optional[int] | None = None
    page: int
    page_size: int
    results: List[T]
