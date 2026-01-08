import json
import re
from datetime import datetime
from typing import List, Dict, Any


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


def extract_payment_metadata(remarks: str | None) -> Dict[str, str | None]:
    result = {
        "upi_id": None,
        "party": None,
        "bank": None,
    }

    if not remarks:
        return result

    parts = [p.strip() for p in remarks.split("/")]

    for part in parts:
        if "@" in part and re.match(r".+@.+", part):
            result["upi_id"] = part
            break

    if len(parts) >= 2 and parts[0].upper() == "UPI":
        result["party"] = parts[1]


    if parts:
        result["bank"] = parts[-1]

    return result


def markdown_table_to_json(markdown: str) -> List[Dict[str, Any]]:
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    if len(lines) < 2:
        return []

    headers = [h.strip() for h in lines[0].strip("|").split("|")]

    def normalize_header(h: str) -> str:
        h = h.lower()
        h = re.sub(r"[^\w\s]", "", h)
        h = h.replace(" ", "_")
        h = h.replace("withdrawl", "withdrawal")
        return h

    headers = [normalize_header(h) for h in headers]
    records = []

    for row in lines[2:]:
        values = [v.strip() for v in row.strip("|").split("|")]
        if len(values) != len(headers):
            continue

        record = dict(zip(headers, values))
        print(f"Record is \n {record}")

        for k, v in record.items():
            if v in ("", "NA", "N/A"):
                record[k] = None
            elif k in {"withdrawal_dr", "deposit_cr", "balance"} and v is not None:
                print(f" k is {k} and value is {v}")
                record[k] = float(v)
            elif k == "sr_no" and v is not None:
                record[k] = int(v)

        record["value_date"] = normalize_date(record.get("value_date"))
        record["transaction_date"] = normalize_date(record.get("transaction_date"))


        withdrawal = record.get("withdrawal_dr")
        deposit = record.get("deposit_cr")
        if deposit is not None:
            record["direction"] = "credit"
            record["amount"] = deposit
        elif withdrawal is not None:
            record["direction"] = "debit"
            record["amount"] = -withdrawal
        else:
            record["direction"] = None
            record["amount"] = None


        # Extract metadata
        meta = extract_payment_metadata(record.get("transaction_remarks"))
        record.update(meta)

        records.append(record)

    return records


def to_dummy_format(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "from_ledger": record.get("bank"),
        "to_ledger": record.get("party"),
        "amount": record.get("amount"),
        "date": iso_to_yyyymmdd(record.get("transaction_date")),
    }

def parse_mistral_ocr_response(response_dict: dict) -> List[Dict[str, Any]]:
    final_records = []

    for page in response_dict.get("pages", []):
        markdown = page.get("markdown")
        if markdown:
            parsed_rows = markdown_table_to_json(markdown)
            for row in parsed_rows:
                final_records.append(to_dummy_format(row))

    return final_records



