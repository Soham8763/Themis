import os
import sys
import json
import pytest
import asyncio
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "services", "backend"))

from app.main import app
from app.config import settings
from app.database import init_db
from app.agents.orchestrator import run_multi_agent_pipeline
from app.agents.risk_analysis_agent import evaluate_deterministic_rules, call_gemini_ai_reasoning
from app.rag.vector_store import VectorPolicyStore

# Initialize test database
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(init_db())

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# ============================================================================
# 1. API GATEWAY ENDPOINTS RIGOROUS TESTS
# ============================================================================

def test_gateway_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["environment"] == settings.ENV

def test_api_process_valid_compliant_transaction(client):
    payload = {
        "transaction_id": "TX-IND-1001",
        "customer_id": "CUST-9901",
        "customer_name": "Acme Industrial Corp",
        "amount": 1250.00,
        "currency": "USD",
        "transaction_type": "merchant_payment",
        "destination_country": "United States",
        "destination_account": "ACC-44120",
        "account_age_days": 400,
        "kyc_level": 1,
        "pep_flag": False,
        "is_cross_border": False,
        "dual_approval": False,
        "sow_verified": True
    }
    response = client.post("/api/v1/transactions/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "TX-IND-1001"
    assert data["status"] == "APPROVED"
    assert data["confidence"] == 1.0
    assert len(data["violations"]) == 0
    assert data["audit_trail_id"].startswith("AUD-")
    assert len(data["agent_decisions"]) == 5

def test_api_process_sanctioned_country_escalation(client):
    payload = {
        "transaction_id": "TX-IND-1002",
        "customer_id": "CUST-9902",
        "customer_name": "Tehran General Supplies",
        "amount": 45000.00,
        "currency": "USD",
        "transaction_type": "wire_transfer",
        "destination_country": "Iran",
        "destination_account": "ACC-99012",
        "account_age_days": 100,
        "kyc_level": 1,
        "pep_flag": False
    }
    response = client.post("/api/v1/transactions/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ESCALATE"
    assert len(data["violations"]) >= 1
    assert any(v["severity"] == "CRITICAL" for v in data["violations"])
    assert any(v["rule_id"] == "SNC-R1" for v in data["violations"])

def test_api_get_transactions_list(client):
    response = client.get("/api/v1/transactions?limit=10")
    assert response.status_code == 200
    txs = response.json()
    assert isinstance(txs, list)
    assert len(txs) >= 2
    tx_ids = [t["transaction_id"] for t in txs]
    assert "TX-IND-1001" in tx_ids
    assert "TX-IND-1002" in tx_ids

def test_api_get_transaction_detail(client):
    response = client.get("/api/v1/transactions/TX-IND-1001")
    assert response.status_code == 200
    detail = response.json()
    assert "transaction" in detail
    assert "decision" in detail
    assert "audit_logs" in detail
    assert detail["transaction"]["transaction_id"] == "TX-IND-1001"
    assert detail["decision"]["status"] == "APPROVED"
    assert len(detail["audit_logs"]) == 5

def test_api_get_transaction_detail_404_not_found(client):
    response = client.get("/api/v1/transactions/TX-NON-EXISTENT-9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"

def test_api_get_policies(client):
    response = client.get("/api/v1/policies")
    assert response.status_code == 200
    policies = response.json()
    assert isinstance(policies, list)
    assert len(policies) >= 5
    categories = {p["category"] for p in policies}
    assert {"KYC", "AML", "Limits", "Sanctions", "PEP"}.issubset(categories)

def test_api_get_policies_filtered_by_category(client):
    response = client.get("/api/v1/policies?category=Sanctions")
    assert response.status_code == 200
    policies = response.json()
    assert all(p["category"] == "Sanctions" for p in policies)

def test_api_get_metrics(client):
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    m = response.json()
    assert m["total_processed"] >= 2
    assert m["approved_count"] >= 1
    assert m["escalated_count"] >= 1
    assert "avg_processing_time_ms" in m
    assert "violations_by_category" in m

# ============================================================================
# 2. EDGE CASES & AGENT RESILIENCE TESTS
# ============================================================================

def test_agent_intake_missing_optional_fields():
    minimal_tx = {
        "transaction_id": "TX-MIN-001",
        "customer_id": "CUST-00",
        "amount": 100.0
    }
    state = run_multi_agent_pipeline(minimal_tx)
    assert state["transaction_id"] == "TX-MIN-001"
    assert state["decision"]["status"] == "APPROVED"
    assert len(state["agent_logs"]) == 5

def test_agent_risk_analysis_multiple_simultaneous_critical_violations():
    tx_extreme = {
        "transaction_id": "TX-EXTREME-01",
        "customer_id": "CUST-EXT",
        "amount": 750000.0,
        "destination_country": "Syria",
        "transaction_type": "cash_deposit",
        "kyc_level": 0,
        "pep_flag": True,
        "is_cross_border": True,
        "sow_verified": False
    }
    state = run_multi_agent_pipeline(tx_extreme)
    assert state["decision"]["status"] == "ESCALATE"
    violations = state["violations"]
    assert len(violations) >= 4
    rule_ids = {v["rule_id"] for v in violations}
    assert {"SNC-R1", "KYC-R1", "AML-R2", "LMT-R2", "PEP-R1"}.issubset(rule_ids)

def test_gemini_fallback_when_invalid_key():
    features = {
        "amount": 15000.0,
        "destination_country": "Iran",
        "kyc_level": 1
    }
    rule_violations = evaluate_deterministic_rules(features, [])
    os.environ["GEMINI_API_KEY"] = "INVALID_KEY_EXPLICIT_TEST"
    res = call_gemini_ai_reasoning(features, [], rule_violations)
    assert len(res) >= 1
    assert res[0]["rule_id"] == "SNC-R1"

# ============================================================================
# 3. VECTOR STORE PERFORMANCE & QUERY RIGOR
# ============================================================================

def test_vector_store_query_accuracy():
    store = VectorPolicyStore(persist_dir="./rigorous_test_chroma_db")
    policies = [
        {
            "policy_id": "POL-SNC-004",
            "category": "Sanctions",
            "title": "Sanctioned Countries Policy",
            "content": "Transactions involving OFAC comprehensive sanctions countries like Iran, North Korea, and Syria are subject to asset block."
        }
    ]
    store.add_policies(policies)
    results = store.search_policies(query="OFAC asset block sanctioned jurisdictions", top_k=1)
    assert len(results) >= 1
    assert results[0]["policy_id"] == "POL-SNC-004"
