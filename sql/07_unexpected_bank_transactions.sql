
-- ==============================================
-- FINANCEOPS SENTINEL
-- UNEXPECTED BANK TRANSACTION DETECTION
-- ==============================================

SELECT
    b.bank_reference,

    b.transaction_id,

    b.posting_date,

    printf(
        '%.2f',
        b.bank_amount_cents / 100.0
    ) AS bank_amount_cad,

    b.currency,

    'Unexpected bank transaction'
        AS exception_type,

    COUNT(*) OVER ()
        AS total_unexpected_transactions

FROM bank_transactions b

LEFT JOIN ledger_transactions l
    ON b.transaction_id = l.transaction_id

WHERE l.transaction_id IS NULL

ORDER BY b.transaction_id;
