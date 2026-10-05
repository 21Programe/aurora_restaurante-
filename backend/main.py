from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.database import Base, engine

from backend.api.mesas_routes import router as mesas_router
from backend.api.produtos_routes import router as produtos_router
from backend.api.comandas_routes import router as comandas_router
from backend.api.item_comanda_routes import router as item_comanda_router
from backend.api.websocket_routes import router as websocket_router
from backend.api.usuarios_routes import router as usuarios_router
from backend.api.auth_routes import router as auth_router
from backend.api.cozinha_routes import router as cozinha_router
from backend.api.notificacoes_routes import router as notificacoes_router
from backend.api.fechamento_routes import router as fechamento_router

from backend.models.mesa import Mesa
from backend.models.usuario import Usuario
from backend.models.produto import Produto
from backend.models.comanda import Comanda
from backend.models.item_comanda import ItemComanda
from backend.models.pedido import Pedido
from backend.models.pedido_item import PedidoItem
from backend.models.notificacao import Notificacao

settings.validate()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de atendimento, comandas e operação em tempo real.",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

web_dir = Path(__file__).resolve().parent / "web"
app.mount("/web", StaticFiles(directory=web_dir, html=True), name="web")

app.include_router(mesas_router)
app.include_router(produtos_router)
app.include_router(comandas_router)
app.include_router(item_comanda_router)
app.include_router(websocket_router)
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(cozinha_router)
app.include_router(notificacoes_router)
app.include_router(fechamento_router)


@app.get("/")
def root():
    return {
        "status": "online",
        "sistema": settings.APP_NAME,
        "versao": settings.APP_VERSION,
        "modulos": [
            "mesas",
            "comandas",
            "produtos",
            "cozinha",
            "caixa",
            "gerencia",
            "websocket",
        ],
        "docs": "/docs",
    }
