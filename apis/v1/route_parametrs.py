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
from db.repository.parametrs import get_parametrs_list, get_pars_value
from schemas.parametrs import ParamsResponse, ParamsValue

router = APIRouter()

PROJECT_URL = "/parametrs"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/app/user/authUser")


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getParametrsList",
            summary="Получение списка параметров.",
            description="Данный метод предназначен для получения списка параметров позиций модели.",
            responses={200: {"model": ParamsResponse},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_params_list(position_id: int, catalog_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_parametrs_list(pos_id=position_id, cat_id=catalog_id, token=token, db=db)
    if result["code"] != 200:
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    else:
        return JSONResponse(status_code=result["code"],
                            content=result["data"])


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getParamsValue",
            summary="Получение значение параметра.",
            description="Данный метод предназначен для получения значения параметра позиций модели.",
            responses={200: {"model": ParamsValue},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_params_value(position_id: int, path: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_pars_value(pos_id=position_id, path=path.split(","), token=token, db=db)
    if result["code"] != 200:
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    else:
        return JSONResponse(status_code=result["code"],
                            content={"value": result["data"]})