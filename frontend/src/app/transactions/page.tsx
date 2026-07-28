'use client';

import React, { useState, useEffect } from 'react';
import { TransactionFeed } from '@/components/TransactionFeed';
import { ViolationDetailModal } from '@/components/ViolationDetailModal';
import { TransactionItem, TransactionDetail } from '@/types';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [selectedTxId, setSelectedTxId] = useState<string | null>(null);
  const [txDetail, setTxDetail] = useState<TransactionDetail | null>(null);

  useEffect(() => {
    fetch('/api/v1/transactions')
      .then((res) => res.json())
      .then((data) => setTransactions(data))
      .catch(() => {});
  }, []);

  const handleSelectTx = (id: string) => {
    setSelectedTxId(id);
    fetch(`/api/v1/transactions/${id}`)
      .then((res) => res.json())
      .then((data) => setTxDetail(data))
      .catch(() => {});
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-white tracking-wide">Live Transactions Feed</h1>
        <p className="text-sm text-dark-muted mt-1">Real-time incoming transaction processing and risk status tracking</p>
      </div>

      <TransactionFeed transactions={transactions} onSelectTransaction={handleSelectTx} />

      {selectedTxId && (
        <ViolationDetailModal detail={txDetail} onClose={() => setSelectedTxId(null)} />
      )}
    </div>
  );
}
