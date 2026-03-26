from sqlalchemy import Column, Integer, Float, String, ForeignKey
from backend.database import Base


class ItemComanda(Base):
    __tablename__ = "itens_comanda"

    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, default=1)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    observacao = Column(String, nullable=True)
    status = Column(String, default="rascunho")  # rascunho | enviado | cancelado | entregue