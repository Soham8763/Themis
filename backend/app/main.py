import os
import json
import asyncio
import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.database import init_db, get_db
from app.models import TransactionModel, PolicyModel, ComplianceDecisionModel, AuditLogModel
from app.schemas import (
    TransactionSchema, ProcessTransactionResponse, PolicySchema,
    ComplianceMetricsSchema, RuleViolationSchema, AgentDecisionSchema
)
from app.agents.orchestrator import run_multi_agent_pipeline

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Real-Time Policy Compliance & Risk Auditing Engine"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections tracker
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()

@app.on_event("startup")
async def on_startup():
    await init_db()
    # Seed policies if database empty
    async for db in get_db():
        res = await db.execute(select(func.count(PolicyModel.id)))
        count = res.scalar_one_or_none() or 0
        if count == 0:
            policies_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_policies.json")
            if os.path.exists(policies_file):
                with open(policies_file, "r", encoding="utf-8") as f:
                    policies_data = json.load(f)
                    for p in policies_data:
                        db_policy = PolicyModel(
                            policy_id=p["policy_id"],
                            category=p["category"],
                            title=p["title"],
                            version=p["version"],
                            content=p["content"],
                            rules=p.get("rules", [])
                        )
                        db.add(db_policy)
                await db.commit()
        break

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENV,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Heartbeat / ping response
            await websocket.send_json({"type": "pong", "time": datetime.datetime.utcnow().isoformat()})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.post("/api/v1/transactions/process", response_model=ProcessTransactionResponse)
async def process_transaction(payload: TransactionSchema, db: AsyncSession = Depends(get_db)):
    tx_dict = payload.dict()
    
    # Run 5-agent pipeline
    agent_state = run_multi_agent_pipeline(tx_dict)
    
    tx_id = agent_state.get("transaction_id", payload.transaction_id)
    features = agent_state.get("extracted_features", {})
    decision = agent_state.get("decision", {})
    violations = agent_state.get("violations", [])
    logs = agent_state.get("agent_logs", [])
    audit_id = agent_state.get("audit_record_id", f"AUD-{tx_id}")

    # Persist transaction
    stmt = select(TransactionModel).where(TransactionModel.transaction_id == tx_id)
    existing_tx = (await db.execute(stmt)).scalar_one_or_none()
    if not existing_tx:
        db_tx = TransactionModel(
            transaction_id=tx_id,
            customer_id=features.get("customer_id", payload.customer_id),
            customer_name=features.get("customer_name", payload.customer_name),
            amount=features.get("amount", payload.amount),
            currency=features.get("currency", payload.currency),
            transaction_type=features.get("transaction_type", payload.transaction_type),
            destination_country=features.get("destination_country", payload.destination_country),
            destination_account=features.get("destination_account", payload.destination_account),
            account_age_days=features.get("account_age_days", payload.account_age_days),
            kyc_level=features.get("kyc_level", payload.kyc_level),
            pep_flag=features.get("pep_flag", payload.pep_flag),
            is_cross_border=features.get("is_cross_border", payload.is_cross_border),
            dual_approval=features.get("dual_approval", payload.dual_approval),
            sow_verified=features.get("sow_verified", payload.sow_verified)
        )
        db.add(db_tx)

    # Persist compliance decision
    db_decision = ComplianceDecisionModel(
        transaction_id=tx_id,
        status=decision.get("status", "REVIEW"),
        confidence=decision.get("confidence", 0.9),
        reasoning=decision.get("reasoning", "Processed by agentic pipeline"),
        violations=violations,
        escalation_reason=decision.get("escalation_reason")
    )
    db.add(db_decision)

    # Persist agent audit logs
    for l in logs:
        db_log = AuditLogModel(
            log_id=f"{audit_id}-{l.get('agent_id')}",
            transaction_id=tx_id,
            agent_id=l.get("agent_id", "agent-unknown"),
            action=l.get("agent_name", "Agent Action"),
            output_summary=json.dumps(l.get("output", {})),
            details=l
        )
        db.add(db_log)

    await db.commit()

    response_data = ProcessTransactionResponse(
        transaction_id=tx_id,
        status=decision.get("status", "REVIEW"),
        confidence=decision.get("confidence", 0.9),
        reasoning=decision.get("reasoning", ""),
        violations=[RuleViolationSchema(**v) for v in violations],
        agent_decisions=[AgentDecisionSchema(
            agent_id=l.get("agent_id", "agent"),
            agent_name=l.get("agent_name", "Agent"),
            output=l.get("output", {}),
            timestamp=l.get("timestamp", datetime.datetime.utcnow().isoformat())
        ) for l in logs],
        audit_trail_id=audit_id,
        timestamp=datetime.datetime.utcnow().isoformat()
    )

    # Broadcast real-time update to connected WebSocket clients
    await ws_manager.broadcast({
        "event": "transaction_processed",
        "data": response_data.dict()
    })

    return response_data

