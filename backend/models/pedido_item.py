from sqlalchemy import Column, Integer, String, Float, ForeignKey
from backend.database import Base


class PedidoItem(Base):
    __tablename__ = "pedido_itens"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    nome_produto = Column(String, nullable=False)
    quantidade = Column(Integer, default=1)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    observacao = Column(String, nullable=True)
    setor_destino = Column(String, nullable=False)  # cozinha | bar