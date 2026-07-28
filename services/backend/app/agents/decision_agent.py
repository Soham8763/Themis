import datetime
from typing import Dict, Any, List
from app.agents.state import AgentState

def decision_agent(state: AgentState) -> AgentState:
    """
    Agent 4: Decision Engine Agent
    Synthesizes risk analysis violations into a final compliance status (APPROVED, REVIEW, ESCALATE)
    with confidence scoring and detailed reasoning.
    """
    features = state.get("extracted_features", {})
    violations = state.get("violations", [])
    logs = state.get("agent_logs", [])

    severities = [v.get("severity", "LOW").upper() for v in violations]

    status = "APPROVED"
    escalation_reason = None
    confidence = 1.0
    reasoning_parts = []

    if "CRITICAL" in severities:
        status = "ESCALATE"
        critical_violations = [v for v in violations if v.get("severity") == "CRITICAL"]
        escalation_reason = f"CRITICAL Compliance Violation: {critical_violations[0].get('rule_name')} - {critical_violations[0].get('reason')}"
        reasoning_parts.append(f"Immediate escalation triggered due to {len(critical_violations)} critical regulatory violation(s).")
        confidence = 0.98
    elif "HIGH" in severities:
        status = "ESCALATE"
        high_violations = [v for v in violations if v.get("severity") == "HIGH"]
        escalation_reason = f"HIGH Risk Violation: {high_violations[0].get('rule_name')} - {high_violations[0].get('reason')}"
        reasoning_parts.append(f"Escalated due to {len(high_violations)} high-severity policy violation(s). Dual sign-off or compliance officer review required.")
        confidence = 0.95
    elif "MEDIUM" in severities:
        status = "REVIEW"
        med_violations = [v for v in violations if v.get("severity") == "MEDIUM"]
        reasoning_parts.append(f"Flagged for Compliance Review due to {len(med_violations)} medium-severity indicator(s).")
        confidence = 0.90
    elif "LOW" in severities:
        status = "APPROVED" # CTR notification needed, but transaction can proceed with log
        reasoning_parts.append("Transaction approved subject to automated regulatory reporting (CTR filing required).")
        confidence = 0.99
    else:
        status = "APPROVED"
        reasoning_parts.append("Transaction fully compliant with all active regulatory policies and internal risk limits.")
        confidence = 1.0

    # Add detail for all violations
    if violations:
        reasoning_parts.append("Summary of Identified Policy Violations:")
        for idx, v in enumerate(violations, 1):
            reasoning_parts.append(f"{idx}. [{v.get('severity')}] {v.get('rule_name')}: {v.get('reason')}")

    full_reasoning = "\n".join(reasoning_parts)

    decision_output = {
        "status": status,
        "confidence": confidence,
        "reasoning": full_reasoning,
        "escalation_reason": escalation_reason,
        "violations_count": len(violations)
    }

    log_entry = {
        "agent_id": "agent-4-decision",
        "agent_name": "Decision Engine Agent",
        "output": decision_output,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    return {
        **state,
        "decision": decision_output,
        "agent_logs": logs + [log_entry]
    }
