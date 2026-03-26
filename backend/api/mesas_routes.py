from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.mesa import Mesa

router = APIRouter(prefix="/mesas", tags=["Mesas"])

# ROTA PARA CRIAR MESA (POST)
@router.post("/")
def criar_mesa(numero: int, capacidade: int = 4, db: Session = Depends(get_db)):
    existente = db.query(Mesa).filter(Mesa.numero == numero).first()
    if existente:
        raise HTTPException(status_code=400, detail="Já existe uma mesa com esse número")

    mesa = Mesa(numero=numero, capacidade=capacidade, status="livre")
    db.add(mesa)
    db.commit()
    db.refresh(mesa)

    return {"mensagem": "Mesa criada com sucesso", "mesa_id": mesa.id}

# ROTA PARA LISTAR TODAS AS MESAS (GET)
@router.get("/")
def listar_mesas(db: Session = Depends(get_db)):
    mesas = db.query(Mesa).all()
    return mesas

# --- NOVA ROTA: ATUALIZAÇÃO MANUAL DE STATUS (PUT) ---
# Use esta rota para destravar mesas (ex: mudar de ocupada para livre)
@router.put("/{numero}/status")
def atualizar_status_manual(numero: int, status: str, db: Session = Depends(get_db)):
    mesa = db.query(Mesa).filter(Mesa.numero == numero).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")
    
    mesa.status = status
    db.commit()
    return {"mensagem": f"Mesa {numero} agora está {status}"}