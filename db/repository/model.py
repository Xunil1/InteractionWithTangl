from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models.catalog import Catalog
from db.models.model import Model
from db.models.user import User
from core.config import Settings
from core.tangl_requests import get_attr
import json


def get_catalog_list(m_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    m_db = db.query(Model).filter(Model.id == m_id).one_or_none()

    if m_db is None:
        return {"code": 403,
                "data": {"status": "PermissionError",
                         "description_en": "The user does not have access to this model with '" + str(m_id) + "' id.",
                         "description_ru": "Пользователь не имеет доступа к данной модели с ИД '" + str(m_id) + "'."}}

    p_db = m_db.project

    c_db = p_db.company

    try:
        url = Settings.URLS["analaysis_url"] + "/byModel?projId=" + str(p_db.project_tangl_id) + "&modelId=" + str(m_db.model_tangl_id)
        catalogs = get_attr(url, user.tangl_token)
        if not isinstance(catalogs, dict):
            return {"code": 401, "data": {"status": "UserAuthError",
                                          "description_en": "User is not auth or register.",
                                          "description_ru": "Пользователь не авторизован или не зарегистрирован."}}
    except:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    if c_db is None:
        return {"code": 400, "data": {"status": "UserCompanyError",
                                      "description_en": "The user is not a member of this company.",
                                      "description_ru": "Пользователь не состоит в данной компании."}}


    for i in catalogs["catalogPrioritiesSchemes"]:
        q = Catalog.model_id == m_db.id, Catalog.catalog_tangl_id == i["id"]
        ctg = db.query(Catalog).filter(*q).one_or_none()
        if ctg:
            stmt = (
                    update(Catalog).
                    where(*q).
                    values(catalog_name=i["name"],
                           catalog_tangl_id=i["id"],
                           model_id=m_db.id)
                )

            db.execute(stmt)

        else:
            catalog = Catalog(
                catalog_name=i["name"],
                catalog_tangl_id=i["id"],
                model_id=m_db.id
            )
            db.add(catalog)
    db.commit()
    catalog_list = list()
    c = db.query(Catalog).filter(Catalog.model_id == m_db.id).all()
    for i in c:
        catalog_list.append({"catalog_name": i.catalog_name, "catalog_id": i.id})

    return catalog_list