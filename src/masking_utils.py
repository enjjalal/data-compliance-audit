"""
Data masking utilities for PII (Personally Identifiable Information).
Provides functions to mask sensitive data while preserving format.
"""

import re
import random
import string
from typing import Any, Dict, Optional, Union

class PIIMasker:
    """Class for masking PII data while preserving format."""
    
    def __init__(self):
        # Character sets for masking
        self.digits = string.digits
        self.letters = string.ascii_letters
        self.alphanumeric = self.digits + self.letters
        
        # Default masking character
        self.mask_char = 'X'
        
        # Preserve last n characters when masking
        self.preserve_last = {
            'email': 4,       # Preserve last 4 chars of email
            'phone': 2,       # Preserve last 2 digits of phone
            'ssn': 4,         # Preserve last 4 of SSN
            'credit_card': 4,  # Preserve last 4 of credit card
        }
    
    def mask_email(self, email: str, mask_char: Optional[str] = None) -> str:
        """Mask an email address while preserving the domain."""
        if not email or '@' not in email:
            return email
            
        mask_char = mask_char or self.mask_char
        username, domain = email.split('@')
        preserve = min(self.preserve_last['email'], len(username) - 1)
        
        if preserve > 0:
            masked = f"{mask_char * (len(username) - preserve)}{username[-preserve:]}@{domain}"
        else:
            masked = f"{mask_char * len(username)}@{domain}"
            
        return masked
    
    def mask_phone(self, phone: str, mask_char: Optional[str] = None) -> str:
        """Mask a phone number while preserving the last few digits."""
        if not phone:
            return phone
            
        mask_char = mask_char or self.mask_char
        
        # Remove all non-digit characters for processing
        digits = re.sub(r'\D', '', phone)
        if not digits:
            return phone
            
        preserve = min(self.preserve_last['phone'], len(digits) - 1)
        # Mask all but the last 'preserve' digits
        masked = f"{mask_char * (len(digits) - preserve)}{digits[-preserve:]}"
        
        # Try to preserve the original format
        if len(phone) > len(digits):
            # Re-insert non-digit characters from the end
            result = []
            d_pos = len(digits) - 1
            m_pos = len(masked) - 1
            
            for c in reversed(phone):
                if c.isdigit():
                    if m_pos >= 0:
                        result.append(masked[m_pos])
                        m_pos -= 1
                    d_pos -= 1
                else:
                    result.append(c)
            
            return ''.join(reversed(result))
        
        return masked
    
    def mask_ssn(self, ssn: str, mask_char: Optional[str] = None) -> str:
        """Mask a Social Security Number, preserving last 4 digits."""
        if not ssn:
            return ssn
            
        mask_char = mask_char or self.mask_char
        digits = re.sub(r'\D', '', ssn)
        
        if not digits:
            return ssn
            
        preserve = min(self.preserve_last['ssn'], len(digits))
        masked = f"{mask_char * (len(digits) - preserve)}{digits[-preserve:]}"
        
        # Format as XXX-XX-1234 if it looks like an SSN
        if len(digits) == 9:
            masked = f"{masked[:3]}-{masked[3:5]}-{masked[5:]}"
            
        return masked
    
    def mask_credit_card(self, card: str, mask_char: Optional[str] = None) -> str:
        """Mask a credit card number, preserving last 4 digits."""
        if not card:
            return card
            
        mask_char = mask_char or self.mask_char
        digits = re.sub(r'\D', '', card)
        
        if not digits:
            return card
            
        preserve = min(self.preserve_last['credit_card'], len(digits))
        masked = f"{mask_char * (len(digits) - preserve)}{digits[-preserve:]}"
        
        # Add spaces every 4 digits if the original had them
        if '-' in card or ' ' in card:
            masked = ' '.join([masked[i:i+4] for i in range(0, len(masked), 4)])
            
        return masked
    
    def mask_name(self, name: str, mask_char: Optional[str] = None) -> str:
        """Mask a person's name, preserving the first letter."""
        if not name:
            return name
            
        mask_char = mask_char or self.mask_char
        parts = name.split()
        masked_parts = []
        
        for part in parts:
            if len(part) > 1:
                masked = f"{part[0]}{mask_char * (len(part) - 1)}"
            else:
                masked = part
            masked_parts.append(masked)
            
        return ' '.join(masked_parts)
    
    def mask_ip(self, ip: str, mask_char: Optional[str] = None) -> str:
        """Mask an IP address."""
        if not ip:
            return ip
            
        mask_char = mask_char or self.mask_char
        parts = ip.split('.')
        
        if len(parts) != 4:
            return ip
            
        return f"{parts[0]}.{mask_char * len(parts[1])}.{mask_char * len(parts[2])}.{parts[3]}"
    
    def mask_field(self, value: Any, field_type: str, mask_char: Optional[str] = None) -> str:
        """Generic masking function that routes to the appropriate masking method."""
        if not value:
            return value
            
        value = str(value)
        mask_char = mask_char or self.mask_char
        
        mask_methods = {
            'email': self.mask_email,
            'phone': self.mask_phone,
            'ssn': self.mask_ssn,
            'credit_card': self.mask_credit_card,
            'name': self.mask_name,
            'ip': self.mask_ip,
        }
        
        mask_func = mask_methods.get(field_type.lower())
        if mask_func:
            return mask_func(value, mask_char)
            
        # Default: mask everything
        return mask_char * len(value)
    
    def mask_dataframe(self, df, column_types: Dict[str, str], inplace: bool = False):
        """Mask PII data in a pandas DataFrame."""
        import pandas as pd
        
        if not inplace:
            df = df.copy()
            
        for column, field_type in column_types.items():
            if column in df.columns:
                df[column] = df[column].apply(
                    lambda x: self.mask_field(x, field_type)
                )
                
        return df if not inplace else None

# Singleton instance for convenience
masker = PIIMasker()

def mask_email(email: str, mask_char: str = 'X') -> str:
    """Mask an email address."""
    return masker.mask_email(email, mask_char)

def mask_phone(phone: str, mask_char: str = 'X') -> str:
    """Mask a phone number."""
    return masker.mask_phone(phone, mask_char)

def mask_ssn(ssn: str, mask_char: str = 'X') -> str:
    """Mask a Social Security Number."""
    return masker.mask_ssn(ssn, mask_char)

def mask_credit_card(card: str, mask_char: str = 'X') -> str:
    """Mask a credit card number."""
    return masker.mask_credit_card(card, mask_char)

def mask_name(name: str, mask_char: str = 'X') -> str:
    """Mask a person's name."""
    return masker.mask_name(name, mask_char)

def mask_ip(ip: str, mask_char: str = 'X') -> str:
    """Mask an IP address."""
    return masker.mask_ip(ip, mask_char)

def mask_field(value: Any, field_type: str, mask_char: str = 'X') -> str:
    """Generic masking function."""
    return masker.mask_field(value, field_type, mask_char)

def mask_dataframe(df, column_types: Dict[str, str], inplace: bool = False):
    """Mask PII data in a pandas DataFrame.
    
    Args:
        df: Input DataFrame
        column_types: Dictionary mapping column names to PII types
        inplace: Whether to modify the DataFrame in place
            
    Returns:
        Masked DataFrame if inplace=False, None otherwise
    """
    return masker.mask_dataframe(df, column_types, inplace)
