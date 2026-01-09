import json
from fastapi import WebSocket, WebSocketDisconnect
from app.ws.manager import manager
from app.ws.state import pending_requests 


async def websocket_handler(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    print(f"Client connected: {client_id}")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            print(f"WS response from client {client_id}")

            future = pending_requests.get(client_id)
            if future and not future.done():
                future.set_result(data)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        pending_requests.pop(client_id, None)

# import asyncio
# import json
# from fastapi import WebSocket, WebSocketDisconnect
# from app.ws.manager import manager
# from app.ws.state import pending_requests

# PING_INTERVAL = 20  # seconds

# async def websocket_handler(websocket: WebSocket, client_id: str):
#     await manager.connect(client_id, websocket)
#     print(f"Client connected: {client_id}")

#     async def keepalive():
#         while True:
#             await asyncio.sleep(PING_INTERVAL)
#             try:
#                 await websocket.send_text(json.dumps({"type": "ping"}))
#             except Exception:
#                 break

#     keepalive_task = asyncio.create_task(keepalive())

#     try:
#         while True:
#             message = await websocket.receive_text()
#             data = json.loads(message)

#             future = pending_requests.get(client_id)
#             if future and not future.done():
#                 future.set_result(data)

#     except WebSocketDisconnect:
#         print(f"Client disconnected: {client_id}")
#     finally:
#         keepalive_task.cancel()
#         manager.disconnect(client_id)
#         pending_requests.pop(client_id, None)
