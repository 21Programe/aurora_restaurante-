from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.usuario_schema import UsuarioLogin
from backend.services.auth_service import AuthService
from backend.core.security import criar_access_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
def login(payload: UsuarioLogin, db: Session = Depends(get_db)):
    try:
        usuario = AuthService.login(
            db=db,
            email=payload.email,
            senha=payload.senha,
        )
        token = criar_access_token(
            {
                "sub": str(usuario.id),
                "perfil": usuario.perfil,
            }
        )
        return {
            "mensagem": "Login realizado com sucesso",
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": usuario.perfil,
            },
        }
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
