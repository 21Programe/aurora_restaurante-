from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.produto import Produto

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.post("/")
def criar_produto(nome: str, categoria: str, preco: float, db: Session = Depends(get_db)):
    existente = db.query(Produto).filter(Produto.nome == nome).first()
    if existente:
        raise HTTPException(status_code=400, detail="Produto já cadastrado")

    produto = Produto(
        nome=nome,
        categoria=categoria,
        preco=preco,
        ativo="sim"
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)

    return {"mensagem": "Produto criado com sucesso", "produto_id": produto.id}


@router.get("/")
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return produtos