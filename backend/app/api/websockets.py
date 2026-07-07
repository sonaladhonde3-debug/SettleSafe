"""
In-memory WebSocket broadcast manager for connected dashboard clients.

NOTE (see engineer handoff doc, point 2): this manager only synchronizes
clients connected to THIS process. If you scale to multiple app instances
behind a load balancer, swap the in-memory `_connections` set for a Redis
Pub/Sub backplane (publish alerts to a channel, subscribe from each
instance) so a client connected to instance A still receives alerts
generated on instance B.
"""
import asyncio
import json
import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

from app.config import settings

logger = logging.getLogger("risk_engine.websockets")


class ConnectionManager:
    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info("Client connected. Active connections: %d", len(self._connections))

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            self._connections.discard(websocket)
        logger.info("Client disconnected. Active connections: %d", len(self._connections))

    async def broadcast(self, message: dict):
        payload = json.dumps(message, default=str)
        dead_connections = []
        async with self._lock:
            targets = list(self._connections)
        for connection in targets:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            await self.disconnect(dead)

    async def heartbeat_loop(self):
        while True:
            await asyncio.sleep(settings.WS_HEARTBEAT_SECONDS)
            await self.broadcast({"type": "HEARTBEAT", "active_clients": len(self._connections)})


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Clients are not required to send anything; this keeps the
            # connection alive and detects disconnects promptly.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
