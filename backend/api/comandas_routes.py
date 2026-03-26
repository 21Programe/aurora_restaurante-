from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.comanda_service import ComandaService
from backend.models.comanda import Comanda

router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.post("/abrir")
async def abrir_comanda(mesa_id: int, garcom_id: int, db: Session = Depends(get_db)):
    try:
        comanda = await ComandaService.abrir_comanda(db, mesa_id, garcom_id)
        return {
            "mensagem": "Comanda aberta com sucesso",
            "comanda_id": comanda.id,
            "numero_comanda": comanda.numero_comanda
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/adicionar-item")
async def adicionar_item(
    comanda_id: int,
    produto_id: int,
    quantidade: int = 1,
    observacao: str | None = None,
    db: Session = Depends(get_db)
):
    try:
        item = await ComandaService.adicionar_item(
            db=db,
            comanda_id=comanda_id,
            produto_id=produto_id,
            quantidade=quantidade,
            observacao=observacao
        )

        return {
            "mensagem": "Item adicionado ao rascunho com sucesso",
            "item_comanda_id": item.id,
            "status": item.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{comanda_id}/itens")
def listar_itens_comanda(
    comanda_id: int,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    try:
        itens = ComandaService.listar_itens_comanda(
            db=db,
            comanda_id=comanda_id,
            status=status
        )
        return itens
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/enviar-pedido")
async def enviar_pedido(comanda_id: int, db: Session = Depends(get_db)):
    try:
        resultado = await ComandaService.enviar_pedido(
            db=db,
            comanda_id=comanda_id
        )

        return {
            "mensagem": "Pedido enviado com sucesso",
            "resultado": resultado
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fechar")
async def fechar_comanda(comanda_id: int, db: Session = Depends(get_db)):
    try:
        comanda = await ComandaService.fechar_comanda(db, comanda_id)
        return {
            "mensagem": "Comanda fechada com sucesso",
            "comanda_id": comanda.id,
            "status": comanda.status
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def listar_comandas(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Comanda)

    if status:
        query = query.filter(Comanda.status == status)

    comandas = query.order_by(Comanda.aberta_em.desc()).all()
    return comandas