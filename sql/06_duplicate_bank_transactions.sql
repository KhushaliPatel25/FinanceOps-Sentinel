
-- ==============================================
-- FINANCEOPS SENTINEL
-- DUPLICATE BANK TRANSACTION DETECTION
-- ==============================================

WITH duplicate_transactions AS (

    SELECT
        transaction_id,

        COUNT(*) AS bank_record_count,

        GROUP_CONCAT(
            bank_reference, ', '
        ) AS bank_references,

        MIN(bank_amount_cents) AS single_amount_cents,

        SUM(bank_amount_cents)
            - MIN(bank_amount_cents)
            AS potential_excess_cents

    FROM bank_transactions

    GROUP BY transaction_id

    HAVING COUNT(*) > 1

)

SELECT
    transaction_id,

    bank_record_count,

    bank_references,

    printf(
        '%.2f',
        single_amount_cents / 100.0
    ) AS bank_amount_cad,

    printf(
        '%.2f',
        potential_excess_cents / 100.0
    ) AS potential_excess_cad,

    COUNT(*) OVER ()
        AS total_duplicate_transaction_ids

FROM duplicate_transactions

ORDER BY transaction_id;
