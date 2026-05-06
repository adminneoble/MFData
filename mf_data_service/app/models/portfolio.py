from pydantic import BaseModel
from typing import Optional


class PortfolioHolding(BaseModel):
    schemecode: str
    invdate: Optional[str] = None
    invenddate: Optional[str] = None
    srno: Optional[str] = None
    fincode: Optional[str] = None
    ASECT_CODE: Optional[str] = None
    sect_code: Optional[str] = None
    noshares: Optional[str] = None
    mktval: Optional[str] = None
    aum: Optional[str] = None
    holdpercentage: Optional[str] = None
    compname: Optional[str] = None
    sect_name: Optional[str] = None
    asect_name: Optional[str] = None
    rating: Optional[str] = None
    flag: str = "A"

    class Config:
        extra = "allow"
