from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models.project import Project as ProjectModel
from db.models.model import Model
from db.models.user import User
from db.models.company import Company
from core.config import Settings
from core.tangl_requests import get_attr
import json
from datetime import datetime, timedelta


def get_project_list(c_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    c_db = db.query(Company).filter(Company.id == c_id).one_or_none()

    try:
        url = Settings.URLS["project_url"] + "/" + str(c_db.company_tangl_id) + "/byCompanyId"
        projects = get_attr(url, user.tangl_token)

        if "error" in projects:
            return {"code": 400, "data": {"status": "RequestError",
                                          "description_en": "The value '" + str(c_db.id) + "' is not valid for id.",
                                          "description_ru": "Компания с ИД '" + str(c_db.id) + "' не существует."}}
    except:
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    if c_db is None:
        return {"code": 400, "data": {"status": "UserCompanyError",
                                      "description_en": "The user is not a member of this company.",
                                      "description_ru": "Пользователь не состоит в данной компании."}}

    for i in projects:
        q = ProjectModel.company_id == c_db.id, ProjectModel.project_tangl_id == i["id"]
        proj = db.query(ProjectModel).filter(*q).one_or_none()

        if proj:
            stmt = (
                update(ProjectModel).
                where(*q).
                values(project_name=i["name"],
                       project_tangl_id=i["id"],
                       folders=json.dumps(i["folders"]),
                       company_id=c_db.id)
            )

            db.execute(stmt)

        else:
            project = ProjectModel(
                project_name=i["name"],
                project_tangl_id=i["id"],
                folders=json.dumps(i["folders"]),
                company_id=c_db.id
            )
            db.add(project)
    db.commit()
    project_list = []
    p = db.query(ProjectModel).filter(ProjectModel.company_id == c_db.id).all()
    for i in p:
        project_list.append({"project_name": i.project_name, "project_id": i.id})

    return project_list


def get_folder_list(p_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()

    if not user or user.last_reg is None or user.last_reg + timedelta(seconds=Settings.TOKEN_EXPIRE) < datetime.now():
        return {"code": 401, "data": {"status": "UserAuthError",
                                      "description_en": "User is not auth or register.",
                                      "description_ru": "Пользователь не авторизован или не зарегистрирован."}}

    main_project = db.query(ProjectModel).filter(ProjectModel.id == p_id).one_or_none()

    if main_project is None:
        return {"code": 400,
                "data": {"status": "RequestError",
                         "description_en": "The value '" + str(p_id) + "' is not valid for id.",
                         "description_ru": "Проект с ИД '" + str(p_id) + "' не существует."}}

    company = db.query(Company).filter(Company.id == main_project.company_id).one_or_none()

    if company.user_id != user.id:
        return {"code": 403,
                "data": {"status": "PermissionError",
                         "description_en": "The user does not have access to this project with '" + str(p_id) + "' id.",
                         "description_ru": "Пользователь не имеет доступа к данному проекту с ИД '" + str(p_id) + "'."}}

    fold = json.loads(main_project.folders)
    models = models_search(fold, [])
    for i in models:
        q = Model.project_id == main_project.id, Model.model_tangl_id == i["id"]

        url = Settings.URLS["model_url"] + "/" + str(i["id"])
        model = get_attr(url, user.tangl_token)
        last_model_version_id = model["versions"][-1]["id"]

        if model:
            stmt = (
                update(Model).
                where(*q).
                values(model_name=i["name"],
                       model_tangl_id=i["id"],
                       model_tangl_version_id=last_model_version_id,
                       project_id=main_project.id)
            )

            db.execute(stmt)

        else:
            m = Model(
                model_name=i["name"],
                model_tangl_id=i["id"],
                model_tangl_version_id=last_model_version_id,
                project_id=main_project.id
            )
            db.add(m)
    db.commit()
    fold = main_project.folders
    m = db.query(Model).filter(Model.project_id == main_project.id).all()
    for i in m:
        fold = fold.replace('\"' + i.model_tangl_id + '\"', str(i.id))
    fold = json.loads(fold)

    return fold


def models_search(folder, model: list):
    if len(folder) > 0:
        for i in folder:
            model.extend(i["models"])
            models_search(i["folders"], model)
        return model
    else:
        return []


def get_model_list(p_id: int, token: str, db: Session):
    user = db.query(User).filter(User.tt_token == token).one_or_none()
    main_project = db.query(ProjectModel).filter(ProjectModel.id == p_id).one_or_none()

    if main_project is None:
        return {"code": 400,
                "data": {"status": "RequestError",
                         "description_en": "The value '" + str(p_id) + "' is not valid for id.",
                         "description_ru": "Проект с ИД '" + str(p_id) + "' не существует."}}

    company = main_project.company
    if company.user_id != user.id:
        return {"code": 403,
                "data": {"status": "PermissionError",
                         "description_en": "The user does not have access to this model with '" + str(p_id) + "' id.",
                         "description_ru": "Пользователь не имеет доступа к данной модели с ИД '" + str(p_id) + "'."}}

    models = db.query(Model).filter(Model.project_id == main_project.id).all()
    models_list = list()
    for i in models:
        models_list.append({
            "name": i.model_name,
            "id": i.id,
            "version": i.version
        })

    return models_list
