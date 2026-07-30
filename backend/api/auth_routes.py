from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.security import criar_access_token, get_current_user
from backend.database import get_db
from backend.models.usuario import Usuario
from backend.schemas.usuario_schema import (
    TokenResponse,
    UsuarioCreate,
    UsuarioLogin,
    UsuarioResponse,
)
from backend.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/bootstrap",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_primeiro_gerente(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
):
    if db.query(Usuario).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A configuração inicial já foi concluída",
        )

    try:
        return AuthService.criar_usuario(
            db=db,
            nome=dados.nome,
            email=str(dados.email),
            senha=dados.senha,
            perfil="gerente",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(
    dados: UsuarioLogin,
    db: Session = Depends(get_db),
):
    try:
        usuario = AuthService.login(
            db=db,
            email=str(dados.email),
            senha=dados.senha,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token = criar_access_token(
        {
            "sub": str(usuario.id),
            "perfil": usuario.perfil,
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "usuario": usuario,
    }


@router.get("/me", response_model=UsuarioResponse)
def obter_sessao(
    usuario: Usuario = Depends(get_current_user),
):
    return usuario
