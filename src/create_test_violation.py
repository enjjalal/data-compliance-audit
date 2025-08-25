"""
Create a test violation to demonstrate the alerting system.
This simulates finding a new compliance issue.
"""

import pandas as pd
from pathlib import Path


def create_test_violation() -> None:
    """Create a test violation to demonstrate alerting."""
    
    # Create a test violation
    test_violation = {
        'policy_id': 'no_pii_in_logs',
        'table': 'logs',
        'column': 'user_email',  # This shouldn't exist in logs
        'pii_tags': 'email',
        'reason': 'PII email found in logs table - policy violation'
    }
    
    # Save to violations.csv
    violations_df = pd.DataFrame([test_violation])
    violations_df.to_csv("outputs/violations.csv", index=False)
    
    print("🚨 Test violation created:")
    print(f"   Policy: {test_violation['policy_id']}")
    print(f"   Table: {test_violation['table']}")
    print(f"   Column: {test_violation['column']}")
    print(f"   Reason: {test_violation['reason']}")
    print(f"   Saved to: outputs/violations.csv")
    print("\nNow run: python src/violation_tracker.py")


if __name__ == "__main__":
    create_test_violation()
