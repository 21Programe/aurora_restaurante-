from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.mesa import Mesa
from backend.models.comanda import Comanda
from backend.models.produto import Produto
from backend.models.item_comanda import ItemComanda
from backend.models.pedido import Pedido
from backend.core.websocket_manager import manager


class ComandaService:
    @staticmethod
    async def abrir_comanda(db: Session, mesa_id: int, garcom_id: int):
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if not mesa:
            raise ValueError("Mesa não encontrada")

        if mesa.status != "livre":
            raise ValueError("Mesa não está livre")

        numero_comanda = f"CMD-{mesa_id}-{garcom_id}-{int(datetime.utcnow().timestamp())}"

        nova_comanda = Comanda(
            numero_comanda=numero_comanda,
            mesa_id=mesa_id,
            garcom_id=garcom_id,
            status="aberta",
            subtotal=0.0,
            taxa_servico=0.0,
            desconto=0.0,
            total=0.0
        )

        mesa.status = "ocupada"

        db.add(nova_comanda)
        db.commit()
        db.refresh(nova_comanda)

        await manager.broadcast("mesas", {
            "evento": "mesa_aberta",
            "dados": {
                "mesa_id": mesa.id,
                "status": mesa.status,
                "comanda_id": nova_comanda.id
            }
        })

        return nova_comanda

    @staticmethod
    async def adicionar_item(
        db: Session,
        comanda_id: int,
        produto_id: int,
        quantidade: int,
        observacao: str | None = None
    ):
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if not comanda:
            raise ValueError("Comanda não encontrada")

        produto = db.query(Produto).filter(Produto.id == produto_id).first()
        if not produto:
            raise ValueError("Produto não encontrado")

        subtotal_item = produto.preco * quantidade

        item = ItemComanda(
            comanda_id=comanda.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal_item,
            observacao=observacao,
            status="pendente"
        )

        db.add(item)

        pedido = Pedido(
            comanda_id=comanda.id,
            mesa_id=comanda.mesa_id,
            setor_destino="cozinha" if produto.categoria != "bebida" else "bar",
            status="enviado"
        )
        db.add(pedido)

        comanda.subtotal += subtotal_item
        comanda.total = comanda.subtotal + comanda.taxa_servico - comanda.desconto

        db.commit()
        db.refresh(item)

        await manager.broadcast("cozinha", {
            "evento": "pedido_criado",
            "dados": {
                "comanda_id": comanda.id,
                "mesa_id": comanda.mesa_id,
                "produto": produto.nome,
                "quantidade": quantidade,
                "observacao": observacao,
                "setor_destino": pedido.setor_destino
            }
        })

        await manager.broadcast("mesas", {
            "evento": "item_adicionado",
            "dados": {
                "comanda_id": comanda.id,
                "mesa_id": comanda.mesa_id,
                "produto": produto.nome,
                "quantidade": quantidade,
                "novo_total": comanda.total
            }
        })

        return item

    @staticmethod
    async def fechar_comanda(db: Session, comanda_id: int):
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if not comanda:
            raise ValueError("Comanda não encontrada")

        mesa = db.query(Mesa).filter(Mesa.id == comanda.mesa_id).first()
        if not mesa:
            raise ValueError("Mesa não encontrada")

        comanda.status = "fechada"
        comanda.fechada_em = datetime.utcnow()

        mesa.status = "livre"

        db.commit()

        await manager.broadcast("mesas", {
            "evento": "mesa_fechada",
            "dados": {
                "mesa_id": mesa.id,
                "comanda_id": comanda.id,
                "status_mesa": mesa.status
            }
        })

        return comanda