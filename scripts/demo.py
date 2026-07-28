import os
import sys
import json
import time

# Ensure backend in PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.agents.orchestrator import run_multi_agent_pipeline

def run_demo():
    print("==========================================================================")
    print("  THEMIS: Automated Policy Compliance & Risk Auditing Engine - DEMO")
    print("==========================================================================")
    
    sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "data", "sample_transactions.json")
    if not os.path.exists(sample_path):
        print(f"Error: Could not find sample transactions at {sample_path}")
        return

    with open(sample_path, "r", encoding="utf-8") as f:
        transactions = json.load(f)

    print(f"Loaded {len(transactions)} sample financial transactions for evaluation.\n")

    summary = {"APPROVED": 0, "REVIEW": 0, "ESCALATE": 0}

    for idx, tx in enumerate(transactions, 1):
        tx_id = tx.get("transaction_id")
        cust = tx.get("customer_name")
        amt = tx.get("amount")
        country = tx.get("destination_country")

        print(f"[{idx:02d}/{len(transactions)}] Processing {tx_id} | {cust} | ${amt:,.2f} -> {country}...")
        
        start_t = time.time()
        res = run_multi_agent_pipeline(tx)
        elapsed = (time.time() - start_t) * 1000

        decision = res.get("decision", {})
        status = decision.get("status", "UNKNOWN")
        summary[status] = summary.get(status, 0) + 1
        violations = res.get("violations", [])

        status_tag = f"\033[92m[{status}]\033[0m" if status == "APPROVED" else f"\033[93m[{status}]\033[0m" if status == "REVIEW" else f"\033[91m[{status}]\033[0m"
        print(f"     => Status: {status_tag} (Confidence: {decision.get('confidence', 1.0):.2f}) | {len(violations)} Violation(s) | {elapsed:.1f}ms")

        if violations:
            for v in violations:
                print(f"        * [{v.get('severity')}] {v.get('rule_id')}: {v.get('reason')}")
        print()

    print("==========================================================================")
    print("  DEMO AUDIT EXECUTION SUMMARY")
    print("==========================================================================")
    print(f" Total Evaluated : {len(transactions)}")
    print(f" Auto-Approved   : {summary['APPROVED']}")
    print(f" Compliance Review: {summary['REVIEW']}")
    print(f" High Risk Escalate: {summary['ESCALATE']}")
    print("==========================================================================")

if __name__ == "__main__":
    run_demo()
