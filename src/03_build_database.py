
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import csv
import sqlite3


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

SCHEMA_PATH = PROJECT_ROOT / "sql" / "01_create_tables.sql"

LEDGER_PATH = RAW_DIR / "ledger_transactions.csv"
BANK_PATH = RAW_DIR / "bank_transactions.csv"

DATABASE_PATH = PROCESSED_DIR / "financeops.db"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Convert Canadian dollar amounts to cents
# --------------------------------------------------

def dollars_to_cents(value):
    amount = Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return int(amount * 100)


# --------------------------------------------------
# 3. Load CSV data
# --------------------------------------------------

def load_csv(file_path, required_columns):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    with file_path.open(
        "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        if not required_columns.issubset(
            set(reader.fieldnames or [])
        ):
            raise ValueError(
                f"Missing required columns in {file_path.name}"
            )

        return list(reader)


# --------------------------------------------------
# 4. Main database-building process
# --------------------------------------------------

def main():

    print("\nFINANCEOPS SENTINEL - DATABASE BUILD")
    print("=" * 55)

    # Read source datasets

    ledger_rows = load_csv(
        LEDGER_PATH,
        {
            "transaction_id",
            "transaction_date",
            "account_id",
            "merchant",
            "category",
            "amount",
            "currency"
        }
    )

    bank_rows = load_csv(
        BANK_PATH,
        {
            "bank_reference",
            "transaction_id",
            "posting_date",
            "bank_amount",
            "currency"
        }
    )

    print(f"Loaded ledger CSV: {len(ledger_rows):,} records")
    print(f"Loaded bank CSV:   {len(bank_rows):,} records")

    if len(ledger_rows) != 5000 or len(bank_rows) != 4990:
        raise ValueError(
            "Unexpected CSV record counts. "
            "Run the data validation script first."
        )

    # Read the SQL schema

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"SQL schema not found: {SCHEMA_PATH}"
        )

    schema_sql = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    # Connect to the SQLite database

    with sqlite3.connect(DATABASE_PATH) as conn:

        # Recreate the tables
        # This deletes existing records in these tables.

        conn.executescript(schema_sql)

        print("\nSQL tables created successfully.")

        # Import ledger transactions

        ledger_values = [
            (
                row["transaction_id"],
                row["transaction_date"],
                row["account_id"],
                row["merchant"],
                row["category"],
                dollars_to_cents(row["amount"]),
                row["currency"]
            )
            for row in ledger_rows
        ]

        conn.executemany(
            """
            INSERT INTO ledger_transactions (
                transaction_id,
                transaction_date,
                account_id,
                merchant,
                category,
                amount_cents,
                currency
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ledger_values
        )

        # Import bank transactions

        bank_values = [
            (
                row["bank_reference"],
                row["transaction_id"],
                row["posting_date"],
                dollars_to_cents(row["bank_amount"]),
                row["currency"]
            )
            for row in bank_rows
        ]

        conn.executemany(
            """
            INSERT INTO bank_transactions (
                bank_reference,
                transaction_id,
                posting_date,
                bank_amount_cents,
                currency
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            bank_values
        )

        # Verify imported record counts

        ledger_count = conn.execute(
            "SELECT COUNT(*) FROM ledger_transactions"
        ).fetchone()[0]

        bank_count = conn.execute(
            "SELECT COUNT(*) FROM bank_transactions"
        ).fetchone()[0]

        if ledger_count != 5000 or bank_count != 4990:
            raise ValueError(
                "Database verification failed."
            )

    # Display final results

    print("\nDATABASE VERIFICATION")
    print("-" * 55)

    print(f"Ledger records imported: {ledger_count:,}")
    print(f"Bank records imported:   {bank_count:,}")

    print("\nDatabase location:")
    print(DATABASE_PATH)

    print("\nSUCCESS: SQLite database built successfully!")


# --------------------------------------------------
# 5. Run the program
# --------------------------------------------------

if __name__ == "__main__":
    main()
