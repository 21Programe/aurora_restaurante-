from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.usuario import Usuario
from backend.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/", response_model=dict)
def criar_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
):
    try:
        usuario = AuthService.criar_usuario(
            db=db,
            nome=payload.nome,
            email=payload.email,
            senha=payload.senha,
            perfil=payload.perfil,
        )
        return {
            "mensagem": "Usuário criado com sucesso",
            "usuario_id": usuario.id,
            "perfil": usuario.perfil,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()
