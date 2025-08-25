"""Tests for masking_utils.py"""

import pytest
import pandas as pd
from src.masking_utils import (
    PIIMasker, mask_email, mask_phone, mask_ssn, 
    mask_credit_card, mask_name, mask_ip, mask_field, mask_dataframe
)

# Test data
TEST_EMAIL = "test.user@example.com"
TEST_PHONE = "+1 (555) 123-4567"
TEST_SSN = "123-45-6789"
TEST_CC = "4111 1111 1111 1111"
TEST_NAME = "John Doe"
TEST_IP = "192.168.1.100"

# Test cases for PIIMasker class
def test_mask_email():
    masker = PIIMasker()
    assert masker.mask_email(TEST_EMAIL) == "XXXXXuser@example.com"
    assert masker.mask_email("a@b.c") == "X@b.c"
    assert masker.mask_email("") == ""
    assert masker.mask_email("not-an-email") == "not-an-email"

def test_mask_phone():
    masker = PIIMasker()
    assert masker.mask_phone(TEST_PHONE) == "+X (XXX) XXX-XX67"
    assert masker.mask_phone("1234567890") == "XXXXXXXX90"
    assert masker.mask_phone("") == ""
    assert masker.mask_phone("abc") == "abc"

def test_mask_ssn():
    masker = PIIMasker()
    assert masker.mask_ssn(TEST_SSN) == "XXX-XX-6789"
    assert masker.mask_ssn("123456789") == "XXX-XX-6789"
    assert masker.mask_ssn("") == ""
    assert masker.mask_ssn("abc") == "abc"

def test_mask_credit_card():
    masker = PIIMasker()
    assert masker.mask_credit_card(TEST_CC) == "XXXX XXXX XXXX 1111"
    assert masker.mask_credit_card("4111111111111111") == "XXXXXXXXXXXX1111"
    assert masker.mask_credit_card("") == ""
    assert masker.mask_credit_card("abc") == "abc"

def test_mask_name():
    masker = PIIMasker()
    assert masker.mask_name(TEST_NAME) == "JXXX DXX"
    assert masker.mask_name("A") == "A"
    assert masker.mask_name("") == ""

def test_mask_ip():
    masker = PIIMasker()
    assert masker.mask_ip(TEST_IP) == "192.XXX.X.100"
    assert masker.mask_ip("1.2.3.4") == "1.X.X.4"
    assert masker.mask_ip("") == ""
    assert masker.mask_ip("not.an.ip") == "not.an.ip"

def test_mask_field():
    masker = PIIMasker()
    assert masker.mask_field(TEST_EMAIL, "email") == "XXXXXuser@example.com"
    assert masker.mask_field(TEST_PHONE, "phone") == "+X (XXX) XXX-XX67"
    assert masker.mask_field("unknown", "unknown_type") == "XXXXXXX"

# Test convenience functions
def test_convenience_functions():
    assert mask_email(TEST_EMAIL) == "XXXXXuser@example.com"
    assert mask_phone(TEST_PHONE) == "+X (XXX) XXX-XX67"
    assert mask_ssn(TEST_SSN) == "XXX-XX-6789"
    assert mask_credit_card(TEST_CC) == "XXXX XXXX XXXX 1111"
    assert mask_name(TEST_NAME) == "JXXX DXX"
    assert mask_ip(TEST_IP) == "192.XXX.X.100"
    assert mask_field(TEST_EMAIL, "email") == "XXXXXuser@example.com"

# Test DataFrame masking
def test_mask_dataframe():
    df = pd.DataFrame({
        'name': ['John Doe', 'Jane Smith'],
        'email': ['john@example.com', 'jane@example.com'],
        'phone': ['+1555123456', '+1555765432']
    })
    
    column_types = {
        'name': 'name',
        'email': 'email',
        'phone': 'phone'
    }
    
    masked_df = mask_dataframe(df, column_types)
    
    assert masked_df['name'].tolist() == ['JXXX DXX', 'JXXX SXXXX']
    assert masked_df['email'].tolist() == ['Xohn@example.com', 'Xane@example.com']
    assert masked_df['phone'].tolist() == ['+XXXXXXXX56', '+XXXXXXXX32']
    
    # Test inplace
    masker = PIIMasker()
    masker.mask_dataframe(df, column_types, inplace=True)
    assert df['name'].tolist() == ['JXXX DXX', 'JXXX SXXXX']

# Test custom mask character
def test_custom_mask_character():
    assert mask_email(TEST_EMAIL, '*') == "*****user@example.com"
    assert mask_phone(TEST_PHONE, '#') == "+# (###) ###-##67"
    assert mask_ssn(TEST_SSN, '#') == "###-##-6789"
    assert mask_name(TEST_NAME, '#') == "J### D##"
    assert mask_ip(TEST_IP, '#') == "192.###.#.100"

# Test edge cases
def test_edge_cases():
    masker = PIIMasker()
    assert masker.mask_email(None) is None
    assert masker.mask_phone(None) is None
    assert masker.mask_ssn(None) is None
    assert masker.mask_credit_card(None) is None
    assert masker.mask_name(None) is None
    assert masker.mask_ip(None) is None
    assert masker.mask_field(None, "email") is None
    
    # Test with empty strings
    assert masker.mask_email("") == ""
    assert masker.mask_phone("") == ""
    assert masker.mask_ssn("") == ""
    assert masker.mask_credit_card("") == ""
    assert masker.mask_name("") == ""
    assert masker.mask_ip("") == ""
    assert masker.mask_field("", "email") == ""
