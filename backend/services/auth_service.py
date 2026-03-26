from sqlalchemy.orm import Session
from backend.models.usuario import Usuario


class AuthService:
    @staticmethod
    def criar_usuario(
        db: Session,
        nome: str,
        email: str,
        senha: str,
        perfil: str = "garcom"
    ):
        existente = db.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            raise ValueError("Já existe um usuário com esse e-mail")

        usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            perfil=perfil
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario

    @staticmethod
    def login(db: Session, email: str, senha: str):
        usuario = db.query(Usuario).filter(Usuario.email == email).first()

        if not usuario:
            raise ValueError("Usuário não encontrado")

        if usuario.senha != senha:
            raise ValueError("Senha inválida")

        return usuario