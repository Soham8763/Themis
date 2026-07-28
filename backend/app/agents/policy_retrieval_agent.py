import os
import json
import datetime
from typing import List, Dict, Any
from app.agents.state import AgentState

POLICIES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sample_policies.json")

def load_all_policies() -> List[Dict[str, Any]]:
    if os.path.exists(POLICIES_PATH):
        try:
            with open(POLICIES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def policy_retrieval_agent(state: AgentState) -> AgentState:
    """
    Agent 2: Policy Retrieval Agent (RAG Baseline)
    Retrieves all relevant regulatory compliance policies based on transaction attributes.
    """
    features = state.get("extracted_features", {})
    logs = state.get("agent_logs", [])
    all_policies = load_all_policies()

    selected_categories = set()

    # Determine policy categories needed based on transaction features
    if features.get("is_unverified") or features.get("is_new_account") or features.get("amount", 0) > 2500:
        selected_categories.add("KYC")

    if features.get("amount", 0) >= 10000 or features.get("transaction_type") == "cash_deposit":
        selected_categories.add("AML")

    if features.get("amount", 0) >= 100000 or features.get("is_high_value"):
        selected_categories.add("Limits")

    if features.get("is_sanctioned_country") or features.get("is_fatf_grey_country") or features.get("is_cross_border"):
        selected_categories.add("Sanctions")

    if features.get("pep_flag"):
        selected_categories.add("PEP")

    # Fallback to loading all policies if no specific category matched
    if not selected_categories:
        relevant_policies = all_policies
    else:
        relevant_policies = [p for p in all_policies if p.get("category") in selected_categories or "all" in selected_categories]

    log_entry = {
        "agent_id": "agent-2-retrieval",
        "agent_name": "Policy Retrieval Agent",
        "output": {
            "retrieved_count": len(relevant_policies),
            "categories": list(selected_categories),
            "policies": [p.get("policy_id") for p in relevant_policies]
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return {
        **state,
        "relevant_policies": relevant_policies,
        "agent_logs": logs + [log_entry]
    }
