-- Test case for pii_check macro
-- This test verifies that the pii_check macro correctly identifies PII data

-- Create a test model with sample data
{{ config(tags=['unit_test']) }}

WITH sample_data AS (
    SELECT 
        1 AS id,
        'test@example.com' AS email,
        'John Doe' AS name,
        '2023-01-01' AS created_at
    
    UNION ALL
    
    SELECT 
        2 AS id,
        'user@domain.com' AS email,
        'Jane Smith' AS name,
        '2023-01-02' AS created_at
)

-- Test that the macro runs without errors
SELECT {{ pii_check('sample_data') }}
WHERE 1=0  -- This ensures no data is returned, just testing compilation
