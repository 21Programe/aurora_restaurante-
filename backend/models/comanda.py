from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base


class Comanda(Base):
    __tablename__ = "comandas"

    id = Column(Integer, primary_key=True, index=True)
    numero_comanda = Column(String, unique=True, nullable=False)
    mesa_id = Column(Integer, ForeignKey("mesas.id"), nullable=False)
    garcom_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(String, default="aberta")
    subtotal = Column(Float, default=0.0)
    taxa_servico = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    aberta_em = Column(DateTime, default=datetime.utcnow)
    fechada_em = Column(DateTime, nullable=True)