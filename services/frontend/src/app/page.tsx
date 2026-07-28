'use client';

import React, { useState, useEffect } from 'react';
import { MetricsOverview } from '@/components/MetricsOverview';
import { TransactionFeed } from '@/components/TransactionFeed';
import { ViolationDetailModal } from '@/components/ViolationDetailModal';
import { ComplianceMetrics, TransactionItem, TransactionDetail } from '@/types';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<ComplianceMetrics>({
    total_processed: 20,
    approved_count: 5,
    review_count: 5,
    escalated_count: 10,
    false_positive_rate: 2.4,
    avg_processing_time_ms: 142.5,
    violations_by_category: { KYC: 4, AML: 5, Limits: 6, Sanctions: 5, PEP: 4 }
  });

  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [selectedTxId, setSelectedTxId] = useState<string | null>(null);
  const [txDetail, setTxDetail] = useState<TransactionDetail | null>(null);

  useEffect(() => {
    // Fetch metrics
    fetch('/api/v1/metrics')
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch(() => {});

    // Fetch transactions
    fetch('/api/v1/transactions')
      .then((res) => res.json())
      .then((data) => setTransactions(data))
      .catch(() => {});

    // WebSocket real-time updates
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.event === 'transaction_processed') {
          const newTx = msg.data;
          setTransactions((prev) => [newTx, ...prev]);
          setMetrics((prev) => ({
            ...prev,
            total_processed: prev.total_processed + 1,
            approved_count: newTx.status === 'APPROVED' ? prev.approved_count + 1 : prev.approved_count,
            review_count: newTx.status === 'REVIEW' ? prev.review_count + 1 : prev.review_count,
            escalated_count: newTx.status === 'ESCALATE' ? prev.escalated_count + 1 : prev.escalated_count,
          }));
        }
      } catch (err) {}
    };

    return () => ws.close();
  }, []);

  const handleSelectTx = (id: string) => {
    setSelectedTxId(id);
    fetch(`/api/v1/transactions/${id}`)
      .then((res) => res.json())
      .then((data) => setTxDetail(data))
      .catch(() => {});
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-white tracking-wide">Compliance Overview</h1>
        <p className="text-sm text-dark-muted mt-1">Real-time AI Multi-Agent Policy Auditing & Risk Monitoring</p>
      </div>

      {/* Metrics Cards & Analytics */}
      <MetricsOverview metrics={metrics} />

      {/* Live Feed Section */}
      <div className="space-y-4 pt-4">
        <h2 className="text-lg font-bold text-white">Recent Transactions Stream</h2>
        <TransactionFeed transactions={transactions} onSelectTransaction={handleSelectTx} />
      </div>

      {/* Detail Modal */}
      {selectedTxId && (
        <ViolationDetailModal detail={txDetail} onClose={() => setSelectedTxId(null)} />
      )}
    </div>
  );
}