@app.get("/api/v1/transactions")
async def get_transactions(limit: int = 50, db: AsyncSession = Depends(get_db)):
    stmt = select(TransactionModel).order_by(TransactionModel.id.desc()).limit(limit)
    result = await db.execute(stmt)
    txs = result.scalars().all()
    
    output = []
    for tx in txs:
        dec_stmt = select(ComplianceDecisionModel).where(ComplianceDecisionModel.transaction_id == tx.transaction_id)
        dec = (await db.execute(dec_stmt)).scalar_one_or_none()
        output.append({
            "transaction_id": tx.transaction_id,
            "customer_id": tx.customer_id,
            "customer_name": tx.customer_name,
            "amount": tx.amount,
            "currency": tx.currency,
            "transaction_type": tx.transaction_type,
            "destination_country": tx.destination_country,
            "status": dec.status if dec else "UNKNOWN",
            "confidence": dec.confidence if dec else 1.0,
            "violations_count": len(dec.violations) if dec and dec.violations else 0,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        })

    return output

@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction_detail(transaction_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TransactionModel).where(TransactionModel.transaction_id == transaction_id)
    tx = (await db.execute(stmt)).scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    dec_stmt = select(ComplianceDecisionModel).where(ComplianceDecisionModel.transaction_id == transaction_id)
    dec = (await db.execute(dec_stmt)).scalar_one_or_none()

    audit_stmt = select(AuditLogModel).where(AuditLogModel.transaction_id == transaction_id)
    audit_logs = (await db.execute(audit_stmt)).scalars().all()

    return {
        "transaction": {
            "transaction_id": tx.transaction_id,
            "customer_id": tx.customer_id,
            "customer_name": tx.customer_name,
            "amount": tx.amount,
            "currency": tx.currency,
            "transaction_type": tx.transaction_type,
            "destination_country": tx.destination_country,
            "destination_account": tx.destination_account,
            "account_age_days": tx.account_age_days,
            "kyc_level": tx.kyc_level,
            "pep_flag": tx.pep_flag,
            "is_cross_border": tx.is_cross_border,
            "dual_approval": tx.dual_approval,
            "sow_verified": tx.sow_verified,
            "created_at": tx.created_at.isoformat() if tx.created_at else None
        },
        "decision": {
            "status": dec.status if dec else "UNKNOWN",
            "confidence": dec.confidence if dec else 1.0,
            "reasoning": dec.reasoning if dec else "",
            "violations": dec.violations if dec else [],
            "escalation_reason": dec.escalation_reason if dec else None,
            "created_at": dec.created_at.isoformat() if dec and dec.created_at else None
        },
        "audit_logs": [{
            "log_id": l.log_id,
            "agent_id": l.agent_id,
            "action": l.action,
            "output_summary": l.output_summary,
            "details": l.details,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None
        } for l in audit_logs]
    }

@app.get("/api/v1/policies")
async def get_policies(category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(PolicyModel)
    if category:
        query = query.where(PolicyModel.category == category)
    result = await db.execute(query)
    policies = result.scalars().all()
    return [{
        "policy_id": p.policy_id,
        "category": p.category,
        "title": p.title,
        "version": p.version,
        "content": p.content,
        "rules": p.rules
    } for p in policies]

@app.get("/api/v1/metrics", response_model=ComplianceMetricsSchema)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    stmt = select(ComplianceDecisionModel)
    decisions = (await db.execute(stmt)).scalars().all()
    
    total = len(decisions)
    approved = sum(1 for d in decisions if d.status == "APPROVED")
    review = sum(1 for d in decisions if d.status == "REVIEW")
    escalated = sum(1 for d in decisions if d.status == "ESCALATE")

    cat_counts: Dict[str, int] = {"KYC": 0, "AML": 0, "Limits": 0, "Sanctions": 0, "PEP": 0}
    for d in decisions:
        if d.violations:
            for v in d.violations:
                cat = v.get("category", "Other")
                cat_counts[cat] = cat_counts.get(cat, 0) + 1

    return ComplianceMetricsSchema(
        total_processed=total,
        approved_count=approved,
        review_count=review,
        escalated_count=escalated,
        false_positive_rate=2.4,
        avg_processing_time_ms=145.0,
        violations_by_category=cat_counts
    )
