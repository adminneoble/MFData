from pydantic import BaseModel, Field
from typing import List, Optional


class BulkISINRequest(BaseModel):
    isins: List[str] = Field(..., min_length=1, max_length=100)


class BulkSchemeCodeRequest(BaseModel):
    schemecodes: List[str] = Field(..., min_length=1, max_length=100)


class SchemeSearchParams(BaseModel):
    q: Optional[str] = None
    amc_code: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    status: Optional[str] = None
    amfi_type: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


class NavHistoryParams(BaseModel):
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=100, ge=1, le=1000)


class DataLoadRequest(BaseModel):
    datasets: Optional[List[str]] = None  # None = load all
    drop_existing: bool = False
