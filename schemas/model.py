from pydantic import BaseModel
from typing import List


class Model(BaseModel):
    name: str
    id: int
    version: str


class ModelInfo(BaseModel):
    models: List[Model]
