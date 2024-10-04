from __future__ import annotations
from pydantic import BaseModel
from typing import List


class Folder(BaseModel):
    models: list
    folders: List[Folder] = []
    unionModels: list
    name: str


Folder.model_rebuild()


class Project(BaseModel):
    project_name: str
    project_id: int


class ProjectInfo(BaseModel):
    projects: List[Project]


class FolderInfo(BaseModel):
    folders: List[Folder]
