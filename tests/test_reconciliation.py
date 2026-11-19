
from pathlib import Path
import sqlite3

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "financeops.db"
)

SQL_PATH = (
    PROJECT_ROOT / "sql" / "08_reconciliation_details.sql"
)

EXPECTED_COUNTS = {
    "Matched": 4775,
    "Missing from bank": 100,
    "Amount mismatch": 75,
    "Duplicate bank records": 50,
    "Unexpected bank transactions": 40
}


@pytest.fixture(scope="module")
def reconciliation_data():

    assert DATABASE_PATH.exists(), "Database is missing"
    assert SQL_PATH.exists(), "Reconciliation SQL is missing"

    sql = SQL_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DATABASE_PATH) as conn:
        data = pd.read_sql_query(sql, conn)

    return data


def test_total_transaction_count(reconciliation_data):

    assert len(reconciliation_data) == 5040


def test_reconciliation_status_counts(reconciliation_data):

    actual = (
        reconciliation_data["reconciliation_status"]
        .value_counts()
        .to_dict()
    )

    assert actual == EXPECTED_COUNTS


def test_unique_transaction_ids(reconciliation_data):

    assert reconciliation_data["transaction_id"].is_unique


def test_amount_mismatch_values(reconciliation_data):

    mismatches = reconciliation_data[
        reconciliation_data["reconciliation_status"]
        == "Amount mismatch"
    ]

    assert len(mismatches) == 75
    assert (mismatches["difference_cents"] == 725).all()


def test_duplicate_bank_records(reconciliation_data):

    duplicates = reconciliation_data[
        reconciliation_data["reconciliation_status"]
        == "Duplicate bank records"
    ]

    assert len(duplicates) == 50
    assert (duplicates["bank_record_count"] == 2).all()


def test_missing_bank_transactions(reconciliation_data):

    missing = reconciliation_data[
        reconciliation_data["reconciliation_status"]
        == "Missing from bank"
    ]

    assert len(missing) == 100
    assert (missing["bank_record_count"] == 0).all()


def test_unexpected_bank_transactions(reconciliation_data):

    unexpected = reconciliation_data[
        reconciliation_data["reconciliation_status"]
        == "Unexpected bank transactions"
    ]

    assert len(unexpected) == 40
    assert unexpected["ledger_amount_cents"].isna().all()


def test_generated_reports_exist():

    files = [
        PROJECT_ROOT / "reports" / "summaries"
        / "reconciliation_summary.csv",

        PROJECT_ROOT / "reports" / "summaries"
        / "reconciliation_details.csv",

        PROJECT_ROOT / "reports" / "exceptions"
        / "financial_exceptions.csv",

        PROJECT_ROOT / "reports" / "summaries"
        / "FinanceOps_Reconciliation_Report.xlsx"
    ]

    for file in files:
        assert file.exists(), f"Missing report: {file.name}"
        assert file.stat().st_size > 0
