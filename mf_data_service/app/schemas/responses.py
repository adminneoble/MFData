from pydantic import BaseModel
from typing import Any, Generic, List, Optional, TypeVar
from datetime import datetime

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int


class APIResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = datetime.utcnow()


# --- Scheme Responses ---

class SchemeListItem(BaseModel):
    schemecode: str
    scheme_name: str = ""
    amc_code: str = ""
    isin: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    amfi_type: Optional[str] = None
    color: str = ""


class SchemeDetailResponse(BaseModel):
    schemecode: str
    scheme_name: str = ""
    amc_code: str = ""
    isin: Optional[str] = None
    s_name: Optional[str] = None
    amfi_name: Optional[str] = None
    status: Optional[str] = None
    type_code: Optional[str] = None
    classcode: Optional[str] = None
    plan: Optional[str] = None
    fund_mgr1: Optional[str] = None
    fund_mgr2: Optional[str] = None
    inception_date: Optional[str] = None
    inception_nav: Optional[str] = None
    min_investment: Optional[str] = None
    sip_available: Optional[str] = None
    etf: Optional[str] = None
    lock_in: Optional[str] = None
    amfi_type: Optional[str] = None
    color: str = ""

    # Enriched fields (joined from other collections)
    current_nav: Optional[dict] = None
    classification: Optional[dict] = None
    isin_details: Optional[dict] = None


class SchemeSnapshotResponse(BaseModel):
    """Composite: master + latest NAV + performance + classification."""
    schemecode: str
    scheme_name: str = ""
    amc_code: str = ""
    isin: Optional[str] = None
    status: Optional[str] = None
    amfi_type: Optional[str] = None
    color: str = ""
    classification: Optional[dict] = None
    current_nav: Optional[dict] = None
    performance: Optional[dict] = None
    expense_ratio: Optional[str] = None
    aum: Optional[dict] = None


# --- NAV Responses ---

class NavHistoryItem(BaseModel):
    schemecode: str
    navdate: str
    navrs: Optional[str] = None
    repurprice: Optional[str] = None
    saleprice: Optional[str] = None


class CurrentNavResponse(BaseModel):
    schemecode: str
    navdate: Optional[str] = None
    navrs: Optional[str] = None
    change: Optional[str] = None
    netchange: Optional[str] = None
    prevnav: Optional[str] = None


# --- Portfolio Responses ---

class PortfolioHoldingItem(BaseModel):
    srno: Optional[str] = None
    compname: Optional[str] = None
    sect_name: Optional[str] = None
    asect_name: Optional[str] = None
    noshares: Optional[str] = None
    mktval: Optional[str] = None
    holdpercentage: Optional[str] = None
    rating: Optional[str] = None


class PortfolioResponse(BaseModel):
    schemecode: str
    invdate: Optional[str] = None
    total_aum: Optional[str] = None
    holdings: List[PortfolioHoldingItem] = []


# --- Performance Responses ---

class PerformanceResponse(BaseModel):
    schemecode: str
    as_of_date: Optional[str] = None
    returns: Optional[dict] = None
    ratios: Optional[dict] = None


# --- Fund Manager Responses ---

class FundManagerResponse(BaseModel):
    id: str
    fundmanager: Optional[str] = None
    designation: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[str] = None


# --- AMC Responses ---

class AMCResponse(BaseModel):
    amc_code: str
    amc: Optional[str] = None
    fund: Optional[str] = None
    s_name: Optional[str] = None
    city: Optional[str] = None
    webiste: Optional[str] = None  # keeping typo from source data
    setup_date: Optional[str] = None
    mf_type: Optional[str] = None


# --- Admin Responses ---

class LoadResult(BaseModel):
    dataset: str
    collection: str
    records_loaded: int
    duration_seconds: float
    status: str = "success"
    error: Optional[str] = None


class DataLoadSummary(BaseModel):
    total_datasets: int
    successful: int
    failed: int
    results: List[LoadResult]
    total_duration_seconds: float
