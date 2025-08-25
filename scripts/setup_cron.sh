#!/bin/bash
# Setup script for cron scheduling of the audit pipeline

echo "Setting up cron job for GDPR/PII compliance audit..."

# Get the absolute path to the cron wrapper script
SCRIPT_PATH=$(realpath "$(dirname "$0")/run_audit_cron.py")

# Create a temporary crontab entry
TEMP_CRON=$(mktemp)
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "" > "$TEMP_CRON"

# Add the cron job (runs daily at 2 AM)
echo "# GDPR/PII Compliance Audit - runs daily at 2 AM" >> "$TEMP_CRON"
echo "0 2 * * * /usr/bin/python3 $SCRIPT_PATH >> /tmp/audit_cron.log 2>&1" >> "$TEMP_CRON"

# Install the new crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "Cron job installed successfully!"
echo "The audit pipeline will run daily at 2 AM"
echo "To view cron logs: tail -f /tmp/audit_cron.log"
echo ""
echo "To edit cron manually: crontab -e"
echo "To list current cron jobs: crontab -l"
