from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.security import exigir_perfis
from backend.database import get_db
from backend.models.usuario import Usuario
from backend.schemas.usuario_schema import UsuarioCreate, UsuarioResponse
from backend.services.auth_service import AuthService


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
    dependencies=[Depends(exigir_perfis("gerente"))],
)


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
):
    try:
        return AuthService.criar_usuario(
            db=db,
            nome=dados.nome,
            email=str(dados.email),
            senha=dados.senha,
            perfil=dados.perfil,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).order_by(Usuario.nome.asc()).all()
