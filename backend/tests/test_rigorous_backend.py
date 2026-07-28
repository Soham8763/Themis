import pytest
import asyncio
from app.agents.intake_agent import intake_agent
from app.agents.policy_retrieval_agent import policy_retrieval_agent
from app.agents.risk_analysis_agent import risk_analysis_agent, evaluate_deterministic_rules
from app.agents.decision_agent import decision_agent
from app.agents.audit_agent import audit_agent
from app.agents.orchestrator import run_multi_agent_pipeline
from app.rag.vector_store import VectorPolicyStore

# ============================================================================
# 1. COMPLIANT TRANSACTIONS TEST CASES
# ============================================================================

def test_compliant_domestic_merchant_payment():
    tx = {
        "transaction_id": "TX-RIG-001",
        "customer_id": "CUST-101",
        "customer_name": "Retail Store",
        "amount": 450.0,
        "destination_country": "United States",
        "transaction_type": "merchant_payment",
        "kyc_level": 1,
        "account_age_days": 365,
        "pep_flag": False
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "APPROVED"
    assert state["decision"]["confidence"] == 1.0
    assert len(state["violations"]) == 0
    assert state["audit_record_id"].startswith("AUD-")

def test_compliant_small_wire_transfer():
    tx = {
        "transaction_id": "TX-RIG-002",
        "customer_id": "CUST-102",
        "customer_name": "Small Tech Inc",
        "amount": 4500.0,
        "destination_country": "United Kingdom",
        "transaction_type": "wire_transfer",
        "kyc_level": 1,
        "account_age_days": 180,
        "pep_flag": False
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "APPROVED"

# ============================================================================
# 2. SANCTIONS & HIGH-RISK JURISDICTION TEST CASES
# ============================================================================

def test_critical_ofac_sanctioned_country_iran():
    tx = {
        "transaction_id": "TX-RIG-003",
        "customer_id": "CUST-103",
        "customer_name": "Iran Exporters",
        "amount": 15000.0,
        "destination_country": "Iran",
        "transaction_type": "wire_transfer"
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    severities = [v["severity"] for v in state["violations"]]
    assert "CRITICAL" in severities
    rules = [v["rule_id"] for v in state["violations"]]
    assert "SNC-R1" in rules

def test_critical_ofac_sanctioned_country_syria():
    tx = {
        "transaction_id": "TX-RIG-004",
        "customer_id": "CUST-104",
        "customer_name": "Damascus Corp",
        "amount": 8500.0,
        "destination_country": "Syria",
        "transaction_type": "wire_transfer"
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    assert "CRITICAL" in [v["severity"] for v in state["violations"]]

def test_high_risk_fatf_grey_country_myanmar():
    tx = {
        "transaction_id": "TX-RIG-005",
        "customer_id": "CUST-105",
        "customer_name": "Yangon Trading",
        "amount": 18000.0,
        "destination_country": "Myanmar",
        "transaction_type": "wire_transfer"
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    rules = [v["rule_id"] for v in state["violations"]]
    assert "SNC-R2" in rules

# ============================================================================
# 3. KYC POLICY TEST CASES
# ============================================================================

def test_kyc_unverified_account_high_amount():
    tx = {
        "transaction_id": "TX-RIG-006",
        "customer_id": "CUST-106",
        "customer_name": "Unverified User",
        "amount": 4800.0,
        "destination_country": "United States",
        "transaction_type": "wire_transfer",
        "kyc_level": 0
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    rules = [v["rule_id"] for v in state["violations"]]
    assert "KYC-R1" in rules

def test_kyc_new_account_large_wire():
    tx = {
        "transaction_id": "TX-RIG-007",
        "customer_id": "CUST-107",
        "customer_name": "New Account Corp",
        "amount": 15000.0,
        "destination_country": "France",
        "transaction_type": "wire_transfer",
        "account_age_days": 12,
        "kyc_level": 1
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] in ["REVIEW", "ESCALATE"]
    rules = [v["rule_id"] for v in state["violations"]]
    assert "KYC-R2" in rules

# ============================================================================
# 4. AML POLICY TEST CASES
# ============================================================================

def test_aml_mandatory_ctr_threshold():
    tx = {
        "transaction_id": "TX-RIG-008",
        "customer_id": "CUST-108",
        "customer_name": "Standard Business",
        "amount": 11500.0,
        "destination_country": "United States",
        "transaction_type": "wire_transfer",
        "kyc_level": 1,
        "account_age_days": 300
    }
    state = run_multi_agent_pipeline(tx)
    rules = [v["rule_id"] for v in state["violations"]]
    assert "AML-R1" in rules

def test_aml_excessive_cash_deposit():
    tx = {
        "transaction_id": "TX-RIG-009",
        "customer_id": "CUST-109",
        "customer_name": "Cash Holdings Inc",
        "amount": 62000.0,
        "destination_country": "United States",
        "transaction_type": "cash_deposit",
        "kyc_level": 1
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    rules = [v["rule_id"] for v in state["violations"]]
    assert "AML-R2" in rules

# ============================================================================
# 5. TRANSACTION LIMITS TEST CASES
# ============================================================================

def test_limits_high_value_wire_no_dual_approval():
    tx = {
        "transaction_id": "TX-RIG-010",
        "customer_id": "CUST-110",
        "customer_name": "Global Investments",
        "amount": 125000.0,
        "destination_country": "United Kingdom",
        "transaction_type": "wire_transfer",
        "dual_approval": False
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    rules = [v["rule_id"] for v in state["violations"]]
    assert "LMT-R1" in rules

def test_limits_executive_review_threshold():
    tx = {
        "transaction_id": "TX-RIG-011",
        "customer_id": "CUST-111",
        "customer_name": "Mega Acquisition Corp",
        "amount": 650000.0,
        "destination_country": "Germany",
        "transaction_type": "wire_transfer"
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    rules = [v["rule_id"] for v in state["violations"]]
    assert "LMT-R2" in rules

# ============================================================================
# 6. PEP POLICY TEST CASES
# ============================================================================

def test_pep_cross_border_unverified_sow():
    tx = {
        "transaction_id": "TX-RIG-012",
        "customer_id": "CUST-112",
        "customer_name": "Senator Vance",
        "amount": 35000.0,
        "destination_country": "Switzerland",
        "transaction_type": "wire_transfer",
        "pep_flag": True,
        "is_cross_border": True,
        "sow_verified": False
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] == "ESCALATE"
    rules = [v["rule_id"] for v in state["violations"]]
    assert "PEP-R1" in rules

def test_pep_activity_flag():
    tx = {
        "transaction_id": "TX-RIG-013",
        "customer_id": "CUST-113",
        "customer_name": "Diplomat Elena Rostova",
        "amount": 45000.0,
        "destination_country": "Singapore",
        "transaction_type": "wire_transfer",
        "pep_flag": True,
        "is_cross_border": True,
        "sow_verified": True
    }
    state = run_multi_agent_pipeline(tx)
    assert state["decision"]["status"] in ["REVIEW", "APPROVED"]
    rules = [v["rule_id"] for v in state["violations"]]
    assert "PEP-R2" in rules

# ============================================================================
# 7. RAG VECTOR STORE INTEGRATION TEST
# ============================================================================

def test_vector_policy_store_semantic_search():
    store = VectorPolicyStore(persist_dir="./rigorous_test_chroma_db")
    policies = [
        {
            "policy_id": "POL-SNC-004",
            "category": "Sanctions",
            "title": "Sanctioned Countries Policy",
            "content": "Transactions to OFAC comprehensive sanctions countries like Iran, North Korea, and Syria are blocked."
        },
        {
            "policy_id": "POL-KYC-001",
            "category": "KYC",
            "title": "Customer Verification",
            "content": "Unverified level 0 customers cannot transfer more than 2500 dollars."
        }
    ]
    store.add_policies(policies)

    res = store.search_policies("Iran sanctioned block", top_k=1)
    assert len(res) == 1
    assert res[0]["policy_id"] == "POL-SNC-004"
