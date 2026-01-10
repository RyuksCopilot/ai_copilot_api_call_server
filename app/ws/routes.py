# import json
# from fastapi import WebSocket, WebSocketDisconnect
# from app.ws.manager import manager
# from app.ws.state import pending_requests 


# async def websocket_handler(websocket: WebSocket, client_id: str):
#     await manager.connect(client_id, websocket)
#     print(f"Client connected: {client_id}")

#     try:
#         while True:
#             message = await websocket.receive_text()
#             data = json.loads(message)

#             print(f"WS response from client {client_id}")

#             future = pending_requests.get(client_id)
#             if future and not future.done():
#                 future.set_result(data)

#     except WebSocketDisconnect:
#         manager.disconnect(client_id)
#         pending_requests.pop(client_id, None)


import json
from fastapi import WebSocket, WebSocketDisconnect
from app.ws.manager import manager
from app.ws.state import pending_requests


async def websocket_handler(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            # Ignore heartbeat pings
            if data.get("type") == "ping":
                continue

            print(f"WS RESPONSE from {client_id}: {data}")

            future = pending_requests.get(client_id)
            if future and not future.done():
                future.set_result(data)

    except WebSocketDisconnect as e:
        print(f"WS DISCONNECT client={client_id}, code={e.code}")
        manager.disconnect(client_id)
        pending_requests.pop(client_id, None)

    except Exception as e:
        print(f"WS ERROR client={client_id}: {e}")
        manager.disconnect(client_id)
        pending_requests.pop(client_id, None)
