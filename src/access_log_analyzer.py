"""
Simple access log analyzer for quick insights and compliance checks.
Provides command-line analysis of access patterns and potential issues.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List


def analyze_access_logs(logs_path: str = "data/access_logs.csv") -> None:
    """Analyze access logs and provide insights."""
    
    if not Path(logs_path).exists():
        print(f"❌ Access logs not found at {logs_path}")
        return
    
    # Load access logs
    df = pd.read_csv(logs_path)
    print(f"📊 Loaded {len(df):,} access records")
    
    # Basic statistics
    print(f"\n📈 Basic Statistics:")
    print(f"   Date range: {df['timestamp'].min()[:10]} to {df['timestamp'].max()[:10]}")
    print(f"   Unique users: {df['user_id'].nunique()}")
    print(f"   Unique tables: {df['table_name'].nunique()}")
    print(f"   Total actions: {df['action'].nunique()}")
    
    # User activity analysis
    print(f"\n👥 User Activity Analysis:")
    user_activity = df.groupby('user_id').agg({
        'timestamp': 'count',
        'table_name': 'nunique',
        'action': 'nunique'
    }).rename(columns={
        'timestamp': 'total_accesses',
        'table_name': 'tables_accessed',
        'action': 'actions_performed'
    }).sort_values('total_accesses', ascending=False)
    
    print(user_activity.head(10).to_string())
    
    # Table access analysis
    print(f"\n📋 Table Access Analysis:")
    table_activity = df.groupby('table_name').agg({
        'timestamp': 'count',
        'user_id': 'nunique',
        'action': 'nunique'
    }).rename(columns={
        'timestamp': 'total_accesses',
        'user_id': 'unique_users',
        'action': 'actions_performed'
    }).sort_values('total_accesses', ascending=False)
    
    print(table_activity.to_string())
    
    # Action analysis
    print(f"\n🔧 Action Analysis:")
    action_counts = df['action'].value_counts()
    print(action_counts.to_string())
    
    # Compliance analysis
    print(f"\n🚨 Compliance Analysis:")
    compliance_issues = df[df['compliance_level'] != 'standard']
    if len(compliance_issues) > 0:
        print(f"   Found {len(compliance_issues)} compliance issues:")
        for level in compliance_issues['compliance_level'].unique():
            count = len(compliance_issues[compliance_issues['compliance_level'] == level])
            print(f"     {level}: {count}")
        
        # Show high-risk activities
        high_risk = compliance_issues[compliance_issues['compliance_level'] == 'review_required']
        if len(high_risk) > 0:
            print(f"\n   High-risk activities requiring review:")
            for _, row in high_risk.head(5).iterrows():
                print(f"     {row['timestamp'][:10]} - {row['user_id']} ({row['user_role']}) "
                      f"performed {row['action']} on {row['table_name']}")
    else:
        print("   ✅ No compliance issues detected")
    
    # Role-based analysis
    print(f"\n🎭 Role-Based Access Patterns:")
    role_analysis = df.groupby('user_role').agg({
        'timestamp': 'count',
        'table_name': 'nunique',
        'user_id': 'nunique'
    }).rename(columns={
        'timestamp': 'total_accesses',
        'table_name': 'tables_accessed',
        'user_id': 'unique_users'
    }).sort_values('total_accesses', ascending=False)
    
    print(role_analysis.to_string())
    
    # Export analysis
    print(f"\n📤 Export Activity Analysis:")
    exports = df[df['action'] == 'EXPORT']
    if len(exports) > 0:
        print(f"   Total exports: {len(exports)}")
        export_by_table = exports.groupby('table_name').size().sort_values(ascending=False)
        print(f"   Exports by table:")
        for table, count in export_by_table.items():
            print(f"     {table}: {count}")
        
        # Check for sensitive table exports
        sensitive_exports = exports[exports['table_name'].isin(['users', 'marketing_emails'])]
        if len(sensitive_exports) > 0:
            print(f"\n   ⚠️  Sensitive table exports detected:")
            for _, row in sensitive_exports.head(5).iterrows():
                print(f"     {row['timestamp'][:10]} - {row['user_id']} ({row['user_role']}) "
                      f"exported {row['table_name']}")
    else:
        print("   No export activity detected")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    # Check for unusual access patterns
    high_access_users = user_activity[user_activity['total_accesses'] > user_activity['total_accesses'].mean() * 2]
    if len(high_access_users) > 0:
        print(f"   🔍 Review high-access users: {', '.join(high_access_users.index.tolist())}")
    
    # Check for sensitive table access by non-compliance roles
    sensitive_access = df[(df['table_name'].isin(['users', 'marketing_emails'])) & 
                         (~df['user_role'].isin(['compliance', 'audit', 'administrator']))]
    if len(sensitive_access) > 0:
        print(f"   🔒 Review sensitive table access by non-compliance roles")
    
    # Check for export activities
    if len(exports) > 0:
        print(f"   📋 Monitor export activities, especially for sensitive tables")
    
    print(f"\n📁 Detailed reports available:")
    print(f"   - Lineage visualization: outputs/lineage_visualization.html")
    print(f"   - Data lineage: outputs/data_lineage.json")
    print(f"   - Access logs: {logs_path}")


def main() -> None:
    """Main function to analyze access logs."""
    analyze_access_logs()


if __name__ == "__main__":
    main()
