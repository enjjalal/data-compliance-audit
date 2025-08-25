"""
Access logs simulator for GDPR/PII compliance auditing.
Generates realistic data access logs with user roles and timestamps.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd


class AccessLogsSimulator:
    """Simulates realistic data access logs for compliance auditing."""
    
    def __init__(self):
        self.users = [
            "analyst_john", "data_scientist_sarah", "marketing_amy", 
            "compliance_officer_mike", "engineer_lisa", "manager_david",
            "auditor_emma", "developer_tom", "analyst_rachel", "admin_sam"
        ]
        
        self.roles = {
            "analyst_john": "data_analyst",
            "data_scientist_sarah": "data_scientist", 
            "marketing_amy": "marketing",
            "compliance_officer_mike": "compliance",
            "engineer_lisa": "data_engineer",
            "manager_david": "management",
            "auditor_emma": "audit",
            "developer_tom": "developer",
            "analyst_rachel": "data_analyst",
            "admin_sam": "administrator"
        }
        
        self.tables = ["users", "transactions", "logs", "marketing_emails"]
        self.actions = ["SELECT", "EXPORT", "VIEW", "ANALYZE", "BACKUP", "RESTORE"]
        
        # Sensitive tables that require special access
        self.sensitive_tables = ["users", "marketing_emails"]
        
        # Access patterns by role
        self.role_access_patterns = {
            "data_analyst": {"users": 0.8, "transactions": 0.9, "logs": 0.6, "marketing_emails": 0.3},
            "data_scientist": {"users": 0.9, "transactions": 0.95, "logs": 0.8, "marketing_emails": 0.7},
            "marketing": {"users": 0.4, "transactions": 0.3, "logs": 0.2, "marketing_emails": 0.9},
            "compliance": {"users": 0.9, "transactions": 0.8, "logs": 0.9, "marketing_emails": 0.8},
            "data_engineer": {"users": 0.7, "transactions": 0.8, "logs": 0.9, "marketing_emails": 0.5},
            "management": {"users": 0.6, "transactions": 0.7, "logs": 0.5, "marketing_emails": 0.6},
            "audit": {"users": 0.95, "transactions": 0.9, "logs": 0.95, "marketing_emails": 0.9},
            "developer": {"users": 0.8, "transactions": 0.7, "logs": 0.8, "marketing_emails": 0.6},
            "administrator": {"users": 0.9, "transactions": 0.8, "logs": 0.9, "marketing_emails": 0.8}
        }
    
    def generate_access_logs(self, days: int = 30, avg_daily_access: int = 50) -> pd.DataFrame:
        """Generate realistic access logs over specified period."""
        
        logs = []
        start_date = datetime.now() - timedelta(days=days)
        
        for _ in range(days * avg_daily_access):
            # Random timestamp within the day
            random_days = random.uniform(0, days)
            random_seconds = random.uniform(0, 24 * 3600)
            timestamp = start_date + timedelta(days=random_days, seconds=random_seconds)
            
            # Select user and determine access
            user = random.choice(self.users)
            role = self.roles[user]
            
            # Select table based on role access patterns
            table = self._select_table_by_role(role)
            action = self._select_action_by_role_and_table(role, table)
            
            # Generate access details
            access_details = self._generate_access_details(user, role, table, action)
            
            logs.append({
                'timestamp': timestamp.isoformat(),
                'user_id': user,
                'user_role': role,
                'table_name': table,
                'action': action,
                'access_details': access_details,
                'ip_address': self._generate_ip_for_user(user),
                'session_id': f"session_{random.randint(1000, 9999)}",
                'compliance_level': self._get_compliance_level(role, table, action)
            })
        
        # Sort by timestamp
        df = pd.DataFrame(logs)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        return df
    
    def _select_table_by_role(self, role: str) -> str:
        """Select table based on role access patterns."""
        patterns = self.role_access_patterns.get(role, {})
        if not patterns:
            return random.choice(self.tables)
        
        # Weighted selection based on access patterns
        tables = list(patterns.keys())
        weights = list(patterns.values())
        return random.choices(tables, weights=weights)[0]
    
    def _select_action_by_role_and_table(self, role: str, table: str) -> str:
        """Select action based on role and table sensitivity."""
        if table in self.sensitive_tables and role in ["marketing", "developer"]:
            # Limit sensitive actions for certain roles
            return random.choice(["SELECT", "VIEW"])
        elif role == "compliance" or role == "audit":
            # Compliance and audit roles can do everything
            return random.choice(self.actions)
        else:
            # Other roles have standard access
            return random.choice(["SELECT", "VIEW", "ANALYZE"])
    
    def _generate_access_details(self, user: str, role: str, table: str, action: str) -> str:
        """Generate detailed access information."""
        if action == "EXPORT":
            return f"Exported {random.randint(100, 10000)} rows for {role} analysis"
        elif action == "SELECT":
            return f"Queried {random.randint(1, 1000)} records with filters"
        elif action == "VIEW":
            return f"Viewed table structure and sample data"
        elif action == "ANALYZE":
            return f"Performed {role} analysis on {table} data"
        elif action == "BACKUP":
            return f"Created backup of {table} table"
        else:
            return f"Standard {action} operation on {table}"
    
    def _generate_ip_for_user(self, user: str) -> str:
        """Generate consistent IP addresses for users."""
        # Simple hash-based IP generation for consistency
        user_hash = hash(user) % 254
        return f"192.168.1.{user_hash + 1}"
    
    def _get_compliance_level(self, role: str, table: str, action: str) -> str:
        """Determine compliance level of the access."""
        if role in ["compliance", "audit"]:
            return "compliant"
        elif table in self.sensitive_tables and action in ["EXPORT", "BACKUP"]:
            return "review_required"
        elif action == "EXPORT":
            return "monitored"
        else:
            return "standard"
    
    def generate_lineage_data(self, access_logs: pd.DataFrame) -> Dict:
        """Generate data lineage information from access logs."""
        
        lineage = {
            'data_flows': [],
            'user_access_summary': {},
            'table_access_summary': {},
            'compliance_issues': []
        }
        
        # User access summary
        for user in self.users:
            user_logs = access_logs[access_logs['user_id'] == user]
            lineage['user_access_summary'][user] = {
                'total_accesses': len(user_logs),
                'tables_accessed': user_logs['table_name'].nunique(),
                'last_access': user_logs['timestamp'].max() if len(user_logs) > 0 else None,
                'role': self.roles[user],
                'compliance_level': user_logs['compliance_level'].value_counts().to_dict()
            }
        
        # Table access summary
        for table in self.tables:
            table_logs = access_logs[access_logs['table_name'] == table]
            lineage['table_access_summary'][table] = {
                'total_accesses': len(table_logs),
                'unique_users': table_logs['user_id'].nunique(),
                'actions_performed': table_logs['action'].value_counts().to_dict(),
                'last_accessed': table_logs['timestamp'].max() if len(table_logs) > 0 else None,
                'is_sensitive': table in self.sensitive_tables
            }
        
        # Identify potential compliance issues
        export_logs = access_logs[access_logs['action'] == 'EXPORT']
        for _, log in export_logs.iterrows():
            if log['table_name'] in self.sensitive_tables:
                lineage['compliance_issues'].append({
                    'timestamp': log['timestamp'],
                    'user': log['user_id'],
                    'role': log['user_role'],
                    'table': log['table_name'],
                    'issue': f"Sensitive table {log['table_name']} exported by {log['user_role']}",
                    'severity': 'high' if log['user_role'] in ['marketing', 'developer'] else 'medium'
                })
        
        return lineage


def main() -> None:
    """Generate access logs and lineage data."""
    
    simulator = AccessLogsSimulator()
    
    # Generate access logs
    print("📊 Generating access logs...")
    access_logs = simulator.generate_access_logs(days=30, avg_daily_access=60)
    
    # Save access logs
    logs_path = Path("data/access_logs.csv")
    logs_path.parent.mkdir(parents=True, exist_ok=True)
    access_logs.to_csv(logs_path, index=False)
    
    print(f"💾 Access logs saved to: {logs_path}")
    print(f"   Total access records: {len(access_logs)}")
    print(f"   Date range: {access_logs['timestamp'].min()} to {access_logs['timestamp'].max()}")
    
    # Generate lineage data
    print("\n🔗 Generating data lineage...")
    lineage_data = simulator.generate_lineage_data(access_logs)
    
    # Save lineage data
    lineage_path = Path("outputs/data_lineage.json")
    lineage_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(lineage_path, 'w', encoding='utf-8') as f:
        json.dump(lineage_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Data lineage saved to: {lineage_path}")
    
    # Print summary
    print(f"\n📈 Access Summary:")
    print(f"   Users: {len(simulator.users)}")
    print(f"   Tables: {len(simulator.tables)}")
    print(f"   Sensitive tables: {len(simulator.sensitive_tables)}")
    print(f"   Compliance issues found: {len(lineage_data['compliance_issues'])}")
    
    # Show some sample data
    print(f"\n📋 Sample access logs:")
    print(access_logs.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
