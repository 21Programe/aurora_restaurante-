from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.auth_routes import router as auth_router
from backend.api.cozinha_routes import router as cozinha_router
from backend.api.comandas_routes import router as comandas_router
from backend.api.fechamento_routes import router as fechamento_router
from backend.api.item_comanda_routes import router as item_comanda_router
from backend.api.mesas_routes import router as mesas_router
from backend.api.notificacoes_routes import router as notificacoes_router
from backend.api.produtos_routes import router as produtos_router
from backend.api.usuarios_routes import router as usuarios_router
from backend.api.websocket_routes import router as websocket_router
from backend.core.config import settings
from backend.core.security import exigir_perfis, get_current_user
from backend.database import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Sistema completo de gestão de restaurante com API, "
        "WebSocket e painel web."
    ),
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_directory = Path(__file__).resolve().parents[1] / "web"
if web_directory.is_dir():
    app.mount(
        "/web",
        StaticFiles(directory=web_directory, html=True),
        name="web",
    )

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(
    mesas_router,
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    produtos_router,
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    comandas_router,
    dependencies=[Depends(exigir_perfis("garcom", "gerente"))],
)
app.include_router(
    item_comanda_router,
    dependencies=[Depends(exigir_perfis("garcom", "gerente"))],
)
app.include_router(websocket_router)
app.include_router(
    cozinha_router,
    dependencies=[Depends(exigir_perfis("cozinha", "gerente"))],
)
app.include_router(
    notificacoes_router,
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    fechamento_router,
    dependencies=[Depends(exigir_perfis("caixa", "gerente"))],
)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "versao": settings.APP_VERSION,
        "status": "online",
        "documentacao": "/docs",
        "painel_web": "/web" if web_directory.is_dir() else None,
    }
