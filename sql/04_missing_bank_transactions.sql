
-- ============================================
-- FINANCEOPS SENTINEL
-- MISSING BANK TRANSACTIONS
-- ============================================

SELECT
    l.transaction_id,
    l.transaction_date,
    l.account_id,
    l.merchant,
    l.category,

    printf(
        '%.2f',
        l.amount_cents / 100.0
    ) AS ledger_amount_cad,

    COUNT(*) OVER () AS total_missing

FROM ledger_transactions AS l

LEFT JOIN bank_transactions AS b
    ON l.transaction_id = b.transaction_id

WHERE b.transaction_id IS NULL

ORDER BY
    l.amount_cents DESC,
    l.transaction_id;
