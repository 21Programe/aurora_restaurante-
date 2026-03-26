from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.cozinha_service import CozinhaService

router = APIRouter(prefix="/cozinha", tags=["Cozinha"])


@router.get("/pedidos")
def listar_pedidos(
    status: str | None = None,
    setor: str | None = None,
    db: Session = Depends(get_db)
):
    pedidos = CozinhaService.listar_pedidos(db=db, status=status, setor=setor)
    return pedidos


@router.post("/pedido/status")
async def atualizar_status_pedido(
    pedido_id: int,
    novo_status: str,
    db: Session = Depends(get_db)
):
    try:
        pedido = await CozinhaService.atualizar_status_pedido(
            db=db,
            pedido_id=pedido_id,
            novo_status=novo_status
        )
        return {
            "mensagem": "Status do pedido atualizado com sucesso",
            "pedido_id": pedido.id,
            "novo_status": pedido.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))