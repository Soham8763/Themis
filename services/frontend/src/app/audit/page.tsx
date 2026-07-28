'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AuditTrailViewer } from '@/components/AuditTrailViewer';
import { AgentLog } from '@/types';

export default function AuditPage() {
  const [txId, setTxId] = useState<string>('TX-1003');
  const [logs, setLogs] = useState<AgentLog[]>([]);

  const fetchAudit = useCallback((id: string) => {
    if (!id) return;
    fetch(`/api/v1/transactions/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.audit_logs) {
          setLogs(data.audit_logs);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchAudit(txId);
  }, [fetchAudit, txId]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-white tracking-wide">Audit Trail Inspector</h1>
        <p className="text-sm text-dark-muted mt-1">Regulatory decision lineage & step-by-step multi-agent execution record</p>
      </div>

      <div className="flex items-center gap-3 bg-dark-card/60 p-3 rounded-2xl border border-dark-border max-w-md">
        <span className="text-xs font-semibold text-dark-muted font-mono">TX ID:</span>
        <input
          type="text"
          value={txId}
          onChange={(e) => setTxId(e.target.value)}
          placeholder="e.g. TX-1003"
          className="bg-dark-bg text-white font-mono text-sm px-3 py-1.5 rounded-xl border border-dark-border flex-1 focus:outline-none focus:border-brand-500"
        />
        <button
          onClick={() => fetchAudit(txId)}
          className="px-4 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold transition-colors"
        >
          Load Audit
        </button>
      </div>

      <AuditTrailViewer logs={logs} transactionId={txId} />
    </div>
  );
}
