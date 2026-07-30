from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.security import exigir_perfis
from backend.database import get_db
from backend.models.produto import Produto
from backend.models.usuario import Usuario


router = APIRouter(prefix="/produtos", tags=["Produtos"])
ATIVOS_VALIDOS = {"sim", "nao"}


@router.post("/")
def criar_produto(
    nome: str,
    categoria: str,
    preco: float,
    _usuario: Usuario = Depends(exigir_perfis("gerente")),
    db: Session = Depends(get_db),
):
    if preco < 0:
        raise HTTPException(
            status_code=400,
            detail="O preço não pode ser negativo",
        )

    nome_normalizado = nome.strip()
    existente = (
        db.query(Produto)
        .filter(Produto.nome == nome_normalizado)
        .first()
    )
    if existente:
        raise HTTPException(status_code=400, detail="Produto já cadastrado")

    produto = Produto(
        nome=nome_normalizado,
        categoria=categoria.strip(),
        preco=preco,
        ativo="sim",
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return {
        "mensagem": "Produto criado com sucesso",
        "produto_id": produto.id,
        "produto": produto,
    }


@router.get("/")
def listar_produtos(
    categoria: str | None = None,
    ativo: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Produto)
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    if ativo:
        query = query.filter(Produto.ativo == ativo)
    return query.order_by(Produto.nome.asc()).all()


@router.get("/{produto_id}")
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
):
    produto = db.get(Produto, produto_id)
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
    _usuario: Usuario = Depends(exigir_perfis("gerente")),
    db: Session = Depends(get_db),
):
    ativo_normalizado = ativo.strip().lower()
    if preco < 0:
        raise HTTPException(
            status_code=400,
            detail="O preço não pode ser negativo",
        )
    if ativo_normalizado not in ATIVOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="Situação do produto inválida",
        )

    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.nome = nome.strip()
    produto.categoria = categoria.strip()
    produto.preco = preco
    produto.ativo = ativo_normalizado
    db.commit()
    db.refresh(produto)
    return {"mensagem": "Produto atualizado com sucesso", "produto": produto}


@router.delete("/{produto_id}")
def desativar_produto(
    produto_id: int,
    _usuario: Usuario = Depends(exigir_perfis("gerente")),
    db: Session = Depends(get_db),
):
    produto = db.get(Produto, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.ativo = "nao"
    db.commit()
    db.refresh(produto)
    return {
        "mensagem": "Produto desativado com sucesso",
        "produto_id": produto.id,
        "ativo": produto.ativo,
    }
