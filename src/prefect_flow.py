"""
Optional Prefect flow for advanced orchestration of the audit pipeline.
Install with: pip install prefect
"""

from pathlib import Path
from typing import Dict, Any

try:
    from prefect import flow, task, get_run_logger
    from prefect.filesystems import LocalFileSystem
    from prefect.deployments import Deployment
    PREFECT_AVAILABLE = True
except ImportError:
    PREFECT_AVAILABLE = False
    print("Prefect not available. Install with: pip install prefect")


@task
def run_pii_scan_task() -> Dict[str, Any]:
    """Task to run PII scanning."""
    if not PREFECT_AVAILABLE:
        raise ImportError("Prefect not available")
    
    logger = get_run_logger()
    logger.info("Starting PII scan task...")
    
    # Import and run the PII scan
    from scan_pii import main as run_pii_scan
    run_pii_scan()
    
    logger.info("PII scan task completed")
    return {"status": "success", "task": "pii_scan"}


@task
def run_policy_evaluation_task() -> Dict[str, Any]:
    """Task to run policy evaluation."""
    if not PREFECT_AVAILABLE:
        raise ImportError("Prefect not available")
    
    logger = get_run_logger()
    logger.info("Starting policy evaluation task...")
    
    # Import and run the policy engine
    from policy_engine import main as run_policies
    run_policies()
    
    logger.info("Policy evaluation task completed")
    return {"status": "success", "task": "policy_evaluation"}


@task
def generate_report_task() -> Dict[str, Any]:
    """Task to generate final audit report."""
    if not PREFECT_AVAILABLE:
        raise ImportError("Prefect not available")
    
    logger = get_run_logger()
    logger.info("Generating audit report...")
    
    # Generate summary report
    from run_audit import generate_summary_report
    generate_summary_report()
    
    logger.info("Report generation completed")
    return {"status": "success", "task": "report_generation"}


@flow(name="gdpr-compliance-audit")
def compliance_audit_flow() -> Dict[str, Any]:
    """Main Prefect flow for the compliance audit pipeline."""
    if not PREFECT_AVAILABLE:
        raise ImportError("Prefect not available")
    
    logger = get_run_logger()
    logger.info("Starting GDPR compliance audit flow...")
    
    # Execute tasks in sequence
    pii_result = run_pii_scan_task()
    policy_result = run_policy_evaluation_task()
    report_result = generate_report_task()
    
    # Aggregate results
    flow_result = {
        "flow": "gdpr-compliance-audit",
        "tasks": [pii_result, policy_result, report_result],
        "status": "completed"
    }
    
    logger.info("Compliance audit flow completed successfully")
    return flow_result


def create_deployment() -> None:
    """Create a Prefect deployment for the flow."""
    if not PREFECT_AVAILABLE:
        print("Prefect not available. Install with: pip install prefect")
        return
    
    # Create a local file system storage
    storage = LocalFileSystem(basepath=str(Path.cwd()))
    
    # Create deployment
    deployment = Deployment.build_from_flow(
        flow=compliance_audit_flow,
        name="gdpr-audit-daily",
        storage=storage,
        work_queue_name="default",
        cron="0 2 * * *"  # Daily at 2 AM
    )
    
    deployment.apply()
    print("Prefect deployment created successfully!")


if __name__ == "__main__":
    if PREFECT_AVAILABLE:
        # Run the flow directly
        result = compliance_audit_flow()
        print(f"Flow result: {result}")
    else:
        print("Prefect not available. Running basic pipeline...")
        from run_audit import main
        main()
