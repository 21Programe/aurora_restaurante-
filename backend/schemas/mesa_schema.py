from pydantic import BaseModel


class MesaBase(BaseModel):
    numero: int
    capacidade: int = 4
    status: str = "livre"


class MesaCreate(BaseModel):
    numero: int
    capacidade: int = 4


class MesaUpdateStatus(BaseModel):
    status: str


class MesaResponse(MesaBase):
    id: int

    class Config:
        from_attributes = True