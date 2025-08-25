@echo off

:: Update pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Create necessary directories
if not exist "outputs" mkdir outputs
if not exist "data" mkdir data

:: Run the application
streamlit run audit_dashboard/app.py

pause
