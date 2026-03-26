from pydantic import BaseModel, EmailStr


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    perfil: str = "garcom"


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str = "garcom"


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        from_attributes = True