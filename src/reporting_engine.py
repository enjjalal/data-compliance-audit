"""
Reporting engine for generating compliance reports and exports.
Supports multiple formats including CSV, JSON, and interactive HTML.
"""

import json
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader
import webbrowser

# Configure paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

class ReportingEngine:
    """Handles generation of compliance reports in various formats."""
    
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_data(self) -> Dict[str, Any]:
        """Load all necessary data for reporting."""
        data = {}
        
        # Load violations data
        violations_path = OUTPUT_DIR / "violations.csv"
        if violations_path.exists():
            data['violations'] = pd.read_csv(violations_path)
        
        # Load PII scan results
        pii_scan_path = OUTPUT_DIR / "pii_scan.csv"
        if pii_scan_path.exists():
            data['pii_scan'] = pd.read_csv(pii_scan_path)
        
        # Load violation history
        history_path = OUTPUT_DIR / "violations_history.json"
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                data['history'] = json.load(f)
        
        return data
    
    def generate_csv_report(self, data: Dict[str, Any]) -> Path:
        """Generate CSV reports for violations and PII findings."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate violations report
        if 'violations' in data and not data['violations'].empty:
            violations_path = REPORTS_DIR / f"violations_report_{timestamp}.csv"
            data['violations'].to_csv(violations_path, index=False)
        
        # Generate PII findings report
        if 'pii_scan' in data and not data['pii_scan'].empty:
            pii_path = REPORTS_DIR / f"pii_findings_{timestamp}.csv"
            data['pii_scan'].to_csv(pii_path, index=False)
            
        return REPORTS_DIR
    
    def generate_html_profile(self, data: Dict[str, Any]) -> Path:
        """Generate an interactive HTML profile with visualizations."""
        # Create visualizations
        figures = self._create_visualizations(data)
        
        # Prepare context for template
        context = {
            'report_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'violations_count': len(data.get('violations', [])),
            'pii_findings_count': len(data.get('pii_scan', [])),
            'figures': figures,
            'violations': data.get('violations', pd.DataFrame()).to_dict('records'),
            'pii_findings': data.get('pii_scan', pd.DataFrame()).to_dict('records'),
        }
        
        # Render template
        template = self.env.get_template('compliance_report.html')
        html_content = template.render(**context)
        
        # Save to file
        report_path = REPORTS_DIR / f"compliance_report_{self.timestamp}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return report_path
    
    def _create_visualizations(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create Plotly visualizations for the HTML report."""
        figures = {}
        
        # Violations by type
        if 'violations' in data and not data['violations'].empty:
            fig = px.bar(
                data['violations']['violation_type'].value_counts().reset_index(),
                x='index',
                y='violation_type',
                labels={'index': 'Violation Type', 'violation_type': 'Count'},
                title='Violations by Type'
            )
            figures['violations_by_type'] = fig.to_html(full_html=False)
        
        # PII type distribution
        if 'pii_scan' in data and not data['pii_scan'].empty:
            pii_dist = data['pii_scan']['pii_type'].value_counts().reset_index()
            fig = px.pie(
                pii_dist,
                values='pii_type',
                names='index',
                title='PII Type Distribution'
            )
            figures['pii_distribution'] = fig.to_html(full_html=False)
        
        # Violation trend
        if 'history' in data and data['history']:
            dates = list(data['history'].keys())
            counts = list(data['history'].values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, 
                y=counts,
                mode='lines+markers',
                name='Violations',
                line=dict(color='#1f77b4')
            ))
            
            fig.update_layout(
                title='Violation Trend Over Time',
                xaxis_title='Date',
                yaxis_title='Number of Violations',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            figures['violation_trend'] = fig.to_html(full_html=False)
        
        return figures
    
    def generate_report(self, format: str = 'all') -> Dict[str, Path]:
        """Generate reports in the specified format(s)."""
        data = self.load_data()
        reports = {}
        
        if format in ['csv', 'all']:
            reports['csv'] = self.generate_csv_report(data)
            
        if format in ['html', 'all']:
            reports['html'] = self.generate_html_profile(data)
            
        return reports


def main():
    """Generate all reports."""
    # Create HTML template if it doesn't exist
    template_path = TEMPLATES_DIR / "compliance_report.html"
    if not template_path.exists():
        _create_default_template(template_path)
    
    # Generate reports
    engine = ReportingEngine()
    reports = engine.generate_report('all')
    
    print("Generated reports:")
    for format, path in reports.items():
        print(f"- {format.upper()}: {path}")
    
    # Open HTML report in browser if generated
    if 'html' in reports:
        webbrowser.open(f"file://{reports['html'].resolve()}")


def _create_default_template(template_path: Path):
    """Create a default HTML template if none exists."""
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance Report - {{ report_date }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .header { background-color: #f8f9fa; padding: 2rem 0; margin-bottom: 2rem; }
        .section { margin-bottom: 3rem; }
        .card { margin-bottom: 1.5rem; box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075); }
        .card-header { font-weight: 600; background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>Data Compliance Report</h1>
            <p class="lead">Generated on {{ report_date }}</p>
        </div>
    </div>

    <div class="container">
        <!-- Summary Section -->
        <div class="section">
            <h2>Summary</h2>
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3 class="text-primary">{{ violations_count }}</h3>
                            <p class="text-muted">Active Violations</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h3 class="text-info">{{ pii_findings_count }}</h3>
                            <p class="text-muted">PII Findings</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Visualizations -->
        {% if figures %}
        <div class="section">
            <h2>Visualizations</h2>
            {% if 'violations_by_type' in figures %}
            <div class="card">
                <div class="card-header">Violations by Type</div>
                <div class="card-body">
                    {{ figures.violations_by_type | safe }}
                </div>
            </div>
            {% endif %}
            
            {% if 'pii_distribution' in figures %}
            <div class="card">
                <div class="card-header">PII Type Distribution</div>
                <div class="card-body">
                    {{ figures.pii_distribution | safe }}
                </div>
            </div>
            {% endif %}
            
            {% if 'violation_trend' in figures %}
            <div class="card">
                <div class="card-header">Violation Trend</div>
                <div class="card-body">
                    {{ figures.violation_trend | safe }}
                </div>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- Violations Table -->
        {% if violations %}
        <div class="section">
            <h2>Active Violations</h2>
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
                            {% for key in violations[0].keys() %}
                            <th>{{ key }}</th>
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in violations %}
                        <tr>
                            {% for value in item.values() %}
                            <td>{{ value }}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}
    </div>

    <footer class="bg-light py-4 mt-5">
        <div class="container text-center text-muted">
            <p>Generated by Data Compliance Audit System</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)


if __name__ == "__main__":
    main()
