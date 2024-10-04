import sqlalchemy.exc
from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models.catalog import Catalog
from db.models.position import Position
from db.models.model import Model
from db.models.user import User
from db.models.parametrs import Params
from core.config import Settings
from core.tangl_requests import get_attr
import time
import numexpr


def get_value_parametric_field(expr: str, val: str, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    if user is None:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    try:
        vals = val.replace("{", "").replace("}", "").replace(" ", "").replace('"', '').split(",")
        if vals[-1] == "":
            vals.pop(-1)
        d = {}
        for i in vals:
            k, v = i.split(":")
            d[k] = float(v)

        res = numexpr.evaluate(expr, d)
        return {"code": 200, "data": str(res)}
    except IndexError:
        return {"code": 400, "data": {"status": "IncorrectValueError",
                                      "description_en": "The values were passed in the wrong form.",
                                      "description_ru": "Значения переданы в неверном виде."}}
    except ValueError:
        return {"code": 400, "data": {"status": "TypeValueError",
                                      "description_en": "The value passed is not a numeric value.",
                                      "description_ru": "Передано не числовое значение."}}
    except KeyError:
        return {"code": 400, "data": {"status": "ExpressionError",
                                      "description_en": "The expression uses a variable whose value is not passed.",
                                      "description_ru": "В выражении используется переменная, значение которой не передано."}}
    except SyntaxError:
        return {"code": 400, "data": {"status": "IncorrectExpressionError",
                                      "description_en": "An incorrect expression was passed.",
                                      "description_ru": "Передано некорректное выражение."}}


def get_levels(m_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()

    if user is None:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    m_db: Model = db.query(Model).filter(Model.id == m_id).one_or_none()

    try:
        tree = get_tree(m_db.model_tangl_id, user.tangl_token)
        if tree == "":
            return {"code": 401, "data": {"status": "UserAuthError",
                                          "description_en": "User is not auth or register.",
                                          "description_ru": "Пользователь не авторизован или не зарегистрирован."}}
    except:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    if tree["metaTree"] is None:
        return {"code": 400, "data": {"status": "RequestError",
                                      "description_en": "Model is empty",
                                      "description_ru": "Пустая модель"}}

    levels = set()
    for i in tree['metaTree']:
        if i["name"] == "Уровни":
            for j in i["typeGroups"]:
                if j["name"] == "ADSK_Стрелка_Проектная_Вверх_Имя уровня":
                    for k in j["elements"]:
                        levels.add(k["name"])
            return {"code": 200, "data": list(sorted(levels))}


def get_total_by_levels(pos_id: int, lvl_name: str, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()

    if user is None:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    pos_db = db.query(Position).filter(Position.id == pos_id).one_or_none()
    m_db = pos_db.model
    p_db = m_db.project
    c_db = p_db.company

    if c_db.user_id != user.id:
        return {"code": 403,
                "data": {"status": "PermissionError",
                         "description_en": "The user does not have access to this model with '" + str(
                             m_db.id) + "' id.",
                         "description_ru": "Пользователь не имеет доступа к данной модели с ИД '" + str(
                             m_db.id) + "'."}}

    elements = db.query(Params).filter(Params.position_parent_id == pos_id).all()

    if elements is None:
        return {"code": 404,
                "data": {"status": "PositionNotFound",
                         "description_en": "Item ID '" + str(
                             pos_id) + "' is missing or not accessible to the user.",
                         "description_ru": "Элемент с ИД '" + str(
                             pos_id) + "' отсутствует или не доступен для пользователя."}}

    count = 0
    for i in elements:
        pars = i.param
        if pars["Meta"]["Element"]["Level"]["Name"] == lvl_name:
            count += 1

    return {"code": 200, "data": count}

def get_tree(model_id: str, auth_token: str):
    url = Settings.URLS["tree_url"] + "/" + model_id + "/tree"
    tree = get_attr(url, auth_token)
    return tree


def get_total(pos_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    if user is None:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    pos_db = db.query(Position).filter(Position.id == pos_id).one_or_none()
    if pos_db is None:
        return {"code": 404,
                "data": {"status": "PositionNotFound",
                         "description_en": "Item ID '" + str(
                             pos_id) + "' is missing or not accessible to the user.",
                         "description_ru": "Элемент с ИД '" + str(
                             pos_id) + "' отсутствует или не доступен для пользователя."}}

    m_db = pos_db.model
    p_db = m_db.project
    c_db = p_db.company

    if c_db.user_id != user.id:
        return {"code": 403,
                "data": {"status": "PermissionError",
                         "description_en": "The user does not have access to this model with '" + str(m_db.id) + "' id.",
                         "description_ru": "Пользователь не имеет доступа к данной модели с ИД '" + str(m_db.id) + "'."}}

    return {"code": 200, "data": pos_db.position_value}