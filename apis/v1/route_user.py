# required modules for routing
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import Depends
from db.models.user import User
from db.session import get_db
from core.config import Settings

# modules for different schemas
from db.repository.user import create_new_user
from schemas.user import UserAuth, UserInfo
from schemas.error import BaseError

router = APIRouter()

USER_URL = "/user"


@router.post(Settings.ROOT_URL + USER_URL + "/authUser",
             summary="Аутентификация пользователя.",
             description="Данный метод предназначен для аутентификации пользователя в веб-сервисе",
             responses={200: {"model": UserInfo},
                        401: {"model": BaseError}})
def create_user(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    result = create_new_user(user=UserAuth(username=form.username, password=form.password), db=db)
    if isinstance(result, dict):
        return JSONResponse(status_code=result["code"],
                            content={"status": result["data"]["status"],
                                     "description_en": result["data"]["description_en"],
                                     "description_ru": result["data"]["description_ru"]})
    elif isinstance(result, User):
        return JSONResponse(status_code=200,
                            content={"username": result.username,
                                     "access_token": result.tt_token,
                                     "expire": Settings.TOKEN_EXPIRE})
