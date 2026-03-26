from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.usuario import Usuario
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("/")
def criar_usuario(
    nome: str,
    email: str,
    senha: str,
    perfil: str = "garcom",
    db: Session = Depends(get_db)
):
    try:
        usuario = AuthService.criar_usuario(
            db=db,
            nome=nome,
            email=email,
            senha=senha,
            perfil=perfil
        )
        return {
            "mensagem": "Usuário criado com sucesso",
            "usuario_id": usuario.id,
            "perfil": usuario.perfil
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios