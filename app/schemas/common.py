from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number starting from 1")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    search: Optional[str] = Field(None, description="Optional search term")
    sort_by: Optional[str] = Field(None, description="Column name to sort by")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order: asc or desc")

class PaginatedResponse(BaseModel, Generic[DataT]):
    items: List[DataT]
    total: int
    page: int
    page_size: int
    pages: int

class GenericResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[dict] = None
