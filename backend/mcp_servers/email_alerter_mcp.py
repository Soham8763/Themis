import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

mcp_app = FastAPI(title="Email Alerter MCP Server", version="1.0.0")

class SendAlertRequest(BaseModel):
    transaction_id: str
    recipient_email: Optional[str] = "compliance-alerts@azentio-themis.com"
    violations: List[Dict[str, Any]]
    decision_status: str
    escalation_reason: Optional[str] = None

@mcp_app.get("/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": "send_violation_alert",
                "description": "Send high-priority compliance violation alert emails to compliance officers.",
                "parameters": {
                    "transaction_id": "string",
                    "recipient_email": "string",
                    "violations": "array of violation objects",
                    "decision_status": "APPROVED | REVIEW | ESCALATE"
                }
            }
        ]
    }

@mcp_app.post("/tools/send_violation_alert")
async def send_violation_alert(req: SendAlertRequest):
    # Simulated email alert dispatch
    alert_payload = {
        "alert_id": f"ALT-{req.transaction_id}",
        "recipient": req.recipient_email,
        "transaction_id": req.transaction_id,
        "status": req.decision_status,
        "violations_count": len(req.violations),
        "escalation_reason": req.escalation_reason,
        "dispatched_at": datetime.datetime.utcnow().isoformat(),
        "delivered": True
    }
    return {
        "status": "success",
        "message": f"Compliance violation alert for transaction {req.transaction_id} successfully sent to {req.recipient_email}.",
        "alert": alert_payload
    }

if __name__ == "__main__":
    uvicorn.run(mcp_app, host="0.0.0.0", port=8002)
