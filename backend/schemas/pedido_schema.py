from datetime import datetime
from pydantic import BaseModel


class PedidoItemResponse(BaseModel):
    id: int
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float
    observacao: str | None = None
    setor_destino: str


class PedidoStatusUpdate(BaseModel):
    pedido_id: int
    novo_status: str


class PedidoResponse(BaseModel):
    id: int
    comanda_id: int
    mesa_id: int
    mesa_numero: int
    garcom_id: int
    setor_destino: str
    status: str
    criado_em: datetime
    itens: list[PedidoItemResponse]