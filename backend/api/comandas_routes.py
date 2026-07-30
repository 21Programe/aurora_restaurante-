from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.security import exigir_perfis
from backend.database import get_db
from backend.models.comanda import Comanda
from backend.models.usuario import Usuario
from backend.services.comanda_service import ComandaService


router = APIRouter(prefix="/comandas", tags=["Comandas"])


@router.post("/abrir")
async def abrir_comanda(
    mesa_id: int,
    usuario: Usuario = Depends(exigir_perfis("garcom", "gerente")),
    db: Session = Depends(get_db),
):
    try:
        comanda = await ComandaService.abrir_comanda(
            db,
            mesa_id,
            usuario.id,
        )
        return {
            "mensagem": "Comanda aberta com sucesso",
            "comanda_id": comanda.id,
            "numero_comanda": comanda.numero_comanda,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/adicionar-item")
async def adicionar_item(
    comanda_id: int,
    produto_id: int,
    quantidade: int = 1,
    observacao: str | None = None,
    db: Session = Depends(get_db),
):
    if quantidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="A quantidade deve ser positiva",
        )

    try:
        item = await ComandaService.adicionar_item(
            db=db,
            comanda_id=comanda_id,
            produto_id=produto_id,
            quantidade=quantidade,
            observacao=observacao,
        )
        return {
            "mensagem": "Item adicionado ao rascunho com sucesso",
            "item_comanda_id": item.id,
            "status": item.status,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{comanda_id}/itens")
def listar_itens_comanda(
    comanda_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return ComandaService.listar_itens_comanda(
            db=db,
            comanda_id=comanda_id,
            status=status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/enviar-pedido")
async def enviar_pedido(
    comanda_id: int,
    db: Session = Depends(get_db),
):
    try:
        resultado = await ComandaService.enviar_pedido(
            db=db,
            comanda_id=comanda_id,
        )
        return {
            "mensagem": "Pedido enviado com sucesso",
            "resultado": resultado,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/")
def listar_comandas(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Comanda)
    if status:
        query = query.filter(Comanda.status == status)
    return query.order_by(Comanda.aberta_em.desc()).all()
