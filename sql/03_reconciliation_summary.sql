
-- ==============================================
-- FINANCEOPS SENTINEL
-- TRANSACTION RECONCILIATION SUMMARY
-- ==============================================

WITH bank_rollup AS (

    -- Count how many bank records exist
    -- for each transaction ID

    SELECT
        transaction_id,
        COUNT(*) AS bank_record_count,
        MIN(bank_amount_cents) AS bank_amount_cents

    FROM bank_transactions

    GROUP BY transaction_id

),

ledger_status AS (

    -- Compare ledger transactions against bank data

    SELECT
        l.transaction_id,

        CASE
            WHEN b.transaction_id IS NULL
                THEN 'Missing from bank'

            WHEN b.bank_record_count > 1
                THEN 'Duplicate bank records'

            WHEN l.amount_cents != b.bank_amount_cents
                THEN 'Amount mismatch'

            ELSE 'Matched'
        END AS reconciliation_status

    FROM ledger_transactions l

    LEFT JOIN bank_rollup b
        ON l.transaction_id = b.transaction_id

),

reconciliation_summary AS (

    -- Successfully matched transactions

    SELECT
        1 AS sort_order,
        'Matched' AS status,
        COUNT(*) AS transaction_count
    FROM ledger_status
    WHERE reconciliation_status = 'Matched'

    UNION ALL

    -- Missing bank transactions

    SELECT
        2,
        'Missing from bank',
        COUNT(*)
    FROM ledger_status
    WHERE reconciliation_status = 'Missing from bank'

    UNION ALL

    -- Amount mismatches

    SELECT
        3,
        'Amount mismatch',
        COUNT(*)
    FROM ledger_status
    WHERE reconciliation_status = 'Amount mismatch'

    UNION ALL

    -- Duplicate bank transaction IDs

    SELECT
        4,
        'Duplicate bank records',
        COUNT(*)
    FROM ledger_status
    WHERE reconciliation_status = 'Duplicate bank records'

    UNION ALL

    -- Bank transactions without ledger records

    SELECT
        5,
        'Unexpected bank transactions',
        COUNT(*)

    FROM bank_rollup b

    LEFT JOIN ledger_transactions l
        ON b.transaction_id = l.transaction_id

    WHERE l.transaction_id IS NULL

)

-- Display final reconciliation results

SELECT
    status,
    transaction_count

FROM reconciliation_summary

ORDER BY sort_order;
