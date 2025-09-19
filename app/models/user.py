from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, func
from app.models.db import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), unique=False, nullable=True)
    name = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)