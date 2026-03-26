from pydantic import BaseModel


class ProdutoBase(BaseModel):
    nome: str
    categoria: str
    preco: float
    ativo: str = "sim"


class ProdutoCreate(BaseModel):
    nome: str
    categoria: str
    preco: float


class ProdutoResponse(ProdutoBase):
    id: int

    class Config:
        from_attributes = True