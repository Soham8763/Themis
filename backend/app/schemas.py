from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class TransactionSchema(BaseModel):
    transaction_id: str
    customer_id: str
    customer_name: str
    amount: float
    currency: str = "USD"
    transaction_type: str
    destination_country: str
    destination_account: str
    account_age_days: int = 0
    kyc_level: int = 1
    pep_flag: bool = False
    is_cross_border: bool = False
    dual_approval: bool = False
    sow_verified: bool = False
    timestamp: Optional[str] = None

class RuleViolationSchema(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    reason: str
    confidence: float = 1.0

class AgentDecisionSchema(BaseModel):
    agent_id: str
    agent_name: str
    output: Dict[str, Any]
    timestamp: str

class ComplianceDecisionSchema(BaseModel):
    transaction_id: str
    status: str # APPROVED, REVIEW, ESCALATE
    confidence: float
    reasoning: str
    violations: List[RuleViolationSchema] = []
    escalation_reason: Optional[str] = None
    created_at: str

class ProcessTransactionResponse(BaseModel):
    transaction_id: str
    status: str
    confidence: float
    reasoning: str
    violations: List[RuleViolationSchema]
    agent_decisions: List[AgentDecisionSchema]
    audit_trail_id: str
    timestamp: str

class PolicySchema(BaseModel):
    policy_id: str
    category: str
    title: str
    version: str
    content: str
    rules: List[Dict[str, Any]] = []

class ComplianceMetricsSchema(BaseModel):
    total_processed: int
    approved_count: int
    review_count: int
    escalated_count: int
    false_positive_rate: float
    avg_processing_time_ms: float
    violations_by_category: Dict[str, int]
