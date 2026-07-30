from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.security import exigir_perfis
from backend.database import get_db
from backend.models.mesa import Mesa
from backend.models.usuario import Usuario


router = APIRouter(prefix="/mesas", tags=["Mesas"])
STATUS_VALIDOS = {
    "livre",
    "ocupada",
    "aguardando_preparo",
    "pedido_em_preparo",
    "pronta_para_servir",
}


@router.post("/")
def criar_mesa(
    numero: int,
    capacidade: int = 4,
    _usuario: Usuario = Depends(exigir_perfis("gerente")),
    db: Session = Depends(get_db),
):
    if numero <= 0 or capacidade <= 0:
        raise HTTPException(
            status_code=400,
            detail="Número e capacidade devem ser positivos",
        )

    existente = db.query(Mesa).filter(Mesa.numero == numero).first()
    if existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe uma mesa com esse número",
        )

    mesa = Mesa(numero=numero, capacidade=capacidade, status="livre")
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return {"mensagem": "Mesa criada com sucesso", "mesa_id": mesa.id}


@router.get("/")
def listar_mesas(db: Session = Depends(get_db)):
    return db.query(Mesa).order_by(Mesa.numero.asc()).all()


@router.put("/{numero}/status")
def atualizar_status_manual(
    numero: int,
    status: str,
    _usuario: Usuario = Depends(exigir_perfis("gerente")),
    db: Session = Depends(get_db),
):
    status_normalizado = status.strip().lower()
    if status_normalizado not in STATUS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="Status de mesa inválido",
        )

    mesa = db.query(Mesa).filter(Mesa.numero == numero).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    mesa.status = status_normalizado
    db.commit()
    return {
        "mensagem": f"Mesa {numero} agora está {status_normalizado}"
    }
