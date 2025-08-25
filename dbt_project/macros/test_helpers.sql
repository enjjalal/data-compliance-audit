{% macro create_test_data() %}
    -- Create a test table with various PII and non-PII columns
    {% set create_table_sql %}
        CREATE OR REPLACE TABLE {{ target.schema }}.test_pii_data AS
        SELECT 
            1 AS id,
            'test@example.com' AS email,
            'John Doe' AS full_name,
            '555-123-4567' AS phone_number,
            '123-45-6789' AS ssn,
            '192.168.1.1' AS ip_address,
            '1990-01-01' AS date_of_birth,
            'non-sensitive data' AS description,
            42 AS user_id
        
        UNION ALL
        
        SELECT 
            2 AS id,
            'user@domain.com' AS email,
            'Jane Smith' AS full_name,
            '(555) 987-6543' AS phone_number,
            '987-65-4321' AS ssn,
            '10.0.0.1' AS ip_address,
            '1985-12-31' AS date_of_birth,
            'another non-sensitive data' AS description,
            84 AS user_id
    {% endset %}
    
    {% do run_query(create_table_sql) %}
    
    -- Return the table name for use in tests
    {{ return(target.schema ~ '.test_pii_data') }}
{% endmacro %}

{% macro cleanup_test_data() %}
    -- Clean up test data
    {% set drop_table_sql %}
        DROP TABLE IF EXISTS {{ target.schema }}.test_pii_data
    {% endset %}
    
    {% do run_query(drop_table_sql) %}
{% endmacro %}
