from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.fechamento_service import FechamentoService

router = APIRouter(prefix="/fechamento", tags=["Fechamento"])


@router.get("/resumo")
def resumo_comanda(comanda_id: int, db: Session = Depends(get_db)):
    try:
        return FechamentoService.resumo_comanda(db, comanda_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ajustar")
async def aplicar_ajustes(
    comanda_id: int,
    taxa_servico: float = 0.0,
    desconto: float = 0.0,
    db: Session = Depends(get_db)
):
    try:
        comanda = await FechamentoService.aplicar_ajustes(
            db=db,
            comanda_id=comanda_id,
            taxa_servico=taxa_servico,
            desconto=desconto
        )
        return {
            "mensagem": "Ajustes aplicados com sucesso",
            "comanda_id": comanda.id,
            "total": comanda.total
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/fechar")
async def fechar_comanda(
    comanda_id: int,
    forma_pagamento: str = "dinheiro",
    db: Session = Depends(get_db)
):
    try:
        resultado = await FechamentoService.fechar_comanda(
            db=db,
            comanda_id=comanda_id,
            forma_pagamento=forma_pagamento
        )
        return {
            "mensagem": "Comanda fechada com sucesso",
            "resultado": resultado
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))