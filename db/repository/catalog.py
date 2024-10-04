import sqlalchemy.exc
from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models.catalog import Catalog
from db.models.position import Position
from db.models.model import Model
from db.models.user import User
from core.config import Settings
from core.tangl_requests import get_attr
import time


def get_position_list(cat_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    cat_db = db.query(Catalog).filter(Catalog.id == cat_id).one_or_none()
    if cat_db is None:
        return {"code": 400,
                "data": {"status": "RequestError",
                         "description_en": f"There is no catalog with ID {cat_id}.",
                         "description_ru": f"Справочника с ИД {cat_id} не существует."}}

    m_db: Model = cat_db.model
    p_db = m_db.project
    c_db = p_db.company

    try:
        url = Settings.URLS[
                  "odata_url"] + "('" + c_db.company_name + "','" + p_db.project_name + "','" + m_db.model_name + "','" + cat_db.catalog_name + "')?parents=true "
        positions = get_attr(url, user.tangl_token)
        if "error" in positions.keys() and "code" in positions["error"].keys():
            if positions["error"]["code"] == '404':
                return {"code": 400, "data": {"status": "RequestError",
                                              "description_en": "Union tree not found.",
                                              "description_ru": "Дерево объединений не найдено."}}
            else:
                return {"code": 400, "data": {"status": "RequestError",
                                              "description_en": "An unexpected error occurred.",
                                              "description_ru": "Возникла непредвиденная ошибка."}}
    except:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    if c_db is None:
        return {"code": 400, "data": {"status": "UserCompanyError",
                                      "description_en": "The user is not a member of this company.",
                                      "description_ru": "Пользователь не состоит в данной компании."}}
    if m_db.version != positions["value"][0]["Version"]:
        query = Model.id == m_db.id, Model.model_name == m_db.model_name
        model = db.query(Model).filter(*query).one_or_none()
        if model:
            stmt = (
                update(Model).
                where(*query).
                values(version=positions["value"][0]["Version"]
                       )
            )
            db.execute(stmt)

    for i in positions["value"]:
        try:
            q = Position.catalog_id == cat_id, Position.model_id == m_db.id, Position.position_tangl_id == i["TanglId"]
            pst = db.query(Position).filter(*q).one_or_none()
        except sqlalchemy.exc.MultipleResultsFound:
            q = Position.catalog_id == cat_id, Position.model_id == m_db.id, Position.position_tangl_id == i["TanglId"], Position.position_name == i["Name"]
            pst = db.query(Position).filter(*q).one_or_none()

        if pst:
            stmt = (
                update(Position).
                where(*q).
                values(position_name=i["Name"],
                       position_value=i["Value"],
                       position_tangl_id=i["TanglId"],
                       parent_tangl_id=i["ParentTanglId"],
                       catalog_id=cat_db.id,
                       model_id=m_db.id
                       )
            )

            db.execute(stmt)

        else:
            pos = Position(
                position_name=i["Name"],
                position_value=i["Value"],
                position_tangl_id=i["TanglId"],
                parent_tangl_id=i["ParentTanglId"],
                catalog_id=cat_db.id,
                model_id=m_db.id
            )
            db.add(pos)
    db.commit()
    p = db.query(Position).filter(Position.model_id == m_db.id, Position.catalog_id == cat_db.id).all()

    position_dict = get_struct_odata("00000000-0000-0000-0000-000000000000", p)

    return position_dict


def get_position_children_list(pos_id: int, cat_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    if user is None:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}
    cat_db = db.query(Catalog).filter(Catalog.id == cat_id).one_or_none()
    m_db: Model = cat_db.model
    p_db = m_db.project
    c_db = p_db.company

    if c_db not in user.company:
        return {"code": 400, "data": {"status": "UserCompanyError",
                                      "description_en": "The user is not a member of this company.",
                                      "description_ru": "Пользователь не состоит в данной компании."}}

    pos_db = db.query(Position).filter(Position.id == pos_id).one_or_none()

    q = Position.catalog_id == cat_id, Position.model_id == m_db.id, Position.parent_tangl_id == pos_db.position_tangl_id
    positions = db.query(Position).filter(*q).all()

    pos_chd = list()

    for i in positions:
        pos_chd.append(
            {
                "name": i.position_name,
                "id": i.id
            }
        )
    return pos_chd




def get_struct_odata(id: str, pos_list: list) -> list:
    chld = []
    f = False
    for i in pos_list:
        if i.parent_tangl_id == id and (i.parent_tangl_id != i.position_tangl_id):
            pos_list.pop(pos_list.index(i))
            f = True
            chld.append({
                "name": i.position_name,
                "id": i.id,
                "children": get_struct_odata(i.position_tangl_id, pos_list)
            })
        elif i.parent_tangl_id == id and (i.parent_tangl_id == i.position_tangl_id):
            pos_list.pop(pos_list.index(i))
    if not f:
        return []
    else:
        return chld
