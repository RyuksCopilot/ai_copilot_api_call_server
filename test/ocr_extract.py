import json
from pathlib import Path
from mistralai import Mistral, DocumentURLChunk

# ==============================
# CONFIG
# ==============================
API_KEY = "saHMOIlNFXiLsvfLMzG4mJiOYZf4qa6z"
PDF_FILE_NAME = "sample.pdf"  # PDF must be in same folder as this script
# ==============================


def run_mistral_ocr():
    client = Mistral(api_key=API_KEY)

    pdf_path = Path(__file__).parent / PDF_FILE_NAME

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"Uploading: {pdf_path.name}")

    uploaded_file = client.files.upload(
        file={
            "file_name": pdf_path.stem,
            "content": pdf_path.read_bytes(),
        },
        purpose="ocr",
    )

    signed_url = client.files.get_signed_url(
        file_id=uploaded_file.id,
        expiry=1
    )

    print("Running OCR...")

    response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=False
    )

    result = json.loads(response.model_dump_json())

    # Save result to file
    output_file = pdf_path.stem + "_ocr.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"OCR complete!")
    print(f"Saved output to: {output_file}")

    return result


if __name__ == "__main__":
    run_mistral_ocr()