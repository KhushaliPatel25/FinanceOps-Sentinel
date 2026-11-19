
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker


# --------------------------------------------
# 1. Project settings
# --------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
rng = np.random.default_rng(SEED)

Faker.seed(SEED)
fake = Faker("en_CA")

TOTAL_TRANSACTIONS = 5000


# --------------------------------------------
# 2. Generate synthetic ledger transactions
# --------------------------------------------

merchant_names = [fake.company() for _ in range(30)]

categories = [
    "Retail",
    "Groceries",
    "Utilities",
    "Transportation",
    "Healthcare",
    "Subscriptions",
    "Travel"
]

random_days = rng.integers(
    0, 90, size=TOTAL_TRANSACTIONS
)

ledger = pd.DataFrame({
    "transaction_id": [
        f"TXN{i:06d}"
        for i in range(1, TOTAL_TRANSACTIONS + 1)
    ],
    "transaction_date": [
        (date(2026, 1, 1) + timedelta(days=int(day))).isoformat()
        for day in random_days
    ],
    "account_id": [
        f"ACC{i:04d}"
        for i in rng.integers(
            1, 101, size=TOTAL_TRANSACTIONS
        )
    ],
    "merchant": rng.choice(
        merchant_names, size=TOTAL_TRANSACTIONS
    ),
    "category": rng.choice(
        categories, size=TOTAL_TRANSACTIONS
    ),
    "amount": (
        rng.integers(
            1000, 200000, size=TOTAL_TRANSACTIONS
        ) / 100
    ),
    "currency": "CAD"
})


# --------------------------------------------
# 3. Simulate corresponding bank transactions
# --------------------------------------------

bank = ledger[
    ["transaction_id", "transaction_date", "amount", "currency"]
].copy()

bank = bank.rename(columns={
    "transaction_date": "posting_date",
    "amount": "bank_amount"
})

bank.insert(
    0,
    "bank_reference",
    [f"BNK{i:06d}" for i in range(1, TOTAL_TRANSACTIONS + 1)]
)


# --------------------------------------------
# 4. Introduce deliberate financial exceptions
# --------------------------------------------

selected_ids = rng.choice(
    ledger["transaction_id"].to_numpy(),
    size=225,
    replace=False
)

missing_ids = set(selected_ids[:100])
mismatch_ids = set(selected_ids[100:175])
duplicate_ids = set(selected_ids[175:225])

# Remove 100 bank records
bank = bank[
    ~bank["transaction_id"].isin(missing_ids)
].copy()

# Change the amounts of 75 bank records
mismatch_mask = bank["transaction_id"].isin(mismatch_ids)

bank.loc[mismatch_mask, "bank_amount"] += 7.25

# Duplicate 50 bank records
duplicates = bank[
    bank["transaction_id"].isin(duplicate_ids)
].copy()

duplicates["bank_reference"] = [
    f"DUP{i:06d}"
    for i in range(1, len(duplicates) + 1)
]

# Add 40 unexpected bank-only transactions
extras = pd.DataFrame({
    "bank_reference": [
        f"EXTREF{i:06d}" for i in range(1, 41)
    ],
    "transaction_id": [
        f"EXT{i:06d}" for i in range(1, 41)
    ],
    "posting_date": ["2026-03-31"] * 40,
    "bank_amount": rng.integers(
        1000, 200000, size=40
    ) / 100,
    "currency": ["CAD"] * 40
})

bank = pd.concat(
    [bank, duplicates, extras],
    ignore_index=True
)

bank = bank.sample(
    frac=1,
    random_state=SEED
).reset_index(drop=True)


# --------------------------------------------
# 5. Save CSV datasets
# --------------------------------------------

ledger_path = RAW_DATA_DIR / "ledger_transactions.csv"
bank_path = RAW_DATA_DIR / "bank_transactions.csv"

ledger.to_csv(ledger_path, index=False)
bank.to_csv(bank_path, index=False)


# --------------------------------------------
# 6. Display generation summary
# --------------------------------------------

print("\nFINANCEOPS SENTINEL - DATA GENERATION")
print("=" * 50)

print(f"Ledger transactions: {len(ledger):,}")
print(f"Bank transactions:   {len(bank):,}")

print("\nDeliberately inserted exceptions:")
print("Missing bank transactions: 100")
print("Amount mismatches:         75")
print("Duplicate bank records:    50")
print("Unexpected bank records:   40")

print("\nGenerated files:")
print(ledger_path)
print(bank_path)

print("\nSUCCESS: Synthetic financial datasets created!")
