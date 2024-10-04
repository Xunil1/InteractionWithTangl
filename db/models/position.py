from sqlalchemy import Column, Integer, String, ForeignKey
from db.base_class import Base
from sqlalchemy.orm import relationship


class Position(Base):
    id = Column(Integer, primary_key=True)
    position_name = Column(String, nullable=False)
    position_value = Column(Integer, nullable=False)
    position_tangl_id = Column(String, default="00000000-0000-0000-0000-000000000000")
    parent_tangl_id = Column(String, default="00000000-0000-0000-0000-000000000000")
    catalog_id = Column(Integer, ForeignKey("catalog.id"))
    model_id = Column(Integer, ForeignKey("model.id"))
    catalog = relationship("Catalog", back_populates="position")
    model = relationship("Model", back_populates="position")
    params = relationship("Params", back_populates="position")