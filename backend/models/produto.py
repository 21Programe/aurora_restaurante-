from sqlalchemy import Column, Integer, String, Float
from backend.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False)  # bebida, lanche, sobremesa, prato
    preco = Column(Float, nullable=False)
    ativo = Column(String, default="sim")