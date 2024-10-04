from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from db.base_class import Base
from sqlalchemy.orm import relationship


class Params(Base):
    id = Column(Integer, primary_key=True)
    el_num = Column(Integer, nullable=False)
    el_name = Column(String, nullable=False)
    el_type = Column(String, nullable=False)
    el_category = Column(String, nullable=False)
    el_id = Column(String, nullable=False)
    param = Column(JSON, nullable=False)
    model_version = Column(String, default="new")
    model_id = Column(Integer, ForeignKey("model.id"))
    position_parent_id = Column(Integer, ForeignKey("position.id"))
    model = relationship("Model", back_populates="params")
    position = relationship("Position", back_populates="params")

