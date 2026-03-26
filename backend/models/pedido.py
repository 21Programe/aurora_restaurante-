from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    comanda_id = Column(Integer, ForeignKey("comandas.id"), nullable=False)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    garcom_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    setor_destino = Column(String, nullable=False) # cozinha | bar
    status = Column(String, default="enviado")
    criado_em = Column(DateTime, default=datetime.utcnow)