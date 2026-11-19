
-- ==============================================
-- FINANCEOPS SENTINEL
-- AMOUNT MISMATCH DETECTION
-- ==============================================

SELECT
    l.transaction_id,
    l.transaction_date,
    l.account_id,
    l.merchant,
    l.category,

    b.bank_reference,

    printf(
        '%.2f',
        l.amount_cents / 100.0
    ) AS ledger_amount_cad,

    printf(
        '%.2f',
        b.bank_amount_cents / 100.0
    ) AS bank_amount_cad,

    printf(
        '%.2f',
        (b.bank_amount_cents - l.amount_cents) / 100.0
    ) AS difference_cad,

    printf(
        '%.2f',
        ABS(b.bank_amount_cents - l.amount_cents) / 100.0
    ) AS absolute_difference_cad,

    COUNT(*) OVER () AS total_mismatches

FROM ledger_transactions AS l

INNER JOIN bank_transactions AS b
    ON l.transaction_id = b.transaction_id

WHERE l.amount_cents != b.bank_amount_cents

ORDER BY
    ABS(b.bank_amount_cents - l.amount_cents) DESC,
    l.transaction_id;
