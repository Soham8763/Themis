import datetime
from typing import Dict, Any
from app.agents.state import AgentState

SANCTIONED_COUNTRIES = {"iran", "north korea", "syria", "cuba", "crimea"}
FATF_HIGH_RISK = {"myanmar", "yemen", "south sudan"}

def intake_agent(state: AgentState) -> AgentState:
    """
    Agent 1: Transaction Intake & Structuring Agent
    Parses, validates, and extracts structured risk indicators from raw transaction payload.
    """
    raw_tx = state.get("raw_transaction", {})
    errors = state.get("errors", [])
    logs = state.get("agent_logs", [])

    tx_id = raw_tx.get("transaction_id", f"TX-{int(datetime.datetime.utcnow().timestamp())}")
    amount = float(raw_tx.get("amount", 0.0))
    dest_country = str(raw_tx.get("destination_country", "")).strip()
    account_age = int(raw_tx.get("account_age_days", 0))
    kyc_level = int(raw_tx.get("kyc_level", 1))
    pep_flag = bool(raw_tx.get("pep_flag", False))
    tx_type = str(raw_tx.get("transaction_type", "wire_transfer")).lower()
    is_cross_border = bool(raw_tx.get("is_cross_border", dest_country.lower() != "united states"))
    dual_approval = bool(raw_tx.get("dual_approval", False))
    sow_verified = bool(raw_tx.get("sow_verified", False))

    # Feature extraction & classification
    dest_country_lower = dest_country.lower()
    is_sanctioned = dest_country_lower in SANCTIONED_COUNTRIES
    is_fatf_grey = dest_country_lower in FATF_HIGH_RISK

    extracted_features = {
        "transaction_id": tx_id,
        "customer_id": raw_tx.get("customer_id", "UNKNOWN"),
        "customer_name": raw_tx.get("customer_name", "Valued Customer"),
        "amount": amount,
        "currency": raw_tx.get("currency", "USD"),
        "transaction_type": tx_type,
        "destination_country": dest_country,
        "destination_account": raw_tx.get("destination_account", "N/A"),
        "account_age_days": account_age,
        "kyc_level": kyc_level,
        "pep_flag": pep_flag,
        "is_cross_border": is_cross_border,
        "dual_approval": dual_approval,
        "sow_verified": sow_verified,
        "is_high_value": amount >= 100000.0,
        "is_critical_value": amount >= 500000.0,
        "is_sanctioned_country": is_sanctioned,
        "is_fatf_grey_country": is_fatf_grey,
        "is_new_account": account_age < 30,
        "is_unverified": kyc_level == 0,
        "timestamp": raw_tx.get("timestamp", datetime.datetime.utcnow().isoformat())
    }

    log_entry = {
        "agent_id": "agent-1-intake",
        "agent_name": "Intake & Structuring Agent",
        "output": {
            "summary": f"Processed transaction {tx_id} for amount ${amount:,.2f}",
            "risk_flags": {
                "high_value": extracted_features["is_high_value"],
                "sanctioned_country": is_sanctioned,
                "pep": pep_flag,
                "unverified": extracted_features["is_unverified"]
            }
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return {
        **state,
        "transaction_id": tx_id,
        "extracted_features": extracted_features,
        "agent_logs": logs + [log_entry],
        "errors": errors
    }
