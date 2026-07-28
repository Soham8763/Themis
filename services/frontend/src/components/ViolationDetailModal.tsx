'use client';

import React from 'react';
import { TransactionDetail, DecisionStatus } from '@/types';
import { X, ShieldAlert, CheckCircle2, AlertTriangle, Cpu, FileText, User, Globe, DollarSign, ExternalLink } from 'lucide-react';

interface Props {
  detail: TransactionDetail | null;
  onClose: () => void;
}

export const ViolationDetailModal: React.FC<Props> = ({ detail, onClose }) => {
  if (!detail) return null;

  const { transaction: tx, decision, audit_logs } = detail;

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return <span className="px-2.5 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 text-xs font-bold font-mono">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 text-xs font-bold font-mono">HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 text-xs font-bold font-mono">MEDIUM</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 text-xs font-bold font-mono">LOW</span>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-dark-surface border border-dark-border rounded-3xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Modal Header */}
        <div className="p-6 border-b border-dark-border flex items-center justify-between bg-dark-card/50">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-brand-600/20 text-brand-accent border border-brand-500/30">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-extrabold text-white font-mono">{tx.transaction_id}</h2>
                <span className={`px-3 py-0.5 rounded-full text-xs font-bold ${
                  decision.status === 'APPROVED' ? 'badge-approved' : decision.status === 'REVIEW' ? 'badge-review' : 'badge-escalate'
                }`}>
                  {decision.status}
                </span>
              </div>
              <p className="text-xs text-dark-muted mt-0.5">Automated AI Policy Compliance Audit Report</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-dark-muted hover:text-white hover:bg-dark-card transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Transaction Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-dark-bg/60 border border-dark-border text-sm">
            <div>
              <span className="text-xs text-dark-muted block">Customer</span>
              <span className="font-semibold text-white">{tx.customer_name}</span>
            </div>
            <div>
              <span className="text-xs text-dark-muted block">Amount</span>
              <span className="font-mono font-bold text-emerald-400">${tx.amount.toLocaleString()} USD</span>
            </div>
            <div>
              <span className="text-xs text-dark-muted block">Destination Country</span>
              <span className="font-semibold text-white">{tx.destination_country}</span>
            </div>
            <div>
              <span className="text-xs text-dark-muted block">PEP Status</span>
              <span className={`font-semibold ${tx.pep_flag ? 'text-rose-400' : 'text-emerald-400'}`}>
                {tx.pep_flag ? 'YES (Flagged)' : 'NO'}
              </span>
            </div>
          </div>

          {/* AI Decision Reasoning Section */}
          <div className="p-5 rounded-2xl bg-gradient-to-r from-brand-600/10 to-cyan-500/10 border border-brand-500/30">
            <h3 className="text-sm font-bold text-brand-accent uppercase tracking-wider mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4" />
              Claude / Gemini Multi-Agent Reasoning
            </h3>
            <p className="text-sm text-gray-200 whitespace-pre-line leading-relaxed font-sans">
              {decision.reasoning}
            </p>
          </div>

          {/* Policy Violations List */}
          {decision.violations && decision.violations.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                Detected Policy Violations ({decision.violations.length})
              </h3>
              <div className="space-y-3">
                {decision.violations.map((v, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-dark-card/60 border border-dark-border space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white font-mono text-sm">{v.rule_id}</span>
                        <span className="text-xs font-semibold text-gray-300">{v.rule_name}</span>
                      </div>
                      {getSeverityBadge(v.severity)}
                    </div>
                    <p className="text-xs text-gray-300">{v.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
