from sqlalchemy.orm import Session
from sqlalchemy import update
import requests
from schemas.user import UserAuth
from db.models.user import User
from core.hashing import Hasher
from core.config import Settings
from datetime import datetime, timedelta


def create_new_user(user: UserAuth, db: Session):
    u_db = db.query(User).filter(User.username == user.username).one_or_none()

    if u_db and not u_db.last_reg is None:
        if u_db.last_reg + timedelta(seconds=Settings.TOKEN_EXPIRE) > datetime.now():
            return u_db

    token = get_tangl_token(user.username, user.password)
    user = User(
        username=user.username,
        hash_password=Hasher.get_password_hash(user.password),
        tangl_token=token,
        tt_token=token,
        last_reg=datetime.now()
    )
    if db.query(User).filter(User.username == user.username).one_or_none():
        stmt = (
            update(User).
            where(User.username == user.username).
            values(tangl_token=token,
                   tt_token=token,
                   last_reg=datetime.now())
        )

        db.execute(stmt)
        db.commit()
    else:
        if user.tangl_token is None:
            return {"code": 401, "data": {"status": "UserAuthError", "description_en": "User is not registered.",
                                          "description_ru": "Пользователь не зарегистрирован."}}
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_tangl_token(login, password):
    head = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'client_id': 'BimTanglValue_External', 'grant_type': 'password', 'username': login,
            'password': password}
    req = requests.post(Settings.URLS["auth_url"], data=data, headers=head)
    res = req.json()
    try:
        a_token = res["access_token"]
        return a_token
    except:
        return None
