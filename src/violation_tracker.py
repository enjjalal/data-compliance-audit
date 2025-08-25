"""
Violation tracker for GDPR/PII compliance violations.
Handles persistence, alerting, and violation history.
"""

import json
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class ViolationTracker:
    """Tracks and manages compliance violations."""
    
    def __init__(self, violations_db: str = "outputs/violations_history.json"):
        self.violations_db = Path(violations_db)
        self.violations_db.parent.mkdir(parents=True, exist_ok=True)
        self.load_violations()
    
    def load_violations(self) -> None:
        """Load existing violations from JSON database."""
        if self.violations_db.exists():
            with open(self.violations_db, 'r', encoding='utf-8') as f:
                self.violations = json.load(f)
        else:
            self.violations = []
    
    def add_violation(self, violation: Dict) -> None:
        """Add a new violation with timestamp."""
        violation_with_meta = {
            **violation,
            'detected_at': datetime.now().isoformat(),
            'status': 'open',
            'alerted': False
        }
        self.violations.append(violation_with_meta)
        self.save_violations()
    
    def save_violations(self) -> None:
        """Save violations to JSON database."""
        with open(self.violations_db, 'w', encoding='utf-8') as f:
            json.dump(self.violations, f, indent=2, ensure_ascii=False)
    
    def get_open_violations(self) -> List[Dict]:
        """Get all open violations."""
        return [v for v in self.violations if v.get('status') == 'open']
    
    def get_violations_by_policy(self, policy_id: str) -> List[Dict]:
        """Get violations for a specific policy."""
        return [v for v in self.violations if v.get('policy_id') == policy_id]
    
    def mark_resolved(self, violation_index: int) -> None:
        """Mark a violation as resolved."""
        if 0 <= violation_index < len(self.violations):
            self.violations[violation_index]['status'] = 'resolved'
            self.violations[violation_index]['resolved_at'] = datetime.now().isoformat()
            self.save_violations()
    
    def get_violation_stats(self) -> Dict:
        """Get violation statistics."""
        total = len(self.violations)
        open_count = len(self.get_open_violations())
        resolved_count = total - open_count
        
        policy_counts = {}
        for v in self.violations:
            policy_id = v.get('policy_id', 'unknown')
            policy_counts[policy_id] = policy_counts.get(policy_id, 0) + 1
        
        return {
            'total_violations': total,
            'open_violations': open_count,
            'resolved_violations': resolved_count,
            'by_policy': policy_counts
        }


class AlertManager:
    """Manages alerting for violations."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alert_history_file = Path("logs/alert_history.json")
        self.alert_history_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_alert_history()
    
    def load_alert_history(self) -> None:
        """Load alert history."""
        if self.alert_history_file.exists():
            with open(self.alert_history_file, 'r', encoding='utf-8') as f:
                self.alert_history = json.load(f)
        else:
            self.alert_history = []
    
    def save_alert_history(self) -> None:
        """Save alert history."""
        with open(self.alert_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.alert_history, f, indent=2, ensure_ascii=False)
    
    def send_email_alert(self, violations: List[Dict]) -> bool:
        """Send email alert for violations (mock implementation)."""
        try:
            # Mock email sending - in production, this would use real SMTP
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'violations_count': len(violations),
                'violations': violations[:5],  # Limit to first 5 for email
                'alert_type': 'email'
            }
            
            self.alert_history.append(alert_data)
            self.save_alert_history()
            
            # Log the alert
            print(f"📧 EMAIL ALERT SENT: {len(violations)} violations detected")
            print(f"   Recipients: {self.config.get('alert_email', 'data.governance@company.com')}")
            print(f"   Alert saved to: {self.alert_history_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email alert: {e}")
            return False
    
    def send_console_alert(self, violations: List[Dict]) -> None:
        """Send console alert for violations."""
        if not violations:
            return
        
        print("\n" + "="*60)
        print("🚨 COMPLIANCE VIOLATIONS DETECTED")
        print("="*60)
        
        for i, v in enumerate(violations, 1):
            print(f"{i}. Policy: {v.get('policy_id', 'unknown')}")
            print(f"   Table: {v.get('table', 'unknown')}")
            print(f"   Column: {v.get('column', 'unknown')}")
            print(f"   Reason: {v.get('reason', 'unknown')}")
            print(f"   PII Tags: {v.get('pii_tags', 'none')}")
            print()
        
        print(f"Total violations: {len(violations)}")
        print("="*60 + "\n")
    
    def should_alert(self, violations: List[Dict]) -> bool:
        """Determine if alerts should be sent."""
        if not violations:
            return False
        
        # Alert if there are new violations or if it's been more than 24 hours
        last_alert = self.alert_history[-1] if self.alert_history else None
        if not last_alert:
            return True
        
        last_alert_time = datetime.fromisoformat(last_alert['timestamp'])
        hours_since_last = (datetime.now() - last_alert_time).total_seconds() / 3600
        
        return hours_since_last >= 24


def main() -> None:
    """Main function to demonstrate violation tracking and alerting."""
    # Load configuration
    config = {
        'alert_email': 'data.governance@company.com',
        'smtp_server': 'localhost',
        'alert_threshold': 1  # Alert if 1 or more violations
    }
    
    # Initialize components
    tracker = ViolationTracker()
    alert_manager = AlertManager(config)
    
    # Load current violations
    current_violations_path = Path("outputs/violations.csv")
    if current_violations_path.exists():
        current_violations = pd.read_csv(current_violations_path)
        
        # Add new violations to tracker
        for _, row in current_violations.iterrows():
            violation = {
                'policy_id': row['policy_id'],
                'table': row['table'],
                'column': row['column'],
                'pii_tags': row['pii_tags'],
                'reason': row['reason']
            }
            tracker.add_violation(violation)
    
    # Get open violations
    open_violations = tracker.get_open_violations()
    
    # Send alerts if needed
    if alert_manager.should_alert(open_violations):
        alert_manager.send_console_alert(open_violations)
        
        if len(open_violations) >= config['alert_threshold']:
            alert_manager.send_email_alert(open_violations)
    
    # Generate violation report
    stats = tracker.get_violation_stats()
    print(f"📊 Violation Statistics:")
    print(f"   Total: {stats['total_violations']}")
    print(f"   Open: {stats['open_violations']}")
    print(f"   Resolved: {stats['resolved_violations']}")
    
    # Save enhanced violations report
    enhanced_report = pd.DataFrame(open_violations)
    if not enhanced_report.empty:
        enhanced_report.to_csv("outputs/enhanced_violations.csv", index=False)
        print(f"💾 Enhanced violations report saved to: outputs/enhanced_violations.csv")
    
    print(f"📁 Violation database: {tracker.violations_db}")
    print(f"📁 Alert history: {alert_manager.alert_history_file}")


if __name__ == "__main__":
    main()
