from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.core.websocket_manager import manager
from backend.core.config import settings

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{canal}")
async def websocket_endpoint(websocket: WebSocket, canal: str):
    if canal not in settings.WS_CHANNELS:
        await websocket.accept()
        await websocket.send_json({
            "evento": "erro",
            "dados": {
                "mensagem": f"Canal inválido: {canal}"
            }
        })
        await websocket.close()
        return

    await manager.connect(canal, websocket)

    try:
        await websocket.send_json({
            "evento": "conectado",
            "dados": {
                "canal": canal,
                "mensagem": f"Conectado ao canal {canal}"
            }
        })

        while True:
            data = await websocket.receive_text()

            await manager.broadcast(canal, {
                "evento": "mensagem_recebida",
                "dados": {
                    "canal": canal,
                    "conteudo": data
                }
            })

    except WebSocketDisconnect:
        manager.disconnect(canal, websocket)