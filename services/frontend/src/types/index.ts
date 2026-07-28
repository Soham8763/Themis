export type DecisionStatus = 'APPROVED' | 'REVIEW' | 'ESCALATE';
export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface RuleViolation {
  rule_id: string;
  rule_name: string;
  category: string;
  severity: SeverityLevel;
  reason: string;
  confidence: number;
}

export interface AgentLog {
  agent_id: string;
  agent_name: string;
  output: Record<string, any>;
  timestamp: string;
}

export interface TransactionItem {
  transaction_id: string;
  customer_id: string;
  customer_name: string;
  amount: number;
  currency: string;
  transaction_type: string;
  destination_country: string;
  status: DecisionStatus;
  confidence: number;
  violations_count: number;
  created_at: string;
}

export interface TransactionDetail {
  transaction: {
    transaction_id: string;
    customer_id: string;
    customer_name: string;
    amount: number;
    currency: string;
    transaction_type: string;
    destination_country: string;
    destination_account: string;
    account_age_days: number;
    kyc_level: number;
    pep_flag: boolean;
    is_cross_border: boolean;
    dual_approval: boolean;
    sow_verified: boolean;
    created_at: string;
  };
  decision: {
    status: DecisionStatus;
    confidence: number;
    reasoning: string;
    violations: RuleViolation[];
    escalation_reason?: string;
    created_at: string;
  };
  audit_logs: AgentLog[];
}

export interface Policy {
  policy_id: string;
  category: string;
  title: string;
  version: string;
  content: string;
  rules: any[];
}

export interface ComplianceMetrics {
  total_processed: number;
  approved_count: number;
  review_count: number;
  escalated_count: number;
  false_positive_rate: number;
  avg_processing_time_ms: number;
  violations_by_category: Record<string, number>;
}
