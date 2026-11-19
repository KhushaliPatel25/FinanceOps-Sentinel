
-- ==================================================
-- FINANCEOPS SENTINEL
-- SQL DATABASE SCHEMA
-- ==================================================

-- Recreate tables when rebuilding the database.
-- WARNING: Existing data in these two tables is deleted.

DROP TABLE IF EXISTS bank_transactions;
DROP TABLE IF EXISTS ledger_transactions;


-- ==================================================
-- TABLE 1: LEDGER TRANSACTIONS
-- ==================================================

CREATE TABLE ledger_transactions (

    transaction_id TEXT PRIMARY KEY,

    transaction_date TEXT NOT NULL,

    account_id TEXT NOT NULL,

    merchant TEXT NOT NULL,

    category TEXT NOT NULL,

    amount_cents INTEGER NOT NULL
        CHECK (amount_cents > 0),

    currency TEXT NOT NULL
        CHECK (currency = 'CAD')

);


-- ==================================================
-- TABLE 2: BANK TRANSACTIONS
-- ==================================================

CREATE TABLE bank_transactions (

    bank_reference TEXT PRIMARY KEY,

    transaction_id TEXT NOT NULL,

    posting_date TEXT NOT NULL,

    bank_amount_cents INTEGER NOT NULL
        CHECK (bank_amount_cents > 0),

    currency TEXT NOT NULL
        CHECK (currency = 'CAD')

);


-- ==================================================
-- CREATE INDEXES FOR FASTER RECONCILIATION
-- ==================================================

CREATE INDEX idx_ledger_date
ON ledger_transactions(transaction_date);

CREATE INDEX idx_bank_transaction_id
ON bank_transactions(transaction_id);

CREATE INDEX idx_bank_posting_date
ON bank_transactions(posting_date);


-- ==================================================
-- SCHEMA COMPLETE
-- ==================================================
