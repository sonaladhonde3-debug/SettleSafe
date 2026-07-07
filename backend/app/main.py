import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.endpoints import router as api_router
from app.api.websockets import websocket_endpoint, manager
from app.db.database import engine, Base
from app.db import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("risk_engine.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Start heartbeat
    asyncio.create_task(manager.heartbeat_loop())
    logger.info("%s started.", settings.APP_NAME)
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.websocket("/ws/alerts")
async def alerts_socket(websocket: WebSocket):
    await websocket_endpoint(websocket)


@app.on_event("startup")
async def start_heartbeat():
    asyncio.create_task(manager.heartbeat_loop())
    logger.info("%s started.", settings.APP_NAME)


@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "status": "running"}
