from pydantic import BaseModel
from typing import Optional


class FundManager(BaseModel):
    id: str
    initial: Optional[str] = None
    fundmanager: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[str] = None
    basicdetails: Optional[str] = None
    designation: Optional[str] = None
    age: Optional[str] = None
    reporteddate: Optional[str] = None
    flag: str = "A"

    class Config:
        extra = "allow"
