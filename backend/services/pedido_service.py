from sqlalchemy.orm import Session

from backend.models.pedido import Pedido
from backend.models.pedido_item import PedidoItem
from backend.models.mesa import Mesa


class PedidoService:
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
    def obter_pedido(db: Session, pedido_id: int):
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            raise ValueError("Pedido não encontrado")

        mesa = db.query(Mesa).filter(Mesa.id == pedido.mesa_id).first()
        itens = db.query(PedidoItem).filter(PedidoItem.pedido_id == pedido.id).all()

        return {
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
        }