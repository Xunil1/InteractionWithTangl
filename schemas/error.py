from pydantic import BaseModel


class BaseError(BaseModel):
    status: str
    description_en: str
    description_ru: str
