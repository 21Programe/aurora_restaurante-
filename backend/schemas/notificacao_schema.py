from datetime import datetime
from pydantic import BaseModel


class NotificacaoBase(BaseModel):
    titulo: str
    mensagem: str
    tipo: str = "info"
    lida: str = "nao"


class NotificacaoCreate(BaseModel):
    usuario_id: int | None = None
    titulo: str
    mensagem: str
    tipo: str = "info"


class NotificacaoResponse(NotificacaoBase):
    id: int
    usuario_id: int | None = None
    criado_em: datetime

    class Config:
        from_attributes = True