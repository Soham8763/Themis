'use client';

import React, { useState } from 'react';
import { TransactionItem, DecisionStatus } from '@/types';
import { Search, Filter, AlertOctagon, AlertTriangle, CheckCircle, ArrowUpRight, Globe, UserCheck, Shield } from 'lucide-react';

interface Props {
  transactions: TransactionItem[];
  onSelectTransaction: (id: string) => void;
}

export const TransactionFeed: React.FC<Props> = ({ transactions, onSelectTransaction }) => {
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filtered = transactions.filter((tx) => {
    const matchesStatus = filterStatus === 'ALL' || tx.status === filterStatus;
    const matchesSearch =
      tx.transaction_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.customer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.destination_country.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusBadge = (status: DecisionStatus) => {
    switch (status) {
      case 'APPROVED':
        return (
          <span className="badge-approved px-3 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1.5 shadow-sm">
            <CheckCircle className="w-3.5 h-3.5" />
            APPROVED
          </span>
        );
      case 'REVIEW':
        return (
          <span className="badge-review px-3 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1.5 shadow-sm">
            <AlertTriangle className="w-3.5 h-3.5" />
            REVIEW
          </span>
        );
      case 'ESCALATE':
        return (
          <span className="badge-escalate px-3 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1.5 shadow-sm animate-pulse">
            <AlertOctagon className="w-3.5 h-3.5" />
            ESCALATE
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl glass-panel border border-dark-border">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-dark-muted absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search TX ID, customer, country..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-dark-bg border border-dark-border text-white text-sm rounded-xl pl-10 pr-4 py-2 focus:outline-none focus:border-brand-500 transition-colors"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 bg-dark-bg p-1 rounded-xl border border-dark-border">
          {['ALL', 'APPROVED', 'REVIEW', 'ESCALATE'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                filterStatus === st
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'text-dark-muted hover:text-white'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Transactions Table */}
      <div className="rounded-2xl glass-panel border border-dark-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-dark-card/60 text-xs uppercase font-semibold text-dark-muted border-b border-dark-border">
              <tr>
                <th className="px-6 py-4">Transaction ID</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Destination</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border/60">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-dark-muted font-medium">
                    No transactions match criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((tx) => (
                  <tr
                    key={tx.transaction_id}
                    onClick={() => onSelectTransaction(tx.transaction_id)}
                    className="hover:bg-dark-card/40 cursor-pointer transition-colors duration-150 group"
                  >
                    <td className="px-6 py-4 font-mono font-bold text-white group-hover:text-brand-accent">
                      {tx.transaction_id}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <span className="font-semibold text-white block">{tx.customer_name}</span>
                        <span className="text-xs text-dark-muted font-mono">{tx.customer_id}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono font-bold text-white">
                      ${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      <span className="text-xs text-dark-muted ml-1 font-normal">{tx.currency}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-gray-300">
                        <Globe className="w-4 h-4 text-dark-muted" />
                        <span>{tx.destination_country}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(tx.status)}</td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 rounded-lg bg-dark-border/40 text-gray-300 group-hover:bg-brand-600 group-hover:text-white transition-all">
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
