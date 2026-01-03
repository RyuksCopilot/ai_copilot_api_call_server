from fastapi import FastAPI, WebSocket
from app.core.config import settings
from app.api.v1.routes.forward import router as forward_router
from app.api.v1.routes.history_routes import router as history_router
from app.ws.routes import websocket_handler
from app.db.init_db import init_db


app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(
    forward_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Forward"]
)
app.include_router(history_router)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_handler(websocket, client_id)


@app.get("/")
def health():
    return {"status": "ok"}
