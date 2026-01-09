from mistralai import Mistral
from pathlib import Path
from mistralai import DocumentURLChunk, ImageURLChunk, TextChunk
import json
from pathlib import Path
# from app.ocr_utils.config import client
from app.ocr_utils.config import MistralClient

def mistral_ocr_results(file_path: str):
    """
    Extract OCR results from a PDF file using Mistral API
    
    :param file_path: location of file to be processed
    :type file_path: str
    """

    client=MistralClient.get_client()
    pdf_file = Path(file_path)
    uploaded_file = client.files.upload(
    file={
        "file_name": pdf_file.stem,
        "content": pdf_file.read_bytes(),
    },
    purpose="ocr",
    )

    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
    pdf_response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=True
    )
    response_dict = json.loads(pdf_response.model_dump_json())
    return response_dict