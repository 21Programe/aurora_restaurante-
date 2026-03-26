from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    titulo = Column(String, nullable=False)
    mensagem = Column(String, nullable=False)
    tipo = Column(String, default="info")
    lida = Column(String, default="nao")
    criado_em = Column(DateTime, default=datetime.utcnow)