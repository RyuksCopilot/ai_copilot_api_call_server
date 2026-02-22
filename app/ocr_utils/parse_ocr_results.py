import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
import html_to_json
from dateutil import parser
from google.genai import types
from app.ocr_utils.config import GeminiClient

def markdown_table_to_json(table: str) -> List[Dict[str, Any]]:
    table_data = html_to_json.convert_tables(table)
    return table_data

def normalize_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    for fmt in ("%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def iso_to_yyyymmdd(date_str: str | None) -> str | None:
    if not date_str:
        return None
    return date_str.replace("-", "")

def general_amount_parser(amount_str: dict | None) -> float | None:
    if not amount_str or not isinstance(amount_str, dict):
        return None

    debit_value = None
    credit_value = None

    for key, value in amount_str.items():
        if not value or str(value).strip() in {"-", ""}:
            continue

        key_lower = key.lower()
        cleaned_value = str(value).replace(",", "").strip()

        try:
            amount = float(cleaned_value)
        except ValueError:
            continue

        if "debit" in key_lower:
            debit_value = amount
        elif "credit" in key_lower:
            credit_value = amount

    if debit_value is not None:
        return debit_value  # Outflow (Debit)
    if credit_value is not None:
        return -credit_value # Inflow (Credit) - Note: Adjust sign based on your preference

    return None

def general_date_parser(date_str: str | None) -> str | None:
    if not date_str:
        return None
    try:
        dt = parser.parse(date_str, dayfirst=True, fuzzy=True)
        return dt.strftime("%Y-%m-%d").replace("-", "")
    except (ValueError, TypeError):
        return None


def llm_batch_extract(narrations: List[str]) -> List[Dict[str, str]]:
    MODEL_NAME = "gemini-flash-lite-latest"
    SYSTEM_PROMPT = """
                    You are a financial transaction classifier.
                    Input: A JSON list of bank narrations.
                    Output: A JSON object with a key "results" containing a list of objects.

                    For each narration:
                    1. "ledger_name": Extract the counterparty name.
                    - Fix artifacts (e.g., "BA NK" -> "BANK").
                    - If it is a bank charge/fee, set name to "BANK CHARGES".

                    2. "transaction_type": Classify strictly into one of these 4 categories:
                    - "bank-person"
                    - "bank-bank"
                    - "charges"
                    - "unknown"
                    """
    print("GEMINI_LLM | Classifying narrations", len(narrations))

    client = GeminiClient.get_client()

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=json.dumps(narrations))
            ],
        )
    ]

    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(text=SYSTEM_PROMPT)
        ],
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=config,
    )

    usage = response.usage_metadata
    if usage:
        print(
            "GEMINI_LLM | tokens | prompt=%s | completion=%s | total=%s",
            usage.prompt_token_count,
            usage.candidates_token_count,
            usage.total_token_count,
        )


    raw_text = response.text

    try:
        parsed = json.loads(raw_text)
        return parsed.get("results", [])
    except Exception:
        print("GEMINI_LLM | Failed to parse response: %s", raw_text)
        raise



def resolve_ledger_direction(record: Dict[str, Any], extracted_entity: str) -> Tuple[str, str]:
    """
    Determines From/To based on Debit/Credit columns.
    Returns (from_ledger, to_ledger).
    """
    debit_val = 0.0
    credit_val = 0.0
    
    raw_debit = str(record.get('Debit (╬ô├⌐Γòú)', '0')).replace(',', '').strip()
    raw_credit = str(record.get('Credit (╬ô├⌐Γòú)', '0')).replace(',', '').strip()

    if raw_debit not in ['-', '']:
        try: debit_val = float(raw_debit)
        except: pass
        
    if raw_credit not in ['-', '']:
        try: credit_val = float(raw_credit)
        except: pass

    SELF_ACCOUNT = "MY_CLIENT_ACCOUNT" 

    if credit_val > 0:
        return extracted_entity, SELF_ACCOUNT
    elif debit_val > 0:
        return SELF_ACCOUNT, extracted_entity
    else:
        return "UNKNOWN", "UNKNOWN"

def extract_payment_metadata(remarks: str | None) -> Tuple[str | None, str | None]:
    """
    Legacy/Fallback function. 
    Kept because you asked not to change function names.
    """
    if not remarks: return None, None
    parts = [p.strip() for p in remarks.split("/")]
    party = None
    if len(parts) >= 2 and parts[0].upper() == "UPI":
        party = parts[1]
    return party, None


def to_dummy_format(record: Dict[str, Any], llm_result: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Maps the LLM result directly to the new schema.
    """
    ledger_name = "unknown"
    txn_type = "unknown"

    if llm_result:
        ledger_name = llm_result.get("ledger_name", "unknown")
        txn_type = llm_result.get("transaction_type", "unknown")

    return {
        "ledger_name": ledger_name,
        "transaction_type": txn_type,
        "amount": general_amount_parser(record), # Uses your existing function
        "date": general_date_parser(record.get("transaction_date") or record.get("Transaction Date")),
        "original_narration": record.get("Description/Narration")
    }


def parse_mistral_ocr_response(response_dict: dict) -> List[Dict[str, Any]]:
    final_records = []

    for page in response_dict.get("pages", []):
        tables = page.get("tables", [])

        for table in tables:
            if not table: continue
            
            parsed_rows = markdown_table_to_json(table["content"])
            flat_rows = []
            if isinstance(parsed_rows, list) and len(parsed_rows) > 0 and isinstance(parsed_rows[0], list):
                 for sublist in parsed_rows:
                     flat_rows.extend(sublist)
            else:
                flat_rows = parsed_rows

            valid_rows = []
            narrations_batch = []

            for row in flat_rows:
                narration = row.get("Description/Narration", "").strip()
                if not narration or narration.lower() == "total":
                    continue
                
                valid_rows.append(row)
                narrations_batch.append(narration)

            if narrations_batch:
                llm_results = llm_batch_extract(narrations_batch)
            else:
                llm_results = []

            for i, row in enumerate(valid_rows):
                extracted_data = llm_results[i] if i < len(llm_results) else None
                
                processed_record = to_dummy_format(row, llm_result=extracted_data)
                final_records.append(processed_record)

    return final_records