import datetime
import uuid
from app.agents.state import AgentState

def audit_agent(state: AgentState) -> AgentState:
    """
    Agent 5: Audit Logger Agent
    Compiles complete multi-agent execution lineage and decision history into an immutable compliance audit record.
    """
    tx_id = state.get("transaction_id", "UNKNOWN")
    decision = state.get("decision", {})
    logs = state.get("agent_logs", [])
    violations = state.get("violations", [])

    audit_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"

    audit_summary = {
        "audit_record_id": audit_id,
        "transaction_id": tx_id,
        "final_status": decision.get("status", "UNKNOWN"),
        "confidence": decision.get("confidence", 1.0),
        "total_agent_steps": len(logs) + 1,
        "violations_logged": len(violations),
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    log_entry = {
        "agent_id": "agent-5-audit",
        "agent_name": "Compliance Audit Logger Agent",
        "output": audit_summary,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return {
        **state,
        "audit_record_id": audit_id,
        "agent_logs": logs + [log_entry]
    }
