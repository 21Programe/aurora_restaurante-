from sqlalchemy import Column, Integer, String
from backend.database import Base


class Mesa(Base):
    __tablename__ = "mesas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, unique=True, nullable=False)
    capacidade = Column(Integer, default=4)
    status = Column(String, default="livre")