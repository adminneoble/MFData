from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SchemeMaster(BaseModel):
    """Core scheme record combining Scheme_master + Scheme_details fields."""
    schemecode: str
    amc_code: str = ""
    scheme_name: str = ""
    color: str = ""  # risk color
    flag: str = "A"

    # From Scheme_details (merged)
    amfi_code: Optional[str] = None
    cams_code: Optional[str] = None
    s_name: Optional[str] = None
    amfi_name: Optional[str] = None
    isin_code: Optional[str] = None
    type_code: Optional[str] = None
    opt_code: Optional[str] = None
    classcode: Optional[str] = None
    rt_code: Optional[str] = None
    plan: Optional[str] = None
    cust_code: Optional[str] = None
    status: Optional[str] = None
    fund_mgr1: Optional[str] = None
    fund_mgr2: Optional[str] = None
    fund_mgr3: Optional[str] = None
    fund_mgr4: Optional[str] = None
    fund_mgr_code1: Optional[str] = None
    FUND_MGR_CODE2: Optional[str] = None
    FUND_MGR_CODE3: Optional[str] = None
    FUND_MGR_CODE4: Optional[str] = None
    mininvt: Optional[str] = None
    sip: Optional[str] = None
    swp: Optional[str] = None
    stp: Optional[str] = None
    switch: Optional[str] = None
    etf: Optional[str] = None
    Incept_date: Optional[str] = None
    Incept_Nav: Optional[str] = None
    LegalNames: Optional[str] = None
    AMFIType: Optional[str] = None
    LockIn: Optional[str] = None
    LockPeriod: Optional[str] = None
    DateOfAllot: Optional[str] = None
    Liquidated_Date: Optional[str] = None
    Direct_Plan: Optional[str] = None
    Old_Plan: Optional[str] = None
    IsPurchaseAvailable: Optional[str] = None
    IsRedeemAvailable: Optional[str] = None

    class Config:
        extra = "allow"


class SchemeISIN(BaseModel):
    """ISIN-to-schemecode mapping from schemeisinmaster.txt."""
    Id: Optional[str] = None
    ISIN: str
    Schemecode: str
    Amc_code: Optional[str] = None
    NseSymbol: Optional[str] = None
    Series: Optional[str] = None
    RTASchemecode: Optional[str] = None
    LongSchemeDescrip: Optional[str] = None
    ShortSchemeDescrip: Optional[str] = None
    Status: Optional[str] = None
    flag: str = "A"

    class Config:
        extra = "allow"
