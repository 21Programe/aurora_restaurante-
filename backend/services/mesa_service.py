from sqlalchemy.orm import Session
from backend.models.mesa import Mesa
from backend.core.websocket_manager import manager


class MesaService:
    @staticmethod
    async def criar_mesa(db: Session, numero: int, capacidade: int = 4):
        existente = db.query(Mesa).filter(Mesa.numero == numero).first()
        if existente:
            raise ValueError("Já existe uma mesa com esse número")

        mesa = Mesa(numero=numero, capacidade=capacidade, status="livre")
        db.add(mesa)
        db.commit()
        db.refresh(mesa)

        await manager.broadcast("mesas", {
            "evento": "mesa_criada",
            "dados": {
                "mesa_id": mesa.id,
                "mesa_numero": mesa.numero,
                "capacidade": mesa.capacidade,
                "status": mesa.status
            }
        })

        return mesa

    @staticmethod
    def listar_mesas(db: Session, status: str | None = None):
        query = db.query(Mesa)

        if status:
            query = query.filter(Mesa.status == status)

        return query.order_by(Mesa.numero.asc()).all()

    @staticmethod
    async def atualizar_status(db: Session, mesa_id: int, novo_status: str):
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if not mesa:
            raise ValueError("Mesa não encontrada")

        mesa.status = novo_status
        db.commit()
        db.refresh(mesa)

        await manager.broadcast("mesas", {
            "evento": "mesa_status_atualizado",
            "dados": {
                "mesa_id": mesa.id,
                "mesa_numero": mesa.numero,
                "status": mesa.status
            }
        })

        return mesa