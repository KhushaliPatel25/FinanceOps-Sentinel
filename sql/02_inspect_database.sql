
-- sqlite
-- ============================================
-- FINANCEOPS SENTINEL
-- DATABASE INSPECTION
-- ============================================

-- Verify the total records in both tables

SELECT
    'ledger_transactions' AS table_name,
    COUNT(*) AS record_count
FROM ledger_transactions

UNION ALL

SELECT
    'bank_transactions' AS table_name,
    COUNT(*) AS record_count
FROM bank_transactions;
