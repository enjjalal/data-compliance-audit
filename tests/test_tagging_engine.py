"""Tests for the PII tagging engine."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from tagging_engine import (
    detect_by_name,
    detect_by_values,
    scan_dataframe,
    ColumnPIIResult,
    PII_COLUMN_NAME_PATTERNS,
    PII_VALUE_REGEXES
)

# Test data
@pytest.fixture
def test_data():
    """Sample test data for PII detection."""
    return pd.DataFrame({
        'user_email': ['test@example.com', 'user@domain.com', 'another@test.co'],
        'phone_number': ['+1-555-123-4567', '(555) 987-6543', '555-111-2222'],
        'ip_address': ['192.168.1.1', '10.0.0.1', '172.16.254.1'],
        'date_of_birth': ['1990-01-01', '1985-12-31', '2000-06-15'],
        'full_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'ssn': ['123-45-6789', '987-65-4321', '456-78-9012'],
        'non_pii_column': [1, 2, 3],
        'empty_column': [None, None, None]
    })

# Test cases for detect_by_name
def test_detect_by_name_emails():
    """Test email pattern detection in column names."""
    assert detect_by_name('email') == 'email'
    assert detect_by_name('user_email') == 'email'
    assert detect_by_name('e_mail') == 'email'
    assert detect_by_name('contact_email') == 'email'

def test_detect_by_name_phones():
    """Test phone number pattern detection in column names."""
    assert detect_by_name('phone') == 'phone'
    assert detect_by_name('phone_number') == 'phone'
    assert detect_by_name('mobile') == 'phone'

def test_detect_by_name_ips():
    """Test IP address pattern detection in column names."""
    assert detect_by_name('ip') == 'ip'
    assert detect_by_name('ip_address') == 'ip'
    assert detect_by_name('ip-address') == 'ip'

def test_detect_by_name_no_match():
    """Test non-matching column names."""
    assert detect_by_name('username') is None
    assert detect_by_name('user_id') is None
    assert detect_by_name('description') is None

# Test cases for detect_by_values
def test_detect_by_values_email(test_data):
    """Test email pattern detection in values."""
    assert detect_by_values(test_data['user_email']) == 'email'

def test_detect_by_values_phone(test_data):
    """Test phone number pattern detection in values."""
    assert detect_by_values(test_data['phone_number']) == 'phone'

def test_detect_by_values_ip(test_data):
    """Test IP address pattern detection in values."""
    assert detect_by_values(test_data['ip_address']) == 'ip'

def test_detect_by_values_dob(test_data):
    """Test date of birth pattern detection in values."""
    assert detect_by_values(test_data['date_of_birth']) == 'dob'

def test_detect_by_values_ssn(test_data):
    """Test SSN pattern detection in values."""
    assert detect_by_values(test_data['ssn']) == 'national_id'

def test_detect_by_values_no_pii():
    """Test non-PII values."""
    non_pii_data = pd.Series(['apple', 'banana', 'orange'])
    assert detect_by_values(non_pii_data) is None

def test_detect_by_values_empty():
    """Test empty series."""
    empty_series = pd.Series([], dtype=object)
    assert detect_by_values(empty_series) is None

# Test cases for scan_dataframe
def test_scan_dataframe(test_data):
    """Test scanning a complete dataframe."""
    results = scan_dataframe(test_data, 'test_table')
    
    # Check that we have the expected number of results
    assert len(results) == 6  # 6 PII columns in test data
    
    # Check that each PII type was detected
    detected_types = {r.detected_tags[0] for r in results}
    assert 'email' in detected_types
    assert 'phone' in detected_types
    assert 'ip' in detected_types
    assert 'dob' in detected_types
    assert 'name' in detected_types
    assert 'national_id' in detected_types
    
    # Check that non-PII columns were not included
    non_pii_columns = [r.column for r in results 
                      if 'non_pii_column' in r.column or 'empty_column' in r.column]
    assert not non_pii_columns

def test_scan_empty_dataframe():
    """Test scanning an empty dataframe."""
    empty_df = pd.DataFrame()
    results = scan_dataframe(empty_df, 'empty_table')
    assert results == []

# Test edge cases
def test_mixed_pii_values():
    """Test with mixed PII and non-PII values."""
    mixed_data = pd.DataFrame({
        'mixed_column': ['test@example.com', 'not_an_email', 'user@domain.com', '12345']
    })
    results = scan_dataframe(mixed_data, 'mixed_table')
    assert len(results) == 1
    assert results[0].detected_tags == ['email']

def test_case_insensitivity():
    """Test case insensitivity in column names."""
    df = pd.DataFrame({
        'UserEmail': ['test@example.com'],
        'PHONE_NUMBER': ['+1-555-123-4567'],
        'IpAddress': ['192.168.1.1']
    })
    results = scan_dataframe(df, 'case_test')
    assert len(results) == 3
    
    detected_columns = {r.column: r.detected_tags[0] for r in results}
    assert detected_columns['UserEmail'] == 'email'
    assert detected_columns['PHONE_NUMBER'] == 'phone'
    assert detected_columns['IpAddress'] == 'ip'
