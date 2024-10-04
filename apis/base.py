from fastapi import APIRouter

from apis.v1 import route_user, route_company, route_project, route_model, route_catalog, route_parametrs, route_calculations


api_router = APIRouter()
api_router.include_router(route_user.router, prefix="", tags=["Users"])
api_router.include_router(route_company.router, prefix="", tags=["Companies"])
api_router.include_router(route_project.router, prefix="", tags=["Projects"])
api_router.include_router(route_model.router, prefix="", tags=["Models"])
api_router.include_router(route_catalog.router, prefix="", tags=["Catalogs"])
api_router.include_router(route_parametrs.router, prefix="", tags=["Params"])
api_router.include_router(route_calculations.router, prefix="", tags=["Calculations"])