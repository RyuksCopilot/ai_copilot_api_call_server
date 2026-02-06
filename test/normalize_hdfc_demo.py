import re
import json

# ============================
# HARDCODED OCR OUTPUT ROW
# ============================


ocr_row= {
    "Tran ID": "S9233365",
    "Value Date": "03-Apr-2025",
    "Transaction Date": "03-Apr-2025",
    "Transaction Remarks": "UPI/9461250770-3@ib/Payment from Ph/Punjab National",
    "Withdrawal (Dr)": "0",
    "Deposit (Cr)": "25000.00",
    "Balance": "45985.37"
}

bank_config = {
  "bank_name": "HDFC",
  "table_headers": {
    "date": ["Transaction Date", "Value Date"],
    "description": ["Transaction Remarks"],
    "amount": ["Withdrawal (Dr)", "Deposit (Cr)"],
    "type": ["DR/CR"],
    "balance": ["Balance"]
  },

  "debit_rule": {
    "direct_column": "Withdrawal (Dr)",
    "na_values": ["NA", "", "-"]
  },

  "credit_rule": {
    "direct_column": "Deposit (Cr)",
    "na_values": ["NA", "", "-"]
  },

  "party_rules": {
    "from_party": "extract_after:Payment from|UPI/",
    "to_party": "static:YOU"
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

def safe_float(value, na_values=None):
    if value is None:
        return 0.0
    if na_values and str(value).strip() in na_values:
        return 0.0
    try:
        return float(str(value).replace(",", "").strip())
    except:
        return 0.0

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

    
    debit_amount = 0.0
    credit_amount = 0.0

    # ==========================
    # STRATEGY 1 — DIRECT COLUMNS
    # ==========================
    if "direct_column" in config.get("debit_rule", {}):
        dr_col = config["debit_rule"]["direct_column"]
        cr_col = config["credit_rule"]["direct_column"]

        debit_amount = safe_float(
            row.get(dr_col),
            config["debit_rule"].get("na_values")
        )

        credit_amount = safe_float(
            row.get(cr_col),
            config["credit_rule"].get("na_values")
        )

    # ==========================
    # STRATEGY 2 — DR/CR TYPE COLUMN
    # ==========================
    else:
        amt_col = get_col(row, config["table_headers"]["amount"])
        amount = safe_float(row[amt_col])

        type_col = config["debit_rule"]["type_column"]
        tx_type = row.get(type_col, "")

        if tx_type == config["debit_rule"]["debit_value"]:
            debit_amount = amount
        else:
            credit_amount = amount


    # Party Extraction
    from_party, to_party = extract_parties(description, config["party_rules"])
    txn["debit_amount"] = debit_amount
    txn["credit_amount"] = credit_amount
    txn["from_party"] = from_party
    txn["to_party"] = to_party
    # txn["reference"] = description

    return txn

# ============================
# RUN
# ============================
if __name__ == "__main__":
    result = normalize_row(ocr_row, bank_config)

    print("\nNormalized Transaction JSON:\n")
    print(json.dumps(result, indent=2))
