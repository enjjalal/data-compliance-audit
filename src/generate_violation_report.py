"""
Generate comprehensive violation reports in multiple formats.
Includes HTML, CSV, and JSON outputs with detailed analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd


def load_violations_data() -> Dict:
    """Load all violations data from various sources."""
    data = {}
    
    # Load current violations
    violations_path = Path("outputs/violations.csv")
    if violations_path.exists():
        data['current'] = pd.read_csv(violations_path).to_dict('records')
    
    # Load violation history
    history_path = Path("outputs/violations_history.json")
    if history_path.exists():
        with open(history_path, 'r', encoding='utf-8') as f:
            data['history'] = json.load(f)
    
    # Load enhanced violations
    enhanced_path = Path("outputs/enhanced_violations.csv")
    if enhanced_path.exists():
        data['enhanced'] = pd.read_csv(enhanced_path).to_dict('records')
    
    return data


def generate_html_report(violations_data: Dict) -> str:
    """Generate an HTML report of violations."""
    
    current_violations = violations_data.get('current', [])
    history = violations_data.get('history', [])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GDPR/PII Compliance Violation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .violation {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
            .critical {{ border-left: 5px solid #dc3545; }}
            .high {{ border-left: 5px solid #fd7e14; }}
            .medium {{ border-left: 5px solid #ffc107; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .timestamp {{ color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚨 GDPR/PII Compliance Violation Report</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Current Violations</h3>
                <h2>{len(current_violations)}</h2>
            </div>
            <div class="stat-card">
                <h3>Total History</h3>
                <h2>{len(history)}</h2>
            </div>
            <div class="stat-card">
                <h3>Open Issues</h3>
                <h2>{len([v for v in history if v.get('status') == 'open'])}</h2>
            </div>
            <div class="stat-card">
                <h3>Resolved</h3>
                <h2>{len([v for v in history if v.get('status') == 'resolved'])}</h2>
            </div>
        </div>
        
        <h2>Current Violations</h2>
    """
    
    if current_violations:
        for violation in current_violations:
            severity_class = 'medium'
            if violation.get('policy_id') in ['no_pii_in_logs', 'no_pii_in_exports']:
                severity_class = 'critical'
            elif violation.get('policy_id') == 'pii_must_be_tagged':
                severity_class = 'high'
            
            html += f"""
            <div class="violation {severity_class}">
                <h3>Policy: {violation.get('policy_id', 'Unknown')}</h3>
                <p><strong>Table:</strong> {violation.get('table', 'Unknown')}</p>
                <p><strong>Column:</strong> {violation.get('column', 'Unknown')}</p>
                <p><strong>PII Tags:</strong> {violation.get('pii_tags', 'None')}</p>
                <p><strong>Reason:</strong> {violation.get('reason', 'Unknown')}</p>
            </div>
            """
    else:
        html += "<p>✅ No current violations detected.</p>"
    
    html += """
        <h2>Violation History</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #f8f9fa;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Policy</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Table</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Column</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Status</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Detected</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for violation in history:
        html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{violation.get('policy_id', 'Unknown')}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{violation.get('table', 'Unknown')}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{violation.get('column', 'Unknown')}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{violation.get('status', 'Unknown')}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{violation.get('detected_at', 'Unknown')}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html


def main() -> None:
    """Generate comprehensive violation reports."""
    
    # Load violations data
    violations_data = load_violations_data()
    
    # Generate HTML report
    html_report = generate_html_report(violations_data)
    
    # Save HTML report
    html_path = Path("outputs/violations_report.html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"📊 Comprehensive violation report generated:")
    print(f"   HTML: {html_path}")
    
    # Generate summary statistics
    current_count = len(violations_data.get('current', []))
    history_count = len(violations_data.get('history', []))
    open_count = len([v for v in violations_data.get('history', []) if v.get('status') == 'open'])
    
    print(f"\n📈 Summary:")
    print(f"   Current violations: {current_count}")
    print(f"   Total in history: {history_count}")
    print(f"   Open issues: {open_count}")
    
    if current_count > 0:
        print(f"\n🚨 Active violations require attention!")
    else:
        print(f"\n✅ No active violations detected.")


if __name__ == "__main__":
    main()
