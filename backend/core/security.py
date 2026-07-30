from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database import get_db
from backend.models.usuario import Usuario


pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated=["bcrypt"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    try:
        return pwd_context.verify(senha_plain, senha_hash)
    except (TypeError, ValueError):
        return False


def senha_esta_hasheada(senha: str) -> bool:
    try:
        return pwd_context.identify(senha) is not None
    except (TypeError, ValueError):
        return False


def criar_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def _credenciais_invalidas() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )


def obter_usuario_por_token(token: str, db: Session) -> Usuario:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        usuario_id = int(payload.get("sub", ""))
    except (JWTError, TypeError, ValueError):
        raise _credenciais_invalidas()

    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise _credenciais_invalidas()
    return usuario


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    return obter_usuario_por_token(token, db)


def exigir_perfis(*perfis: str) -> Callable:
    perfis_permitidos = set(perfis)

    def dependencia(
        usuario: Usuario = Depends(get_current_user),
    ) -> Usuario:
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário sem permissão para esta operação",
            )
        return usuario

    return dependencia
