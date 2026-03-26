from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import Base, engine

# IMPORTS DE ROTAS
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

# IMPORT DOS MODELS (IMPORTANTE PRA CRIAR AS TABELAS)
from backend.models.mesa import Mesa
from backend.models.usuario import Usuario
from backend.models.produto import Produto
from backend.models.comanda import Comanda
from backend.models.item_comanda import ItemComanda
from backend.models.pedido import Pedido
from backend.models.pedido_item import PedidoItem
from backend.models.notificacao import Notificacao

# CRIA TABELAS
Base.metadata.create_all(bind=engine)

# APP
app = FastAPI(
    title="Aurora Restaurante API",
    description="Sistema completo de atendimento de mesas, comandas e operação em tempo real",
    version="2.0.0"
)

# CORS (libera tudo no dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SERVIR FRONTENDS (HTML)
app.mount("/web", StaticFiles(directory="backend/web", html=True), name="web")

# REGISTRO DAS ROTAS
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

# ROOT
@app.get("/")
def root():
    return {
        "status": "online",
        "sistema": "Aurora Restaurante",
        "versao": "2.0.0",
        "modulos": [
            "mesas",
            "comandas",
            "produtos",
            "cozinha",
            "caixa",
            "gerencia",
            "websocket"
        ],
        "painel_cozinha": "http://127.0.0.1:8000/web/cozinha.html",
        "painel_caixa": "http://127.0.0.1:8000/web/caixa.html",
        "painel_gerencia": "http://127.0.0.1:8000/web/gerencia.html"
    }