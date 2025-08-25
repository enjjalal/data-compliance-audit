# Compliance Reporting

This module provides comprehensive reporting capabilities for the Data Compliance Audit system, generating detailed reports in multiple formats.

## Features

- **Multiple Formats**: Generate reports in HTML, CSV, and JSON formats
- **Interactive Visualizations**: Interactive charts and graphs in HTML reports
- **Scheduled Reports**: Easily integrate with cron or other schedulers
- **Custom Templates**: Customize report appearance using Jinja2 templates

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

```bash
# Generate all report formats (default)
python scripts/generate_reports.py

# Generate only HTML reports
python scripts/generate_reports.py --format html

# Generate only CSV reports
python scripts/generate_reports.py --format csv

# Specify custom output directory
python scripts/generate_reports.py --output-dir /path/to/reports
```

### Programmatic Usage

```python
from reporting_engine import ReportingEngine

# Initialize the reporting engine
engine = ReportingEngine()

# Generate all report formats
reports = engine.generate_report('all')

# Access generated report paths
print(f"HTML Report: {reports['html']}")
print(f"CSV Reports directory: {reports['csv']}")
```

## Report Types

### HTML Reports
Interactive HTML reports include:
- Summary metrics
- Visualizations (violations by type, PII distribution, trends)
- Detailed violation listings
- PII findings

### CSV Reports
- `violations_report_*.csv`: Detailed list of all active violations
- `pii_findings_*.csv`: Comprehensive PII scan results

## Customization

### Templates
HTML reports are generated using Jinja2 templates. To customize:

1. Create a `templates` directory in your project root
2. Add your custom template as `compliance_report.html`
3. The template will be automatically used for report generation

### Visualizations
To modify the visualizations, edit the `_create_visualizations` method in `reporting_engine.py`.

## Scheduling Reports

To schedule regular report generation, add a cron job:

```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/project && /usr/bin/python3 scripts/generate_reports.py
```

## Output Directory

Reports are saved to `outputs/reports/` by default, with timestamps in the filenames.

Example:
```
outputs/reports/
  ├── compliance_report_20230825_150045.html
  ├── pii_findings_20230825_150045.csv
  └── violations_report_20230825_150045.csv
```
