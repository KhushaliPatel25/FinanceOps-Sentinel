
from pathlib import Path
import sqlite3

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment


# ---------------------------------------------
# 1. Project paths
# ---------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "financeops.db"
)

SQL_PATH = (
    PROJECT_ROOT / "sql" / "08_reconciliation_details.sql"
)

SUMMARY_DIR = PROJECT_ROOT / "reports" / "summaries"
EXCEPTION_DIR = PROJECT_ROOT / "reports" / "exceptions"

SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
EXCEPTION_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------
# 2. Expected reconciliation results
# ---------------------------------------------

EXPECTED_COUNTS = {
    "Matched": 4775,
    "Missing from bank": 100,
    "Amount mismatch": 75,
    "Duplicate bank records": 50,
    "Unexpected bank transactions": 40
}


# ---------------------------------------------
# 3. Load reconciliation results from SQLite
# ---------------------------------------------

def load_reconciliation_data():

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database missing. Run 03_build_database.py first."
        )

    if not SQL_PATH.exists():
        raise FileNotFoundError(
            "Master reconciliation SQL file is missing."
        )

    sql_query = SQL_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as conn:
        data = pd.read_sql_query(sql_query, conn)

    return data


# ---------------------------------------------
# 4. Validate reconciliation results
# ---------------------------------------------

def validate_results(data):

    actual_counts = (
        data["reconciliation_status"]
        .value_counts()
        .to_dict()
    )

    if len(data) != 5040:
        raise ValueError(
            f"Expected 5040 rows, found {len(data)}"
        )

    if actual_counts != EXPECTED_COUNTS:
        raise ValueError(
            "Reconciliation status counts do not match "
            f"expected results: {actual_counts}"
        )

    if data["transaction_id"].duplicated().any():
        raise ValueError(
            "Duplicate transaction IDs in master report."
        )

    print("\nRECONCILIATION VALIDATION")
    print("-" * 55)

    for status, expected in EXPECTED_COUNTS.items():
        print(f"PASS | {status}: {expected:,}")

    print("\nSUCCESS: Reconciliation validation passed!")


# ---------------------------------------------
# 5. Prepare financial reporting columns
# ---------------------------------------------

def prepare_reporting_data(data):

    money_columns = [
        "ledger_amount_cents",
        "bank_amount_cents",
        "difference_cents"
    ]

    for column in money_columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="raise"
        ).astype("Int64")

        new_column = column.replace(
            "_cents", "_cad"
        )

        data[new_column] = data[column].map(
            lambda value:
            round(int(value) / 100, 2)
            if pd.notna(value)
            else None
        )

    return data


# ---------------------------------------------
# 6. Generate reconciliation summary
# ---------------------------------------------

def generate_summary(data):

    summary = (
        data.groupby("reconciliation_status")
        .size()
        .reset_index(name="transaction_count")
    )

    summary["percentage"] = (
        summary["transaction_count"]
        / len(data) * 100
    ).round(2)

    return summary


# ---------------------------------------------
# 7. Format Excel worksheets
# ---------------------------------------------

def format_excel_sheet(worksheet):

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="17365D"
    )

    header_font = Font(
        bold=True,
        color="FFFFFF"
    )

    for cell in worksheet[1]:

        cell.fill = header_fill
        cell.font = header_font

        cell.alignment = Alignment(
            horizontal="center"
        )

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column in worksheet.columns:

        column_letter = column[0].column_letter

        max_length = max(
            len(str(cell.value))
            if cell.value is not None else 0
            for cell in column
        )

        worksheet.column_dimensions[
            column_letter
        ].width = min(max(max_length + 3, 14), 35)

    for cell in worksheet[1]:
        if str(cell.value).endswith("_cad"):

            for row in worksheet.iter_rows(
                min_row=2,
                min_col=cell.column,
                max_col=cell.column
            ):
                row[0].number_format = '#,##0.00'


# ---------------------------------------------
# 8. Generate CSV and Excel reports
# ---------------------------------------------

def generate_reports(data, summary):

    exceptions = data[
        data["reconciliation_status"] != "Matched"
    ].copy()

    if len(exceptions) != 265:
        raise ValueError(
            "Unexpected exception count."
        )

    # Save CSV files

    summary.to_csv(
        SUMMARY_DIR / "reconciliation_summary.csv",
        index=False
    )

    data.to_csv(
        SUMMARY_DIR / "reconciliation_details.csv",
        index=False
    )

    exceptions.to_csv(
        EXCEPTION_DIR / "financial_exceptions.csv",
        index=False
    )

    # Generate Excel workbook

    excel_path = (
        SUMMARY_DIR / "FinanceOps_Reconciliation_Report.xlsx"
    )

    with pd.ExcelWriter(
        excel_path,
        engine="openpyxl"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        exceptions.to_excel(
            writer,
            sheet_name="Exceptions",
            index=False
        )

        data.to_excel(
            writer,
            sheet_name="All Transactions",
            index=False
        )

        for worksheet in writer.book.worksheets:
            format_excel_sheet(worksheet)

    return excel_path, len(exceptions)


# ---------------------------------------------
# 9. Main program
# ---------------------------------------------

def main():

    print("\nFINANCEOPS SENTINEL")
    print("AUTOMATED FINANCIAL RECONCILIATION")
    print("=" * 55)

    data = load_reconciliation_data()

    print(f"\nSQL records retrieved: {len(data):,}")

    validate_results(data)

    data = prepare_reporting_data(data)

    summary = generate_summary(data)

    excel_path, exception_count = generate_reports(
        data, summary
    )

    print("\nREPORT GENERATION SUMMARY")
    print("-" * 55)

    print(f"Total transactions: {len(data):,}")
    print(f"Matched transactions: 4,775")
    print(f"Financial exceptions: {exception_count:,}")

    print("\nGenerated files:")
    print("- reconciliation_summary.csv")
    print("- reconciliation_details.csv")
    print("- financial_exceptions.csv")
    print("- FinanceOps_Reconciliation_Report.xlsx")

    print("\nExcel report location:")
    print(excel_path)

    print("\nSUCCESS: All financial reports generated!")


if __name__ == "__main__":
    main()
