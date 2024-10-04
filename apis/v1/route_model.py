# required modules for routing
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from core.config import Settings
from db.session import get_db
from fastapi.security import OAuth2PasswordBearer

# modules for different schemas
from schemas.catalog import CatalogInfoResponse
from schemas.error import BaseError
from db.repository.model import get_catalog_list

router = APIRouter()

PROJECT_URL = "/model"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/app/user/authUser")


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getCatalogList",
            summary="Получение списка справочников.",
            description="Данный метод предназначен для получения списка справочников формирования модели.",
            responses={200: {"model": CatalogInfoResponse},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_companies(model_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_catalog_list(m_id=model_id, token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"catalogs": result})