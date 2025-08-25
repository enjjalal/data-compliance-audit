-- Test the pii_check macro with actual data verification

-- Set up test data
{% set test_table = create_test_data() %}

-- Test that the macro identifies PII columns correctly
WITH detected_pii AS (
    {{ pii_check(test_table) }}
)

SELECT 
    'test_pii_check_macro' AS test_name,
    CASE 
        WHEN (SELECT COUNT(*) FROM detected_pii) > 0 THEN 'PASS'
        ELSE 'FAIL: No PII detected in test data'
    END AS test_result

UNION ALL

-- Test that the macro correctly identifies specific PII types
SELECT 
    'pii_type_detection' AS test_name,
    CASE 
        WHEN (
            SELECT COUNT(*) 
            FROM detected_pii 
            WHERE column_name IN ('email', 'full_name', 'phone_number', 'ssn', 'ip_address', 'date_of_birth')
        ) >= 6 THEN 'PASS'
        ELSE 'FAIL: Not all PII types were detected'
    END AS test_result

-- Clean up test data
{{ cleanup_test_data() }}
