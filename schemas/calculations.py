from typing import List

from pydantic import BaseModel


class CalculationVal(BaseModel):
    value: str


class LevelsResponse(BaseModel):
    levels: list = []


class TotalByLevel(BaseModel):
    count: int = 0


class TotalResponse(BaseModel):
    total: int = None
