import datetime

from .database import Base
from sqlalchemy import Column, Integer, String, DateTime


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
