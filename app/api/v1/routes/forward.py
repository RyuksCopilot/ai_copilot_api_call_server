
import json
import asyncio
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.forward import ForwardRequest
from app.ws.manager import manager
from app.ws.state import pending_requests  # SAME IMPORT

from app.ocr_utils.ocr_results import mistral_ocr_results
from app.ocr_utils.parse_ocr_results import parse_mistral_ocr_response
router = APIRouter()

@router.post("/forward")
async def forward(payload: ForwardRequest):
    ws = manager.get(payload.client_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Client not connected")

    if payload.client_id in pending_requests:
        raise HTTPException(status_code=409, detail="Client busy")

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    pending_requests[payload.client_id] = future

    await ws.send_text(json.dumps({
        "method": payload.method,
        "endpoint": payload.endpoint,
        "body": payload.body
    }))

    try:
        return await asyncio.wait_for(future, timeout=30)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Client response timeout")
    finally:
        pending_requests.pop(payload.client_id, None)
        

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Basic validation
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(MEDIA_DIR, filename)

    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Dummy OCR response (placeholder)
    ocr_results = mistral_ocr_results(file_path)
    dummy_response = parse_mistral_ocr_response(ocr_results)
    # dummy_response = [
    #     {
    #         "from_ledger": "ICICI BANK",
    #         "to_ledger": "to_ledger_1",
    #         "amount": 100.0,
    #         "date":"20250401"
    #     },
    #     {
    #         "from_ledger": "from_ledger_2",
    #         "to_ledger": "to_ledger_2",
    #         "amount": 200.0,
    #         "date":"20250401"
    #     }
    # ]

    return JSONResponse(
        status_code=200,
        content=dummy_response
    )
