from pydantic import BaseModel
from typing import Optional


class CurrentNav(BaseModel):
    schemecode: str
    navdate: Optional[str] = None
    navrs: Optional[str] = None
    repurprice: Optional[str] = None
    saleprice: Optional[str] = None
    change: Optional[str] = None
    netchange: Optional[str] = None
    prevnav: Optional[str] = None
    prenavdate: Optional[str] = None
    flag: str = "A"

    class Config:
        extra = "allow"


class NavHistory(BaseModel):
    schemecode: str
    navdate: str
    navrs: Optional[str] = None
    repurprice: Optional[str] = None
    saleprice: Optional[str] = None
    adjustednav_c: Optional[str] = None
    adjustednav_nonc: Optional[str] = None
    flag: str = "A"

    class Config:
        extra = "allow"
