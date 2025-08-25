"""
Data lineage visualizer for GDPR/PII compliance auditing.
Generates HTML reports showing data flows, access patterns, and compliance issues.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd


class LineageVisualizer:
    """Visualizes data lineage and access patterns."""
    
    def __init__(self):
        self.access_logs_path = Path("data/access_logs.csv")
        self.lineage_path = Path("outputs/data_lineage.json")
    
    def load_data(self) -> Dict:
        """Load access logs and lineage data."""
        data = {}
        
        if self.access_logs_path.exists():
            data['access_logs'] = pd.read_csv(self.access_logs_path)
        
        if self.lineage_path.exists():
            with open(self.lineage_path, 'r', encoding='utf-8') as f:
                data['lineage'] = json.load(f)
        
        return data
    
    def generate_access_heatmap(self, access_logs: pd.DataFrame) -> str:
        """Generate HTML heatmap of table access by user role."""
        
        # Create pivot table for heatmap
        pivot = pd.pivot_table(
            access_logs, 
            values='timestamp',  # Count of accesses
            index='user_role',
            columns='table_name',
            aggfunc='count',
            fill_value=0
        )
        
        # Generate heatmap HTML
        html = """
        <div class="heatmap-section">
            <h3>📊 Access Heatmap by Role and Table</h3>
            <div class="heatmap-container">
                <table class="heatmap-table">
                    <thead>
                        <tr>
                            <th>Role</th>
        """
        
        # Add table headers
        for table in pivot.columns:
            html += f'<th>{table}</th>'
        
        html += "</tr></thead><tbody>"
        
        # Add data rows
        for role in pivot.index:
            html += f"<tr><td class='role-cell'>{role}</td>"
            for table in pivot.columns:
                count = pivot.loc[role, table]
                # Color intensity based on access count
                intensity = min(255, 100 + count * 20)
                html += f'<td class="heatmap-cell" style="background-color: rgba(0,123,255,{count/max(pivot.max()):.2f})">{count}</td>'
            html += "</tr>"
        
        html += """
                </tbody>
            </table>
            </div>
        </div>
        """
        
        return html
    
    def generate_user_activity_timeline(self, access_logs: pd.DataFrame) -> str:
        """Generate timeline of user activity."""
        
        # Convert timestamp to datetime for analysis
        access_logs['datetime'] = pd.to_datetime(access_logs['timestamp'])
        access_logs['date'] = access_logs['datetime'].dt.date
        
        # Daily activity by user
        daily_activity = access_logs.groupby(['date', 'user_id']).size().reset_index(name='access_count')
        
        html = """
        <div class="timeline-section">
            <h3>⏰ User Activity Timeline (Last 30 Days)</h3>
            <div class="timeline-container">
        """
        
        # Group by date and show user activity
        for date in sorted(daily_activity['date'].unique()):
            date_activity = daily_activity[daily_activity['date'] == date]
            html += f'<div class="timeline-day"><h4>{date}</h4><ul>'
            
            for _, row in date_activity.iterrows():
                user = row['user_id']
                count = row['access_count']
                html += f'<li><strong>{user}</strong>: {count} accesses</li>'
            
            html += '</ul></div>'
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def generate_compliance_issues_report(self, lineage_data: Dict) -> str:
        """Generate report of compliance issues."""
        
        issues = lineage_data.get('compliance_issues', [])
        
        html = """
        <div class="compliance-section">
            <h3>🚨 Compliance Issues Detected</h3>
        """
        
        if not issues:
            html += '<p class="no-issues">✅ No compliance issues detected</p>'
        else:
            html += f'<p class="issues-count">Found {len(issues)} potential compliance issues:</p>'
            html += '<div class="issues-list">'
            
            for issue in issues:
                severity_class = f"severity-{issue['severity']}"
                html += f"""
                <div class="compliance-issue {severity_class}">
                    <h4>{issue['issue']}</h4>
                    <p><strong>User:</strong> {issue['user']} ({issue['role']})</p>
                    <p><strong>Table:</strong> {issue['table']}</p>
                    <p><strong>Time:</strong> {issue['timestamp']}</p>
                    <p><strong>Severity:</strong> {issue['severity'].title()}</p>
                </div>
                """
            
            html += '</div>'
        
        html += '</div>'
        return html
    
    def generate_data_flow_diagram(self, lineage_data: Dict) -> str:
        """Generate a simple data flow diagram."""
        
        tables = list(lineage_data.get('table_access_summary', {}).keys())
        
        html = """
        <div class="flow-section">
            <h3>🔗 Data Flow Diagram</h3>
            <div class="flow-diagram">
        """
        
        # Simple flow diagram showing table relationships
        for i, table in enumerate(tables):
            table_info = lineage_data.get('table_access_summary', {}).get(table, {})
            is_sensitive = table_info.get('is_sensitive', False)
            access_count = table_info.get('total_accesses', 0)
            
            sensitive_class = "sensitive-table" if is_sensitive else "standard-table"
            
            html += f"""
            <div class="flow-node {sensitive_class}">
                <h4>{table}</h4>
                <p>Accesses: {access_count}</p>
                <p class="table-type">{'🔒 Sensitive' if is_sensitive else '📊 Standard'}</p>
            </div>
            """
            
            # Add flow arrows (simple representation)
            if i < len(tables) - 1:
                html += '<div class="flow-arrow">→</div>'
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive lineage report."""
        
        data = self.load_data()
        if not data:
            return "<p>No data available for visualization</p>"
        
        access_logs = data.get('access_logs')
        lineage_data = data.get('lineage', {})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Lineage & Access Patterns Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; }}
                .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
                
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px; }}
                .section h3 {{ color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }}
                
                .heatmap-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .heatmap-table th, .heatmap-table td {{ border: 1px solid #dee2e6; padding: 8px; text-align: center; }}
                .heatmap-table th {{ background-color: #f8f9fa; font-weight: bold; }}
                .role-cell {{ font-weight: bold; background-color: #e9ecef; }}
                .heatmap-cell {{ font-weight: bold; }}
                
                .timeline-container {{ margin: 15px 0; }}
                .timeline-day {{ margin: 15px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
                .timeline-day h4 {{ margin: 0 0 10px 0; color: #495057; }}
                .timeline-day ul {{ margin: 0; padding-left: 20px; }}
                .timeline-day li {{ margin: 5px 0; }}
                
                .compliance-issue {{ margin: 15px 0; padding: 15px; border-radius: 5px; border-left: 5px solid; }}
                .severity-high {{ background-color: #f8d7da; border-left-color: #dc3545; }}
                .severity-medium {{ background-color: #fff3cd; border-left-color: #ffc107; }}
                .severity-low {{ background-color: #d1ecf1; border-left-color: #17a2b8; }}
                
                .flow-diagram {{ display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
                .flow-node {{ padding: 20px; border: 2px solid #dee2e6; border-radius: 8px; text-align: center; min-width: 150px; }}
                .sensitive-table {{ border-color: #dc3545; background-color: #f8d7da; }}
                .standard-table {{ border-color: #28a745; background-color: #d4edda; }}
                .flow-arrow {{ font-size: 24px; color: #6c757d; }}
                
                .no-issues {{ color: #28a745; font-weight: bold; }}
                .issues-count {{ color: #dc3545; font-weight: bold; }}
                
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .stat-card h3 {{ margin: 0 0 10px 0; color: #495057; }}
                .stat-card .number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔗 Data Lineage & Access Patterns Report</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
        """
        
        # Add summary statistics
        if access_logs is not None:
            total_accesses = len(access_logs)
            unique_users = access_logs['user_id'].nunique()
            unique_tables = access_logs['table_name'].nunique()
            date_range = f"{access_logs['timestamp'].min()[:10]} to {access_logs['timestamp'].max()[:10]}"
            
            html += f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Accesses</h3>
                    <div class="number">{total_accesses:,}</div>
                </div>
                <div class="stat-card">
                    <h3>Unique Users</h3>
                    <div class="number">{unique_users}</div>
                </div>
                <div class="stat-card">
                    <h3>Tables Accessed</h3>
                    <div class="number">{unique_tables}</div>
                </div>
                <div class="stat-card">
                    <h3>Date Range</h3>
                    <div class="number">{date_range}</div>
                </div>
            </div>
            """
        
        # Add heatmap
        if access_logs is not None:
            html += self.generate_access_heatmap(access_logs)
        
        # Add timeline
        if access_logs is not None:
            html += self.generate_user_activity_timeline(access_logs)
        
        # Add compliance issues
        if lineage_data:
            html += self.generate_compliance_issues_report(lineage_data)
        
        # Add data flow diagram
        if lineage_data:
            html += self.generate_data_flow_diagram(lineage_data)
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


def main() -> None:
    """Generate comprehensive lineage visualization report."""
    
    visualizer = LineageVisualizer()
    
    print("🔗 Generating data lineage visualization...")
    html_report = visualizer.generate_comprehensive_report()
    
    # Save HTML report
    report_path = Path("outputs/lineage_visualization.html")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"💾 Lineage visualization saved to: {report_path}")
    print("📊 Open the HTML file in a browser to view the interactive report")


if __name__ == "__main__":
    main()
