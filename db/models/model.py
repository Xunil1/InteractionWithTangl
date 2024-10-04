from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Boolean
from db.base_class import Base
from sqlalchemy.orm import relationship
from db.models.catalog import Catalog
from db.models.position import Position
from db.models.parametrs import Params


class Model(Base):
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    model_tangl_id = Column(String, nullable=False)
    model_tangl_version_id = Column(String, nullable=True)
    version = Column(String, default="new")
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="model")
    catalog = relationship("Catalog", back_populates="model")
    position = relationship("Position", back_populates="model")
    params = relationship("Params", back_populates="model")
