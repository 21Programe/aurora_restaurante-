from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.item_comanda import ItemComanda
from backend.models.produto import Produto
from backend.models.comanda import Comanda

router = APIRouter(prefix="/itens-comanda", tags=["Itens da Comanda"])


@router.get("/")
def listar_itens(
    comanda_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(ItemComanda)

    if comanda_id:
        query = query.filter(ItemComanda.comanda_id == comanda_id)

    if status:
        query = query.filter(ItemComanda.status == status)

    itens = query.order_by(ItemComanda.id.desc()).all()

    resultado = []
    for item in itens:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()

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
            "status": item.status
        })

    return resultado


@router.get("/{item_id}")
def obter_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemComanda).filter(ItemComanda.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item da comanda não encontrado")

    produto = db.query(Produto).filter(Produto.id == item.produto_id).first()

    return {
        "id": item.id,
        "comanda_id": item.comanda_id,
        "produto_id": item.produto_id,
        "nome_produto": produto.nome if produto else f"Produto {item.produto_id}",
        "categoria": produto.categoria if produto else None,
        "quantidade": item.quantidade,
        "preco_unitario": item.preco_unitario,
        "subtotal": item.subtotal,
        "observacao": item.observacao,
        "status": item.status
    }


@router.post("/{item_id}/cancelar")
def cancelar_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemComanda).filter(ItemComanda.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if item.status == "entregue":
        raise HTTPException(status_code=400, detail="Item já foi entregue e não pode ser cancelado")

    comanda = db.query(Comanda).filter(Comanda.id == item.comanda_id).first()
    if not comanda:
        raise HTTPException(status_code=404, detail="Comanda não encontrada")

    if item.status != "cancelado":
        comanda.subtotal -= item.subtotal
        comanda.total = comanda.subtotal + comanda.taxa_servico - comanda.desconto

    item.status = "cancelado"

    db.commit()
    db.refresh(item)

    return {
        "mensagem": "Item cancelado com sucesso",
        "item_id": item.id,
        "status": item.status,
        "novo_total_comanda": comanda.total
    }


@router.post("/{item_id}/entregar")
def marcar_item_entregue(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemComanda).filter(ItemComanda.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if item.status == "cancelado":
        raise HTTPException(status_code=400, detail="Item cancelado não pode ser entregue")

    item.status = "entregue"

    db.commit()
    db.refresh(item)

    return {
        "mensagem": "Item marcado como entregue",
        "item_id": item.id,
        "status": item.status
    }