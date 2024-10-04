from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from db.base_class import Base
from sqlalchemy.orm import relationship
from db.models.project import Project


class Company(Base):
    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    company_tangl_id = Column(String, nullable=False)
    is_personal = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="company")
    project = relationship("Project", back_populates="company")