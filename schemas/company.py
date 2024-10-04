from pydantic import BaseModel
from typing import List


class Company(BaseModel):
    company_name: str
    company_id: int
    is_personal: bool


class CompanyInfo(BaseModel):
    companies: List[Company]
