from pydantic import BaseModel, Json


class ParamsRequest(BaseModel):
    category: str
    project_id: str
    modelID: str


class ParamsResponse(BaseModel):
    params: Json


class ParamsValue(BaseModel):
    value: str