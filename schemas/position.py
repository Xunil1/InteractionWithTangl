from __future__ import annotations
from typing import List
from pydantic import BaseModel


class Position(BaseModel):
    name: str
    id: int
    children: List[Position] = []


Position.model_rebuild()


class PositionChild(BaseModel):
    name: str
    id: int


class PositionChildResponse(BaseModel):
    children: List[PositionChild] = []


class PositionResponse(BaseModel):
    children: List[Position] = []


