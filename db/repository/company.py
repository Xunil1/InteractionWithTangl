from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models.company import Company as CompanyModel
from db.models.user import User
from core.config import Settings
from core.tangl_requests import get_attr


def get_company_list(token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()

    try:
        companies = get_attr(Settings.URLS["company_url"], user.tangl_token)
    except:
        return {"code": 401, "data": {"status": "UserAuthError", "description_en": "User is not auth or register.",
                "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    for i in companies:

        q = CompanyModel.user_id == user.id, CompanyModel.company_tangl_id == i["id"]
        comp = db.query(CompanyModel).filter(*q).one_or_none()
        if comp:
            stmt = (
                update(CompanyModel).
                where(*q).
                values(company_name=i["name"],
                       company_tangl_id=i["id"],
                       is_personal=i["isPersonal"],
                       user_id=user.id)
            )

            db.execute(stmt)

        else:
            company = CompanyModel(
                company_name=i["name"],
                company_tangl_id=i["id"],
                is_personal=i["isPersonal"],
                user_id=user.id
            )
            db.add(company)
    db.commit()
    company_list = []
    comps = db.query(CompanyModel).filter(CompanyModel.user_id == user.id).all()
    for i in comps:
        company_list.append({"company_name": i.company_name, "company_id": i.id, "is_personal": i.is_personal})
    return company_list
