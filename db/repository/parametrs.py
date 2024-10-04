from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models.catalog import Catalog
from db.models.position import Position
from db.models.parametrs import Params
from db.models.model import Model
from db.models.user import User
from core.config import Settings
from core.tangl_requests import get_attr
import json


def get_parametrs_list(pos_id: int, cat_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()

    cat_db = db.query(Catalog).filter(Catalog.id == cat_id).one_or_none()
    m_db: Model = cat_db.model
    p_db = m_db.project
    c_db = p_db.company
    pos_db = db.query(Position).filter(Position.id == pos_id).one_or_none()
    if c_db not in user.company:
        return {"code": 403, "data": {"status": "UserAuthError",
                                      "description_en": "The user does not have access to this model.",
                                      "description_ru": "Пользователь не не имеет доступа к этой модели."}}

    try:
        tree = get_tree(m_db.model_tangl_version_id, user.tangl_token)
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

    q = Position.catalog_id == cat_id, \
        Position.model_id == m_db.id, \
        Position.parent_tangl_id == pos_db.position_tangl_id

    positions = db.query(Position).filter(*q).all()

    elements = dict()
    for i in tree["metaTree"]:
        for j in i["typeGroups"]:
            for k in positions:
                if j["name"].lower().startswith(k.position_name.lower().split(" ")[0] + "_") or j["name"].lower().startswith(k.position_name.lower().split(" ")[0] + " "):
                    if k.id in elements.keys():
                        elements[k.id].extend(j["elements"])
                    else:
                        elements[k.id] = j["elements"]
    for k, val in elements.items():
        for v in val:
            q = Params.model_id == m_db.id, Params.el_num == v["elNum"]
            el = db.query(Params).filter(*q).one_or_none()
            if el:
                if el.model_version == m_db.version:
                    continue
                else:
                    p = get_params(m_db.model_tangl_id, user.tangl_token, el.el_num)
                    stmt = (
                        update(Params).
                        where(*q).
                        values(el_num=el.el_num,
                               el_name=el.el_name,
                               el_type=el.el_type,
                               el_category=el.el_category,
                               el_id=el.el_id,
                               param=json.loads(p["meta"]),
                               model_version=m_db.version
                               )
                    )

                    db.execute(stmt)
            else:
                p = get_params(m_db.model_tangl_id, user.tangl_token, v["elNum"])
                par = Params(
                    el_num=v["elNum"],
                    el_name=v["name"],
                    el_type=v["type"],
                    el_category=v["category"],
                    el_id=v["id"],
                    param=json.loads(p["meta"]),
                    model_version=m_db.version,
                    model_id=m_db.id,
                    position_parent_id=int(k)

                )
                db.add(par)
    db.commit()
    pars = list()
    for i in positions:
        q = Params.model_id == m_db.id, Params.position_parent_id == i.id
        el = db.query(Params).filter(*q).first()
        if el is not None:
            pars.append(el.param)

    res_pars = dict()

    for i in pars:
        merge_nested_dicts(res_pars, i)

    return {"code": 200, "data": res_pars}


def merge_nested_dicts(d1, d2):
    for key, value in d2.items():
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            merge_nested_dicts(d1[key], value)
        else:
            d1[key] = value


def get_tree(model_id: str, auth_token: str):
    url = Settings.URLS["tree_url"] + "/" + model_id + "/tree"
    tree = get_attr(url, auth_token)
    return tree


def get_params(model_id: str, auth_token: str, elNum: int):
    url = Settings.URLS['params_url'] + '/' + model_id + '?elNum=' + str(elNum)
    pars = get_attr(url, auth_token)
    return pars


def get_pars_value(pos_id: int, path: list, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    pos_db = db.query(Position).filter(Position.id == pos_id).one_or_none()
    cat_db = pos_db.catalog
    m_db: Model = cat_db.model
    p_db = m_db.project
    c_db = p_db.company
    if user is None:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    if pos_db is None:
        return {"code": 400, "data": {"status": "RequestError",
                                      "description_en": f"There is no position with ID {pos_id}.",
                                      "description_ru": f"Позиции с ИД {pos_id} не существует."}}

    if pos_db.position_tangl_id != pos_db.parent_tangl_id:
        return {"code": 400, "data": {"status": "RequestError",
                                      "description_en": f"There is no position with ID {pos_id}.",
                                      "description_ru": f"Позиции с ИД {pos_id} не существует."}}

    if c_db not in user.company:
        return {"code": 403, "data": {"status": "UserAuthError",
                                      "description_en": "The user does not have access to this model.",
                                      "description_ru": "Пользователь не не имеет доступа к этой модели."}}

    q = Params.model_id == m_db.id, Params.position_parent_id == pos_id

    el = db.query(Params).filter(*q).first()
    value = None

    if el is not None:
        pars = el.param

        value = pars[path[0]]

        for i in range(1, len(path)):
            try:
                value = value[path[i].strip()]
            except KeyError:
                value = None
                break
    return {"code": 200, "data": value}