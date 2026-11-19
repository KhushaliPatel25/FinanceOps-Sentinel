
-- ==============================================
-- FINANCEOPS SENTINEL
-- MASTER RECONCILIATION DETAILS
-- ==============================================

WITH bank_rollup AS (

    SELECT
        transaction_id,
        COUNT(*) AS bank_record_count,
        MIN(posting_date) AS posting_date,
        MIN(bank_amount_cents) AS bank_amount_cents,
        GROUP_CONCAT(bank_reference, ', ') AS bank_references

    FROM bank_transactions

    GROUP BY transaction_id

),

ledger_comparison AS (

    SELECT
        l.transaction_id,
        l.transaction_date,
        l.account_id,
        l.merchant,
        l.category,
        l.amount_cents AS ledger_amount_cents,

        b.posting_date,
        b.bank_amount_cents,

        COALESCE(b.bank_record_count, 0)
            AS bank_record_count,

        b.bank_references,

        CASE
            WHEN b.transaction_id IS NULL
                THEN 'Missing from bank'

            WHEN b.bank_record_count > 1
                THEN 'Duplicate bank records'

            WHEN l.amount_cents <> b.bank_amount_cents
                THEN 'Amount mismatch'

            ELSE 'Matched'
        END AS reconciliation_status,

        CASE
            WHEN b.bank_record_count = 1
             AND l.amount_cents <> b.bank_amount_cents
            THEN b.bank_amount_cents - l.amount_cents
            ELSE NULL
        END AS difference_cents

    FROM ledger_transactions l

    LEFT JOIN bank_rollup b
        ON l.transaction_id = b.transaction_id

),

bank_only AS (

    SELECT
        b.transaction_id,
        NULL AS transaction_date,
        NULL AS account_id,
        NULL AS merchant,
        NULL AS category,
        NULL AS ledger_amount_cents,

        b.posting_date,
        b.bank_amount_cents,
        b.bank_record_count,
        b.bank_references,

        'Unexpected bank transactions'
            AS reconciliation_status,

        NULL AS difference_cents

    FROM bank_rollup b

    LEFT JOIN ledger_transactions l
        ON b.transaction_id = l.transaction_id

    WHERE l.transaction_id IS NULL

)

SELECT *
FROM ledger_comparison

UNION ALL

SELECT *
FROM bank_only

ORDER BY reconciliation_status, transaction_id;
