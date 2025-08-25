#!/usr/bin/env python3
"""
Command-line interface for generating compliance reports.
"""

import argparse
from pathlib import Path
import sys

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from reporting_engine import ReportingEngine

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate compliance reports.')
    parser.add_argument(
        '--format', 
        choices=['all', 'csv', 'html'], 
        default='all',
        help='Report format to generate (default: all)'
    )
    parser.add_argument(
        '--output-dir', 
        type=Path,
        default=Path('outputs/reports'),
        help='Output directory for reports (default: outputs/reports)'
    )
    return parser.parse_args()

def main():
    """Main entry point for report generation."""
    args = parse_args()
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        engine = ReportingEngine()
        reports = engine.generate_report(args.format)
        
        print("\n✅ Successfully generated reports:")
        for format, path in reports.items():
            print(f"- {format.upper()}: {path}")
            
    except Exception as e:
        print(f"\n❌ Error generating reports: {e}", file=sys.stderr)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
