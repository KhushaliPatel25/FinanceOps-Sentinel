
from pathlib import Path
import pandas as pd


# ----------------------------------------
# 1. Locate the project files
# ----------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "reports" / "summaries"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

ledger_path = RAW_DIR / "ledger_transactions.csv"
bank_path = RAW_DIR / "bank_transactions.csv"

if not ledger_path.exists() or not bank_path.exists():
    raise FileNotFoundError(
        "CSV files missing. Run 01_generate_synthetic_data.py first."
    )


# ----------------------------------------
# 2. Load financial datasets
# ----------------------------------------

ledger = pd.read_csv(ledger_path)
bank = pd.read_csv(bank_path)

print("\nFINANCEOPS SENTINEL - DATA VALIDATION")
print("=" * 55)


# ----------------------------------------
# 3. Check required columns
# ----------------------------------------

ledger_columns = {
    "transaction_id", "transaction_date",
    "account_id", "merchant", "category",
    "amount", "currency"
}

bank_columns = {
    "bank_reference", "transaction_id",
    "posting_date", "bank_amount", "currency"
}

assert ledger_columns.issubset(ledger.columns), (
    "Ledger is missing required columns."
)

assert bank_columns.issubset(bank.columns), (
    "Bank data is missing required columns."
)


# ----------------------------------------
# 4. Detect financial discrepancies
# ----------------------------------------

ledger_ids = set(ledger["transaction_id"])
bank_ids = set(bank["transaction_id"])

missing_count = len(ledger_ids - bank_ids)
unexpected_count = len(bank_ids - ledger_ids)

duplicate_count = int(
    bank["transaction_id"].duplicated().sum()
)

# Compare amounts using one bank record per transaction
unique_bank = bank.drop_duplicates(
    subset=["transaction_id"]
)

matched = ledger[
    ["transaction_id", "amount"]
].merge(
    unique_bank[["transaction_id", "bank_amount"]],
    on="transaction_id",
    how="inner",
    validate="one_to_one"
)

mismatch_count = int(
    (
        matched["amount"].round(2)
        != matched["bank_amount"].round(2)
    ).sum()
)


# ----------------------------------------
# 5. Run validation checks
# ----------------------------------------

checks = {
    "Ledger records": (len(ledger), 5000),
    "Bank records": (len(bank), 4990),
    "Missing bank transactions": (missing_count, 100),
    "Amount mismatches": (mismatch_count, 75),
    "Duplicate bank records": (duplicate_count, 50),
    "Unexpected bank transactions": (unexpected_count, 40),
    "Unique ledger IDs": (
        ledger["transaction_id"].nunique(), 5000
    ),
    "Unique bank references": (
        bank["bank_reference"].nunique(), 4990
    ),
    "Ledger currency CAD": (
        bool(ledger["currency"].eq("CAD").all()), True
    ),
    "Bank currency CAD": (
        bool(bank["currency"].eq("CAD").all()), True
    ),
    "Positive ledger amounts": (
        bool(ledger["amount"].gt(0).all()), True
    ),
    "Positive bank amounts": (
        bool(bank["bank_amount"].gt(0).all()), True
    )
}

results = []

for name, (actual, expected) in checks.items():
    passed = actual == expected
    status = "PASS" if passed else "FAIL"

    print(f"{status:4} | {name}: {actual}")

    results.append({
        "check_name": name,
        "actual": actual,
        "expected": expected,
        "status": status
    })


# ----------------------------------------
# 6. Save validation report
# ----------------------------------------

report = pd.DataFrame(results)

report_path = REPORT_DIR / "data_validation_summary.csv"
report.to_csv(report_path, index=False)

print("\nValidation report saved:")
print(report_path)

if not report["status"].eq("PASS").all():
    raise AssertionError(
        "One or more validation checks failed."
    )

print("\nSUCCESS: All data validation checks passed!")
