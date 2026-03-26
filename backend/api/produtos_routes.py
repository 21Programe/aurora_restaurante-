from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.produto import Produto

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.post("/")
def criar_produto(
    nome: str,
    categoria: str,
    preco: float,
    db: Session = Depends(get_db)
):
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

    return {
        "mensagem": "Produto criado com sucesso",
        "produto_id": produto.id,
        "produto": {
            "id": produto.id,
            "nome": produto.nome,
            "categoria": produto.categoria,
            "preco": produto.preco,
            "ativo": produto.ativo
        }
    }


@router.get("/")
def listar_produtos(
    categoria: str | None = None,
    ativo: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Produto)

    if categoria:
        query = query.filter(Produto.categoria == categoria)

    if ativo:
        query = query.filter(Produto.ativo == ativo)

    produtos = query.order_by(Produto.nome.asc()).all()
    return produtos


@router.get("/{produto_id}")
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return produto


@router.put("/{produto_id}")
def atualizar_produto(
    produto_id: int,
    nome: str,
    categoria: str,
    preco: float,
    ativo: str = "sim",
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.nome = nome
    produto.categoria = categoria
    produto.preco = preco
    produto.ativo = ativo

    db.commit()
    db.refresh(produto)

    return {
        "mensagem": "Produto atualizado com sucesso",
        "produto": produto
    }


@router.delete("/{produto_id}")
def desativar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.ativo = "nao"
    db.commit()
    db.refresh(produto)

    return {
        "mensagem": "Produto desativado com sucesso",
        "produto_id": produto.id,
        "ativo": produto.ativo
    }