# required modules for routing
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from core.config import Settings
from db.session import get_db
from fastapi.security import OAuth2PasswordBearer

# modules for different schemas
from schemas.error import BaseError
from db.repository.catalog import get_position_list, get_position_children_list
from schemas.position import PositionResponse, PositionChildResponse

router = APIRouter()

PROJECT_URL = "/catalog"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/app/user/authUser")


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getPositionList",
            summary="Получение списка позиций.",
            description="Данный метод предназначен для получения списка позиций по справочникам модели.",
            responses={200: {"model": PositionResponse},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_position(catalog_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_position_list(cat_id=catalog_id, token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"children": result})


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getPositionChildrenList",
            summary="Получение элементов позиции.",
            description="Данный метод предназначен для получения списка элементов позиций по справочникам модели.",
            responses={200: {"model": PositionChildResponse},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_position_children(position_id: int, catalog_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_position_children_list(pos_id=position_id, cat_id=catalog_id, token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"children": result})