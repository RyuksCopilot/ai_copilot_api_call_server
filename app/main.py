from fastapi import FastAPI, WebSocket
from app.core.config import settings
from app.api.v1.routes.forward import router as forward_router
from app.ws.routes import websocket_handler

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(
    forward_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Forward"]
)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_handler(websocket, client_id)


@app.get("/")
def health():
    return {"status": "ok"}
