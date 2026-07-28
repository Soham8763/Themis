# API Reference - THEMIS Compliance Engine

Base URL: `http://localhost:8000`

---

## REST Endpoints

### 1. Process Transaction
- **Endpoint**: `POST /api/v1/transactions/process`
- **Request Body**:
```json
{
  "transaction_id": "TX-1003",
  "customer_id": "CUST-9012",
  "customer_name": "Tehran Export Services",
  "amount": 42000.00,
  "currency": "USD",
  "transaction_type": "wire_transfer",
  "destination_country": "Iran",
  "destination_account": "ACC-11092",
  "account_age_days": 120,
  "kyc_level": 1,
  "pep_flag": false
}
```
- **Response**:
```json
{
  "transaction_id": "TX-1003",
  "status": "ESCALATE",
  "confidence": 0.98,
  "reasoning": "Immediate escalation triggered due to 1 critical regulatory violation(s).",
  "violations": [
    {
      "rule_id": "SNC-R1",
      "rule_name": "OFAC Comprehensive Sanctions Block",
      "category": "Sanctions",
      "severity": "CRITICAL",
      "reason": "Destination country 'Iran' is subject to OFAC comprehensive sanctions and asset block.",
      "confidence": 1.0
    }
  ],
  "agent_decisions": [...],
  "audit_trail_id": "AUD-B91A20C4",
  "timestamp": "2026-07-28T15:10:00Z"
}
```

### 2. List Transactions
- **Endpoint**: `GET /api/v1/transactions?limit=50`

### 3. Get Transaction Detail
- **Endpoint**: `GET /api/v1/transactions/{transaction_id}`

### 4. List Policies
- **Endpoint**: `GET /api/v1/policies?category=KYC`

### 5. Get Compliance Metrics
- **Endpoint**: `GET /api/v1/metrics`

---

## WebSocket Endpoint

- **Endpoint**: `ws://localhost:8000/ws`
- **Event Broadcast Payload**:
```json
{
  "event": "transaction_processed",
  "data": { ... }
}
```
