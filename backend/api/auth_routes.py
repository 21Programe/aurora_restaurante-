from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login")
def login(email: str, senha: str, db: Session = Depends(get_db)):
    try:
        usuario = AuthService.login(db=db, email=email, senha=senha)
        return {
            "mensagem": "Login realizado com sucesso",
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": usuario.perfil
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))