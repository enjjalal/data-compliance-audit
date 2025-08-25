#!/bin/bash

# Run the application locally
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p outputs data

# Run the application
streamlit run audit_dashboard/app.py
