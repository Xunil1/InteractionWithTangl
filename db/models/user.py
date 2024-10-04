from sqlalchemy import Column, Integer, String, DateTime
from db.base_class import Base
from sqlalchemy.orm import relationship
from db.models.company import Company
from datetime import datetime as dt


class User(Base):
    id = Column(Integer, primary_key=True)
    tangl_token = Column(String, nullable=False)
    tt_token = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    hash_password = Column(String, nullable=False)
    last_reg = Column(DateTime, default=dt.now())
    company = relationship("Company", back_populates="user")
