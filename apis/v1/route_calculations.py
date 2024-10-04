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
from db.repository.calculations import get_value_parametric_field, get_levels as gt_lvl, get_total as get_ttl, get_total_by_levels
from schemas.calculations import CalculationVal, LevelsResponse, TotalResponse, TotalByLevel


router = APIRouter()

PROJECT_URL = "/calculations"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/app/user/authUser")


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getParametricValue",
            summary="Получение значения параметра.",
            description="Данный метод предназначен для получения значения определенного параметра.",
            responses={200: {"model": CalculationVal},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_parametric_value(expression: str, values: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_value_parametric_field(expr=expression, val=values, token=token, db=db)
    if result["code"] != 200:
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    else:
        return JSONResponse(status_code=result["code"],
                            content={"value": result["data"]})


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getLevels",
            summary="Получение списка уровней (этажей).",
            description="Данный метод предназначен для получения списка уровней (этажей) модели.",
            responses={200: {"model": LevelsResponse},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_levels(model_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = gt_lvl(m_id=model_id, token=token, db=db)
    if result["code"] != 200:
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    else:
        return JSONResponse(status_code=result["code"],
                            content={"levels": result["data"]})


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getElementTotalByLevel",
            summary="Получение количества элементов на определенном этаже.",
            description="Данный метод предназначен для получения количества элементов на определенном этаже.",
            responses={200: {"model": TotalByLevel},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_totalByLvl(position_id: int, level_name: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_total_by_levels(pos_id=position_id, lvl_name=level_name, token=token, db=db)
    if result["code"] != 200:
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    else:
        return JSONResponse(status_code=result["code"],
                            content={"count": result["data"]})


@router.get(Settings.ROOT_URL + PROJECT_URL + "/getTotal",
            summary="Получение общего количества по позициям.",
            description="Данный метод предназначен для получения общего количества элементов по позициям модели.",
            responses={200: {"model": TotalResponse},
                       400: {"model": BaseError},
                       401: {"model": BaseError},
                       403: {"model": BaseError}})
def get_total(position_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_ttl(pos_id=position_id, token=token, db=db)
    if result["code"] != 200:
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    else:
        return JSONResponse(status_code=result["code"],
                            content={"total": result["data"]})