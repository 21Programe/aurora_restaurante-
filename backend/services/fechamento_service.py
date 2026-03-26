from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.comanda import Comanda
from backend.models.mesa import Mesa
from backend.models.item_comanda import ItemComanda
from backend.core.websocket_manager import manager


class FechamentoService:
    @staticmethod
    def resumo_comanda(db: Session, comanda_id: int):
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if not comanda:
            raise ValueError("Comanda não encontrada")

        mesa = db.query(Mesa).filter(Mesa.id == comanda.mesa_id).first()
        itens = db.query(ItemComanda).filter(ItemComanda.comanda_id == comanda.id).all()

        return {
            "comanda_id": comanda.id,
            "numero_comanda": comanda.numero_comanda,
            "mesa_id": comanda.mesa_id,
            "mesa_numero": mesa.numero if mesa else comanda.mesa_id,
            "status": comanda.status,
            "subtotal": comanda.subtotal,
            "taxa_servico": comanda.taxa_servico,
            "desconto": comanda.desconto,
            "total": comanda.total,
            "aberta_em": comanda.aberta_em,
            "fechada_em": comanda.fechada_em,
            "quantidade_itens": len(itens)
        }

    @staticmethod
    async def aplicar_ajustes(
        db: Session,
        comanda_id: int,
        taxa_servico: float = 0.0,
        desconto: float = 0.0
    ):
        comanda = db.query(Comanda).filter(Comanda.id == comanda_id).first()
        if not comanda:
            raise ValueError("Comanda não encontrada")

        comanda.taxa_servico = taxa_servico
        comanda.desconto = desconto
        comanda.total = comanda.subtotal + taxa_servico - desconto

        db.commit()
        db.refresh(comanda)

        await manager.broadcast("caixa", {
            "evento": "comanda_atualizada",
            "dados": {
                "comanda_id": comanda.id,
                "subtotal": comanda.subtotal,
                "taxa_servico": comanda.taxa_servico,
                "desconto": comanda.desconto,
                "total": comanda.total
            }
        })

        return comanda

    @staticmethod
    async def fechar_comanda(
        db: Session,
        comanda_id: int,
        forma_pagamento: str = "dinheiro"
    ):
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

        await manager.broadcast("caixa", {
            "evento": "comanda_fechada",
            "dados": {
                "comanda_id": comanda.id,
                "forma_pagamento": forma_pagamento,
                "total": comanda.total
            }
        })

        await manager.broadcast("mesas", {
            "evento": "mesa_liberada",
            "dados": {
                "mesa_id": mesa.id,
                "mesa_numero": mesa.numero,
                "status": mesa.status
            }
        })

        return {
            "comanda_id": comanda.id,
            "mesa_id": mesa.id,
            "mesa_numero": mesa.numero,
            "forma_pagamento": forma_pagamento,
            "total_pago": comanda.total,
            "status_comanda": comanda.status
        }