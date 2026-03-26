from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.mesa import Mesa
from backend.models.comanda import Comanda
from backend.models.produto import Produto
from backend.models.item_comanda import ItemComanda
from backend.models.pedido import Pedido
from backend.models.pedido_item import PedidoItem
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
                "mesa_numero": mesa.numero,
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

        mesa = db.query(Mesa).filter(Mesa.id == comanda.mesa_id).first()
        if not mesa:
            raise ValueError("Mesa não encontrada")

        subtotal_item = produto.preco * quantidade

        item_comanda = ItemComanda(
            comanda_id=comanda.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal_item,
            observacao=observacao,
            status="rascunho"
        )

        db.add(item_comanda)

        comanda.subtotal += subtotal_item
        comanda.total = comanda.subtotal + comanda.taxa_servico - comanda.desconto

        db.commit()
        db.refresh(item_comanda)

        await manager.broadcast("mesas", {
            "evento": "item_rascunho_adicionado",
            "dados": {
                "comanda_id": comanda.id,
                "mesa_id": comanda.mesa_id,
                "mesa_numero": mesa.numero,
                "produto_id": produto.id,
                "produto": produto.nome,
                "quantidade": quantidade,
                "observacao": observacao,
                "subtotal": subtotal_item,
                "novo_total": comanda.total,
                "status_item": item_comanda.status
            }
        })

        return item_comanda

    @staticmethod
    def listar_itens_comanda(db: Session, comanda_id: int, status: str | None = None):
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if not comanda:
            raise ValueError("Comanda não encontrada")

        query = db.query(ItemComanda).filter(ItemComanda.comanda_id == comanda_id)

        if status:
            query = query.filter(ItemComanda.status == status)

        itens = query.order_by(ItemComanda.id.desc()).all()

        resultado = []
        for item in itens:
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            setor_destino = "bar" if produto and produto.categoria.lower() == "bebida" else "cozinha"

            resultado.append({
                "id": item.id,
                "comanda_id": item.comanda_id,
                "produto_id": item.produto_id,
                "nome_produto": produto.nome if produto else f"Produto {item.produto_id}",
                "categoria": produto.categoria if produto else None,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario,
                "subtotal": item.subtotal,
                "observacao": item.observacao,
                "status": item.status,
                "setor_destino": setor_destino
            })

        return resultado

    @staticmethod
    async def enviar_pedido(db: Session, comanda_id: int):
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if not comanda:
            raise ValueError("Comanda não encontrada")

        mesa = db.query(Mesa).filter(Mesa.id == comanda.mesa_id).first()
        if not mesa:
            raise ValueError("Mesa não encontrada")

        itens_rascunho = db.query(ItemComanda).filter(
            ItemComanda.comanda_id == comanda_id,
            ItemComanda.status == "rascunho"
        ).all()

        if not itens_rascunho:
            raise ValueError("Não há itens em rascunho para enviar")

        itens_por_setor = {
            "cozinha": [],
            "bar": []
        }

        for item in itens_rascunho:
            produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
            if not produto:
                continue

            setor_destino = "bar" if produto.categoria.lower() == "bebida" else "cozinha"

            itens_por_setor[setor_destino].append({
                "item_comanda": item,
                "produto": produto
            })

        pedidos_criados = []

        for setor, itens_setor in itens_por_setor.items():
            if not itens_setor:
                continue

            pedido = Pedido(
                comanda_id=comanda.id,
                mesa_id=comanda.mesa_id,
                garcom_id=comanda.garcom_id,
                setor_destino=setor,
                status="enviado"
            )
            db.add(pedido)
            db.commit()
            db.refresh(pedido)

            itens_payload = []

            for registro in itens_setor:
                item = registro["item_comanda"]
                produto = registro["produto"]

                pedido_item = PedidoItem(
                    pedido_id=pedido.id,
                    produto_id=produto.id,
                    nome_produto=produto.nome,
                    quantidade=item.quantidade,
                    preco_unitario=item.preco_unitario,
                    subtotal=item.subtotal,
                    observacao=item.observacao,
                    setor_destino=setor
                )
                db.add(pedido_item)

                item.status = "enviado"

                itens_payload.append({
                    "item_comanda_id": item.id,
                    "produto": produto.nome,
                    "quantidade": item.quantidade,
                    "observacao": item.observacao,
                    "subtotal": item.subtotal
                })

            db.commit()

            pedidos_criados.append({
                "pedido_id": pedido.id,
                "setor": setor,
                "itens": itens_payload
            })

            await manager.broadcast(setor, {
                "evento": "pedido_criado",
                "dados": {
                    "pedido_id": pedido.id,
                    "comanda_id": comanda.id,
                    "mesa_id": mesa.id,
                    "mesa_numero": mesa.numero,
                    "garcom_id": comanda.garcom_id,
                    "setor_destino": setor,
                    "status": "enviado",
                    "itens": itens_payload
                }
            })

        mesa.status = "aguardando_preparo"
        db.commit()

        await manager.broadcast("mesas", {
            "evento": "pedido_enviado",
            "dados": {
                "comanda_id": comanda.id,
                "mesa_id": mesa.id,
                "mesa_numero": mesa.numero,
                "status_mesa": mesa.status,
                "pedidos_criados": pedidos_criados
            }
        })

        return {
            "comanda_id": comanda.id,
            "mesa_id": mesa.id,
            "mesa_numero": mesa.numero,
            "pedidos_criados": pedidos_criados
        }

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
                "mesa_numero": mesa.numero,
                "comanda_id": comanda.id,
                "status_mesa": mesa.status
            }
        })

        return comanda