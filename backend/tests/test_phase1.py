import pytest
from app.agents.intake_agent import intake_agent
from app.agents.policy_retrieval_agent import policy_retrieval_agent
from app.agents.risk_analysis_agent import risk_analysis_agent, evaluate_deterministic_rules
from app.agents.decision_agent import decision_agent
from app.agents.audit_agent import audit_agent
from app.agents.orchestrator import run_multi_agent_pipeline

def test_intake_agent_sanctioned_country():
    raw_tx = {
        "transaction_id": "TX-TEST-01",
        "customer_id": "CUST-99",
        "customer_name": "Test Co",
        "amount": 50000.0,
        "destination_country": "Iran",
        "transaction_type": "wire_transfer"
    }
    state = intake_agent({"raw_transaction": raw_tx})
    assert state["transaction_id"] == "TX-TEST-01"
    features = state["extracted_features"]
    assert features["is_sanctioned_country"] is True
    assert features["amount"] == 50000.0

def test_policy_retrieval_agent():
    state = {
        "extracted_features": {
            "amount": 150000.0,
            "is_high_value": True,
            "transaction_type": "wire_transfer"
        },
        "agent_logs": []
    }
    retrieved_state = policy_retrieval_agent(state)
    policies = retrieved_state["relevant_policies"]
    assert len(policies) > 0
    categories = [p["category"] for p in policies]
    assert "Limits" in categories or "AML" in categories

def test_risk_analysis_sanctions_violation():
    features = {
        "transaction_id": "TX-TEST-02",
        "amount": 20000.0,
        "destination_country": "Iran",
        "kyc_level": 1
    }
    violations = evaluate_deterministic_rules(features, [])
    assert len(violations) >= 1
    violation_ids = [v["rule_id"] for v in violations]
    assert "SNC-R1" in violation_ids

def test_decision_agent_escalation():
    state = {
        "extracted_features": {"amount": 50000.0},
        "violations": [
            {
                "rule_id": "SNC-R1",
                "rule_name": "OFAC Comprehensive Sanctions Block",
                "category": "Sanctions",
                "severity": "CRITICAL",
                "reason": "Destination country is Iran"
            }
        ],
        "agent_logs": []
    }
    dec_state = decision_agent(state)
    decision = dec_state["decision"]
    assert decision["status"] == "ESCALATE"
    assert "CRITICAL" in decision["escalation_reason"]

def test_full_orchestrator_compliant_tx():
    raw_tx = {
        "transaction_id": "TX-COMPLIANT-01",
        "customer_id": "CUST-101",
        "customer_name": "Compliant Corp",
        "amount": 1500.0,
        "destination_country": "United States",
        "transaction_type": "merchant_payment",
        "kyc_level": 1,
        "account_age_days": 365,
        "pep_flag": False
    }
    res = run_multi_agent_pipeline(raw_tx)
    assert res["transaction_id"] == "TX-COMPLIANT-01"
    assert res["decision"]["status"] == "APPROVED"
    assert res["audit_record_id"].startswith("AUD-")
    assert len(res["agent_logs"]) == 5
