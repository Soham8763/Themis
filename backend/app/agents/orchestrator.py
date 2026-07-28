from typing import Dict, Any
from app.agents.state import AgentState
from app.agents.intake_agent import intake_agent
from app.agents.policy_retrieval_agent import policy_retrieval_agent
from app.agents.risk_analysis_agent import risk_analysis_agent
from app.agents.decision_agent import decision_agent
from app.agents.audit_agent import audit_agent

def run_multi_agent_pipeline(raw_transaction: Dict[str, Any]) -> AgentState:
    """
    Executes the 5-agent compliance auditing pipeline sequentially:
    Intake -> Policy Retrieval -> Risk Analysis -> Decision Engine -> Audit Logger
    """
    initial_state: AgentState = {
        "raw_transaction": raw_transaction,
        "transaction_id": raw_transaction.get("transaction_id", ""),
        "extracted_features": {},
        "relevant_policies": [],
        "violations": [],
        "decision": {},
        "agent_logs": [],
        "audit_record_id": None,
        "errors": []
    }

    try:
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(AgentState)

        workflow.add_node("intake", intake_agent)
        workflow.add_node("retrieval", policy_retrieval_agent)
        workflow.add_node("analysis", risk_analysis_agent)
        workflow.add_node("decision", decision_agent)
        workflow.add_node("audit", audit_agent)

        workflow.set_entry_point("intake")
        workflow.add_edge("intake", "retrieval")
        workflow.add_edge("retrieval", "analysis")
        workflow.add_edge("analysis", "decision")
        workflow.add_edge("decision", "audit")
        workflow.add_edge("audit", END)

        app = workflow.compile()
        final_state = app.invoke(initial_state)
        return final_state
    except Exception:
        # Robust fallback execution loop
        s1 = intake_agent(initial_state)
        s2 = policy_retrieval_agent(s1)
        s3 = risk_analysis_agent(s2)
        s4 = decision_agent(s3)
        s5 = audit_agent(s4)
        return s5
