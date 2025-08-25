"""
Example script demonstrating the use of masking utilities.
"""

import pandas as pd
from src.masking_utils import (
    mask_email, mask_phone, mask_ssn, mask_credit_card,
    mask_name, mask_ip, mask_dataframe, PIIMasker
)

def demo_individual_masking():
    """Demonstrate masking individual values."""
    print("=== Individual Value Masking ===")
    
    # Example data
    email = "john.doe@example.com"
    phone = "+1 (555) 123-4567"
    ssn = "123-45-6789"
    credit_card = "4111 1111 1111 1111"
    name = "John Doe"
    ip = "192.168.1.100"
    
    # Mask individual values
    print(f"Email: {email} -> {mask_email(email)}")
    print(f"Phone: {phone} -> {mask_phone(phone)}")
    print(f"SSN: {ssn} -> {mask_ssn(ssn)}")
    print(f"Credit Card: {credit_card} -> {mask_credit_card(credit_card)}")
    print(f"Name: {name} -> {mask_name(name)}")
    print(f"IP: {ip} -> {mask_ip(ip)}")
    
    # Using custom mask character
    print("\nWith custom mask character (█):")
    print(f"Email: {email} -> {mask_email(email, '█')}")
    print(f"Name: {name} -> {mask_name(name, '█')}")

def demo_dataframe_masking():
    """Demonstrate masking a pandas DataFrame."""
    print("\n=== DataFrame Masking ===")
    
    # Create sample data
    data = {
        'id': [1, 2, 3],
        'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'email': ['john@example.com', 'jane@company.org', 'bob@test.net'],
        'phone': ['+1555123456', '+1555765432', '+1555987654'],
        'ssn': ['123-45-6789', '987-65-4321', '456-78-9012'],
        'credit_card': ['4111 1111 1111 1111', '5555 5555 5555 4444', '3782 822463 10005'],
        'ip_address': ['192.168.1.1', '10.0.0.1', '172.16.254.1']
    }
    
    df = pd.DataFrame(data)
    
    print("\nOriginal DataFrame:")
    print(df)
    
    # Define which columns contain PII and their types
    column_types = {
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'ssn': 'ssn',
        'credit_card': 'credit_card',
        'ip_address': 'ip'
    }
    
    # Mask the DataFrame
    masked_df = mask_dataframe(df, column_types)
    
    print("\nMasked DataFrame:")
    print(masked_df)

def demo_custom_masking_rules():
    """Demonstrate using custom masking rules."""
    print("\n=== Custom Masking Rules ===")
    
    # Create a custom masker with different settings
    custom_masker = PIIMasker()
    custom_masker.mask_char = '#'  # Use # instead of X
    custom_masker.preserve_last = {
        'email': 0,       # Don't preserve any part of the email
        'phone': 0,       # Don't preserve any digits
        'ssn': 2,         # Preserve last 2 digits of SSN
        'credit_card': 4,  # Preserve last 4 digits (default)
    }
    
    # Example data
    email = "john.doe@example.com"
    phone = "+1 (555) 123-4567"
    ssn = "123-45-6789"
    credit_card = "4111 1111 1111 1111"
    
    print(f"Email: {email} -> {custom_masker.mask_email(email)}")
    print(f"Phone: {phone} -> {custom_masker.mask_phone(phone)}")
    print(f"SSN: {ssn} -> {custom_masker.mask_ssn(ssn)}")
    print(f"Credit Card: {credit_card} -> {custom_masker.mask_credit_card(credit_card)}")

if __name__ == "__main__":
    demo_individual_masking()
    demo_dataframe_masking()
    demo_custom_masking_rules()
