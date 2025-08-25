#!/usr/bin/env python3
"""
Main scanning pipeline for GDPR/PII compliance audit.
Orchestrates PII detection, policy evaluation, and reporting.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from policy_engine import main as run_policies
from scan_pii import main as run_pii_scan


def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the audit pipeline."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"audit_{timestamp}.log"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info(f"Audit pipeline started, logging to {log_file}")


def run_pipeline(config: Dict[str, Any]) -> bool:
    """Execute the complete audit pipeline."""
    try:
        logging.info("Starting PII scan...")
        run_pii_scan()
        logging.info("PII scan completed")
        
        logging.info("Starting policy evaluation...")
        run_policies()
        logging.info("Policy evaluation completed")
        
        # Generate summary report
        generate_summary_report()
        logging.info("Audit pipeline completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        return False


def generate_summary_report() -> None:
    """Generate a summary report of the audit results."""
    try:
        from pathlib import Path
        import pandas as pd
        
        pii_scan_path = Path("outputs/pii_scan.csv")
        violations_path = Path("outputs/violations.csv")
        
        if pii_scan_path.exists():
            pii_df = pd.read_csv(pii_scan_path)
            pii_count = len(pii_df)
            logging.info(f"PII scan found {pii_count} columns with PII")
        
        if violations_path.exists():
            violations_df = pd.read_csv(violations_path)
            violation_count = len(violations_df)
            logging.info(f"Policy evaluation found {violation_count} violations")
            
            if violation_count > 0:
                logging.warning(f"Found {violation_count} policy violations!")
            else:
                logging.info("No policy violations detected")
                
    except Exception as e:
        logging.error(f"Failed to generate summary report: {e}")


def main() -> None:
    """Main entry point for the audit pipeline."""
    config = {
        "log_level": "INFO",
        "data_dir": "data",
        "output_dir": "outputs"
    }
    
    setup_logging(config["log_level"])
    
    success = run_pipeline(config)
    
    if success:
        logging.info("Audit pipeline completed successfully")
        sys.exit(0)
    else:
        logging.error("Audit pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
