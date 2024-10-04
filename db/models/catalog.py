from sqlalchemy import Column, Integer, String, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship
from db.models.position import Position


class Catalog(Base):
    id = Column(Integer, primary_key=True)
    catalog_name = Column(String, nullable=False)
    catalog_tangl_id = Column(String, nullable=False)
    model_id = Column(Integer, ForeignKey("model.id"))
    model = relationship("Model", back_populates="catalog")
    position = relationship("Position", back_populates="catalog")
