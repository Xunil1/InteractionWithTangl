# required modules for routing
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from schemas.project import ProjectInfo, FolderInfo
from db.session import get_db
from core.config import Settings
from fastapi.security import OAuth2PasswordBearer

# modules for different schemas
from db.repository.project import get_project_list, get_folder_list, get_model_list
from schemas.model import ModelInfo
from schemas.error import BaseError

router = APIRouter()

PROJECT_URL = "/project"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/app/user/authUser")


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getProjectList",
            summary="Получение списка проектов.",
            description="Данный метод предназначен для получения списка проектов компании.",
            responses={200: {"model": ProjectInfo},
                       400: {"model": BaseError},
                       401: {"model": BaseError}})
def get_companies(company_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_project_list(c_id=company_id, token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"projects": result})


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getProjectFolders",
            summary="Получение структуры проекта.",
            description="Данный метод предназначен для получения структуры проекта компании.",
            responses={200: {"model": FolderInfo},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_companies(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_folder_list(p_id=project_id, token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"folders": result})


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getModels",
            summary="Получение моделей проекта.",
            description="Данный метод предназначен для получения моделей проекта компании.",
            responses={200: {"model": ModelInfo},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_models(project_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_model_list(p_id=project_id, token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"models": result})