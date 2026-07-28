'use client';

import React from 'react';
import { AgentLog } from '@/types';
import { CheckCircle2, Cpu, FileJson, Clock, ArrowRight } from 'lucide-react';

interface Props {
  logs: AgentLog[];
  transactionId: string;
}

export const AuditTrailViewer: React.FC<Props> = ({ logs, transactionId }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between p-4 rounded-2xl glass-panel border border-dark-border">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileJson className="w-5 h-5 text-brand-accent" />
            Compliance Lineage & Audit Trail
          </h2>
          <p className="text-xs text-dark-muted font-mono mt-0.5">Transaction: {transactionId}</p>
        </div>
        <button
          onClick={() => {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(logs, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `AUDIT_${transactionId}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
          }}
          className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold transition-all shadow-lg shadow-brand-600/30 flex items-center gap-2"
        >
          Export Regulator Audit (JSON)
        </button>
      </div>

      {/* Agent Execution Timeline */}
      <div className="relative border-l-2 border-brand-500/40 ml-4 space-y-8 pl-6">
        {logs.map((log, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline Node Icon */}
            <span className="absolute -left-[35px] top-0 p-1.5 rounded-full bg-dark-bg border-2 border-brand-500 text-brand-accent shadow-md">
              <Cpu className="w-4 h-4" />
            </span>

            <div className="p-5 rounded-2xl glass-panel glass-panel-hover border border-dark-border space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-mono font-bold text-brand-accent">{log.agent_id}</span>
                  <h4 className="text-base font-bold text-white">{log.agent_name}</h4>
                </div>
                <span className="text-xs text-dark-muted font-mono flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : ''}
                </span>
              </div>

              {/* JSON Payload Summary */}
              <div className="p-3 rounded-xl bg-dark-bg/80 border border-dark-border/80 font-mono text-xs text-emerald-400 overflow-x-auto">
                <pre>{JSON.stringify(log.output, null, 2)}</pre>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
