import datetime
from sqlalchemy import String, Float, Boolean, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(64), index=True)
    customer_name: Mapped[str] = mapped_column(String(128))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    transaction_type: Mapped[str] = mapped_column(String(64))
    destination_country: Mapped[str] = mapped_column(String(64))
    destination_account: Mapped[str] = mapped_column(String(64))
    account_age_days: Mapped[int] = mapped_column(Integer, default=0)
    kyc_level: Mapped[int] = mapped_column(Integer, default=1)
    pep_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    is_cross_border: Mapped[bool] = mapped_column(Boolean, default=False)
    dual_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    sow_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    decision = relationship("ComplianceDecisionModel", back_populates="transaction", uselist=False)
    audit_logs = relationship("AuditLogModel", back_populates="transaction")

class PolicyModel(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    policy_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256))
    version: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    rules: Mapped[dict] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

class ComplianceDecisionModel(Base):
    __tablename__ = "compliance_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(String(64), ForeignKey("transactions.transaction_id"), index=True)
    status: Mapped[str] = mapped_column(String(32)) # APPROVED, REVIEW, ESCALATE
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    reasoning: Mapped[str] = mapped_column(Text)
    violations: Mapped[list] = mapped_column(JSON, default=list)
    escalation_reason: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    transaction = relationship("TransactionModel", back_populates="decision")

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    log_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    transaction_id: Mapped[str] = mapped_column(String(64), ForeignKey("transactions.transaction_id"), index=True)
    agent_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(128))
    output_summary: Mapped[str] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    transaction = relationship("TransactionModel", back_populates="audit_logs")
