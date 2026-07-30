from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from backend.core.config import settings
from backend.core.security import obter_usuario_por_token
from backend.core.websocket_manager import manager
from backend.database import SessionLocal


router = APIRouter(tags=["WebSocket"])

PERFIS_POR_CANAL = {
    "mesas": {"garcom", "gerente"},
    "cozinha": {"cozinha", "gerente"},
    "bar": {"cozinha", "gerente"},
    "caixa": {"caixa", "gerente"},
    "notificacoes": {"garcom", "caixa", "cozinha", "gerente"},
    "gerente": {"gerente"},
}


@router.websocket("/ws/{canal}")
async def websocket_endpoint(websocket: WebSocket, canal: str):
    if canal not in settings.WS_CHANNELS:
        await websocket.close(code=1008, reason="Canal inválido")
        return

    token = websocket.query_params.get("token", "")
    db = SessionLocal()
    try:
        usuario = obter_usuario_por_token(token, db)
    except HTTPException:
        await websocket.close(code=1008, reason="Autenticação obrigatória")
        return
    finally:
        db.close()

    perfis_permitidos = PERFIS_POR_CANAL.get(canal, {"gerente"})
    if usuario.perfil not in perfis_permitidos:
        await websocket.close(code=1008, reason="Canal não autorizado")
        return

    await manager.connect(canal, websocket)
    try:
        await websocket.send_json(
            {
                "evento": "conectado",
                "dados": {
                    "canal": canal,
                    "usuario_id": usuario.id,
                },
            }
        )

        while True:
            mensagem = await websocket.receive_text()
            if mensagem == "ping":
                await websocket.send_json({"evento": "pong"})
            else:
                await websocket.send_json(
                    {
                        "evento": "erro",
                        "dados": {
                            "mensagem": (
                                "Este canal aceita somente eventos do servidor"
                            )
                        },
                    }
                )
    except WebSocketDisconnect:
        manager.disconnect(canal, websocket)
