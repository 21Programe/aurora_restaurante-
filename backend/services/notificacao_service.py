from sqlalchemy.orm import Session
from backend.models.notificacao import Notificacao
from backend.core.websocket_manager import manager


class NotificacaoService:
    @staticmethod
    async def criar_notificacao(
        db: Session,
        titulo: str,
        mensagem: str,
        tipo: str = "info",
        usuario_id: int | None = None,
        canal_ws: str = "notificacoes"
    ):
        notificacao = Notificacao(
            usuario_id=usuario_id,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            lida="nao"
        )

        db.add(notificacao)
        db.commit()
        db.refresh(notificacao)

        await manager.broadcast(canal_ws, {
            "evento": "notificacao_nova",
            "dados": {
                "id": notificacao.id,
                "titulo": notificacao.titulo,
                "mensagem": notificacao.mensagem,
                "tipo": notificacao.tipo,
                "usuario_id": notificacao.usuario_id
            }
        })

        return notificacao