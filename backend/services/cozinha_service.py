from sqlalchemy.orm import Session

from backend.models.pedido import Pedido
from backend.models.pedido_item import PedidoItem
from backend.models.comanda import Comanda
from backend.models.mesa import Mesa
from backend.core.websocket_manager import manager
from backend.services.notificacao_service import NotificacaoService


class CozinhaService:
    @staticmethod
    def listar_pedidos(db: Session, status: str | None = None, setor: str | None = None):
        query = db.query(Pedido)

        if status:
            query = query.filter(Pedido.status == status)

        if setor:
            query = query.filter(Pedido.setor_destino == setor)

        pedidos = query.order_by(Pedido.criado_em.desc()).all()

        resultado = []
        for pedido in pedidos:
            mesa = db.query(Mesa).filter(Mesa.id == pedido.mesa_id).first()
            itens = db.query(PedidoItem).filter(PedidoItem.pedido_id == pedido.id).all()

            resultado.append({
                "id": pedido.id,
                "comanda_id": pedido.comanda_id,
                "mesa_id": pedido.mesa_id,
                "mesa_numero": mesa.numero if mesa else pedido.mesa_id,
                "garcom_id": pedido.garcom_id,
                "setor_destino": pedido.setor_destino,
                "status": pedido.status,
                "criado_em": pedido.criado_em,
                "itens": [
                    {
                        "id": item.id,
                        "produto_id": item.produto_id,
                        "nome_produto": item.nome_produto,
                        "quantidade": item.quantidade,
                        "preco_unitario": item.preco_unitario,
                        "subtotal": item.subtotal,
                        "observacao": item.observacao,
                        "setor_destino": item.setor_destino
                    }
                    for item in itens
                ]
            })

        return resultado

    @staticmethod
    async def atualizar_status_pedido(db: Session, pedido_id: int, novo_status: str):
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido não encontrado")

        pedido.status = novo_status

        comanda = db.query(Comanda).filter(Comanda.id == pedido.comanda_id).first()
        mesa = db.query(Mesa).filter(Mesa.id == pedido.mesa_id).first()

        if not comanda or not mesa:
            raise ValueError("Comanda ou mesa não encontrada")

        if novo_status == "em_preparo":
            mesa.status = "pedido_em_preparo"
        elif novo_status == "pronto":
            mesa.status = "pronta_para_servir"
        elif novo_status == "entregue":
            mesa.status = "ocupada"

        db.commit()
        db.refresh(pedido)

        await manager.broadcast(pedido.setor_destino, {
            "evento": "pedido_status_atualizado",
            "dados": {
                "pedido_id": pedido.id,
                "mesa_id": pedido.mesa_id,
                "mesa_numero": mesa.numero,
                "comanda_id": pedido.comanda_id,
                "novo_status": pedido.status
            }
        })

        await manager.broadcast("mesas", {
            "evento": "mesa_status_atualizado",
            "dados": {
                "mesa_id": mesa.id,
                "mesa_numero": mesa.numero,
                "status": mesa.status
            }
        })

        if novo_status == "pronto":
            await NotificacaoService.criar_notificacao(
                db=db,
                titulo="Pedido pronto",
                mensagem=f"Pedido da mesa {mesa.numero} está pronto para retirada.",
                tipo="sucesso",
                canal_ws="notificacoes"
            )

        return pedido