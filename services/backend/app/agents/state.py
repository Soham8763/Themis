from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict, total=False):
    transaction_id: str
    raw_transaction: Dict[str, Any]
    extracted_features: Dict[str, Any]
    relevant_policies: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    decision: Dict[str, Any]
    agent_logs: List[Dict[str, Any]]
    audit_record_id: Optional[str]
    errors: List[str]
