# required modules for routing
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import Depends
from db.session import get_db
from core.config import Settings
from fastapi.security import OAuth2PasswordBearer

# modules for different schemas
from schemas.company import CompanyInfo
from schemas.error import BaseError
from db.repository.company import get_company_list

router = APIRouter()

COMPANY_URL = "/company"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/app/user/authUser")


@router.get(Settings.ROOT_URL + COMPANY_URL + "/getCompanyList",
            summary="Получение списка компаний.",
            description="Данный метод предназначен для получения списка компаний, в которых состоит пользователь.",
            responses={200: {"model": CompanyInfo},
                       401: {"model": BaseError}})
def get_companies(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    result = get_company_list(token=token, db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, list):
        return JSONResponse(status_code=200,
                            content={"companies": result})
