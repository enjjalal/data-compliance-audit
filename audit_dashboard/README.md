# Data Compliance Audit Dashboard

A Streamlit-based dashboard for monitoring and analyzing data compliance across your organization.

## Features

- Real-time visualization of PII findings and violations
- Interactive charts and metrics
- Violation trend analysis
- Detailed data exploration

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

1. Clone the repository
2. Navigate to the dashboard directory:
   ```bash
   cd audit_dashboard
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Dashboard

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. The dashboard will open automatically in your default web browser at `http://localhost:8501`

## Usage

- The dashboard loads data from the `outputs` directory
- Use the sidebar to navigate between different views
- Interact with the charts by hovering, zooming, and clicking on data points
- View detailed data in the "Detailed Data" section at the bottom of the page

## Data Sources

The dashboard reads from the following files in the `outputs` directory:
- `violations.csv` - Current active violations
- `pii_scan.csv` - PII scan results
- `enhanced_violations.csv` - Enhanced violation details
- `violations_history.json` - Historical violation data for trend analysis

## License

This project is part of the Data Compliance Audit system.
