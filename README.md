# Data Compliance Audit System

A comprehensive solution for identifying, monitoring, and managing PII (Personally Identifiable Information) and ensuring data compliance across your organization.

## Features

- 🕵️‍♂️ Automated PII detection using regex patterns
- 📊 Interactive dashboard for monitoring compliance
- 🚨 Alerting system for policy violations
- 🔍 Data lineage and access tracking
- 📈 Comprehensive reporting and exports
- 🐳 Docker support for easy deployment

## Quick Start

### Local Development
1. Clone the repository:
   git clone https://github.com/yourusername/data-compliance-audit.git
   cd data-compliance-audit

2. Install dependencies:
   pip install -r requirements.txt

3. Run the application:
   ./run.sh  # or run.bat on Windows

### Docker
1. Build and start the application:
   docker-compose up --build

2. Access the dashboard at http://localhost:8501

## Project Structure
data_compliance_audit/
├── audit_dashboard/     # Streamlit dashboard
├── conf/                # Configuration files
├── data/                # Sample data
├── dbt_project/         # dbt models
└── docs/                # Documentation

## License
MIT License - See LICENSE for details.
