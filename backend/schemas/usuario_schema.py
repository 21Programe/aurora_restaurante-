from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


PerfilUsuario = Literal["garcom", "caixa", "cozinha", "gerente"]


class UsuarioBase(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    perfil: PerfilUsuario = "garcom"


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=8, max_length=128)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class UsuarioResponse(UsuarioBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    usuario: UsuarioResponse
