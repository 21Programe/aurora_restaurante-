from hmac import compare_digest

from sqlalchemy.orm import Session

from backend.core.security import (
    gerar_hash_senha,
    senha_esta_hasheada,
    verificar_senha,
)
from backend.models.usuario import Usuario


PERFIS_VALIDOS = {"garcom", "caixa", "cozinha", "gerente"}


class AuthService:
    @staticmethod
    def criar_usuario(
        db: Session,
        nome: str,
        email: str,
        senha: str,
        perfil: str = "garcom",
    ) -> Usuario:
        email_normalizado = email.strip().lower()
        perfil_normalizado = perfil.strip().lower()

        if perfil_normalizado not in PERFIS_VALIDOS:
            raise ValueError("Perfil de usuário inválido")

        existente = (
            db.query(Usuario)
            .filter(Usuario.email == email_normalizado)
            .first()
        )
        if existente:
            raise ValueError("E-mail já cadastrado")

        usuario = Usuario(
            nome=nome.strip(),
            email=email_normalizado,
            senha=gerar_hash_senha(senha),
            perfil=perfil_normalizado,
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def login(db: Session, email: str, senha: str) -> Usuario:
        email_normalizado = email.strip().lower()
        usuario = (
            db.query(Usuario)
            .filter(Usuario.email == email_normalizado)
            .first()
        )

        if usuario is None:
            raise ValueError("Credenciais inválidas")

        if senha_esta_hasheada(usuario.senha):
            senha_valida = verificar_senha(senha, usuario.senha)
        else:
            # Migração compatível: uma senha legada em texto puro é
            # convertida para hash somente após um login válido.
            senha_valida = compare_digest(usuario.senha, senha)
            if senha_valida:
                usuario.senha = gerar_hash_senha(senha)
                db.commit()

        if not senha_valida:
            raise ValueError("Credenciais inválidas")

        return usuario
