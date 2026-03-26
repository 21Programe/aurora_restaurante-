from fastapi import WebSocket
from collections import defaultdict
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, channel: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[channel].append(websocket)

    def disconnect(self, channel: str, websocket: WebSocket):
        if channel in self.active_connections and websocket in self.active_connections[channel]:
            self.active_connections[channel].remove(websocket)

    async def broadcast(self, channel: str, message: dict):
        dead_connections = []

        for connection in self.active_connections.get(channel, []):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(channel, connection)


manager = ConnectionManager()