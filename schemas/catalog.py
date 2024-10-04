from typing import List
from pydantic import BaseModel


class CatalogInfoRequest(BaseModel):
    project_id: str


class Catalog(BaseModel):
    catalog_name: str
    catalog_id: str


class CatalogInfoResponse(BaseModel):
    catalog: List[Catalog]
