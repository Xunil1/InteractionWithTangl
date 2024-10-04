from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from db.base_class import Base
from sqlalchemy.orm import relationship
from db.models.model import Model


class Project(Base):
    id = Column(Integer, primary_key=True)
    project_name = Column(String, nullable=False)
    project_tangl_id = Column(String, nullable=False)
    folders = Column(JSON, nullable=False)
    company_id = Column(Integer, ForeignKey("company.id"))
    company = relationship("Company", back_populates="project")
    model = relationship("Model", back_populates="project")
