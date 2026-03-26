from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.notificacao import Notificacao

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("/")
def listar_notificacoes(db: Session = Depends(get_db)):
    notificacoes = db.query(Notificacao).order_by(Notificacao.criado_em.desc()).all()
    return notificacoes