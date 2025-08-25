#!/usr/bin/env python3
"""
Cron-compatible wrapper for the audit pipeline.
This script can be added to crontab for automated execution.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change to project directory
os.chdir(project_root)

# Import and run the audit pipeline
from src.run_audit import main

if __name__ == "__main__":
    main()
