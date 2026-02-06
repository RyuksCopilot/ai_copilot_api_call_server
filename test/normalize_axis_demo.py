import re
import json

# ============================
# HARDCODED OCR OUTPUT ROW
# ============================
ocr_row = {
    "Tran Date": "01-04-2025",
    "Transaction Particulars": "IMPS PA Mukesh Kumar STATEBANKOFINDIA",
    "Amount(INR)": "8005.90",
    "DR/CR": "DR",
    "Balance(INR)": "136877.48"
}



# ============================
# HARDCODED AXIS CONFIG
# ============================
axis_config = {
    "bank_name": "AXIS",
    "table_headers": {
        "date": ["Tran Date", "Transaction Date"],
        "description": ["Transaction Particulars"],
        "amount": ["Amount(INR)"],
        "type": ["DR/CR"],
        "balance": ["Balance(INR)"]
    },
    "debit_rule": {
        "type_column": "DR/CR",
        "debit_value": "DR"
    },
    "credit_rule": {
        "type_column": "DR/CR",
        "credit_value": "CR"
    },
    "party_rules": {
        "from_party": "extract_after:IMPS|NEFT|UPI",
        "to_party": "extract_before:STATE BANK|AXIS|HDFC"
    }
}

# ============================
# HELPERS
# ============================
def get_col(row, possible_names):
    for name in possible_names:
        if name in row:
            return name
    raise KeyError(f"Column not found: {possible_names}")

def extract_parties(description, rules):
    from_party = ""
    to_party = ""

    # Extract AFTER rule
    after_rule = rules["from_party"].replace("extract_after:", "")
    after_match = re.split(after_rule, description, flags=re.IGNORECASE)
    if len(after_match) > 1:
        from_party = after_match[1].strip()

    # Extract BEFORE rule
    before_rule = rules["to_party"].replace("extract_before:", "")
    before_match = re.split(before_rule, description, flags=re.IGNORECASE)
    if len(before_match) > 1:
        to_party = before_match[0].strip()

    return from_party, to_party

# ============================
# NORMALIZER
# ============================
def normalize_row(row, config):
    txn = {}

    # Date
    date_col = get_col(row, config["table_headers"]["date"])
    txn["date"] = row[date_col]

    # Description
    desc_col = get_col(row, config["table_headers"]["description"])
    description = row[desc_col]

    # Balance
    bal_col = get_col(row, config["table_headers"]["balance"])
    txn["balance"] = float(row[bal_col])

    # Amount + DR/CR Logic
    amt_col = get_col(row, config["table_headers"]["amount"])
    amount = float(row[amt_col])

    tx_type = row[config["debit_rule"]["type_column"]]

    if tx_type == config["debit_rule"]["debit_value"]:
        txn["debit_amount"] = amount
        txn["credit_amount"] = 0.0
    else:
        txn["credit_amount"] = amount
        txn["debit_amount"] = 0.0

    # Party Extraction
    from_party, to_party = extract_parties(description, config["party_rules"])
    txn["from_party"] = from_party
    txn["to_party"] = to_party

    # Reference (optional)
    txn["reference"] = description

    return txn

# ============================
# RUN
# ============================
if __name__ == "__main__":
    result = normalize_row(ocr_row, axis_config)

    print("\n✅ Normalized Transaction JSON:\n")
    print(json.dumps(result, indent=2))
