'use client';

import React from 'react';
import { ComplianceMetrics } from '@/types';
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, Clock, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

interface Props {
  metrics: ComplianceMetrics;
}

export const MetricsOverview: React.FC<Props> = ({ metrics }) => {
  const pieData = [
    { name: 'Approved', value: metrics.approved_count, color: '#10B981' },
    { name: 'Review', value: metrics.review_count, color: '#F59E0B' },
    { name: 'Escalated', value: metrics.escalated_count, color: '#EF4444' },
  ];

  const barData = Object.entries(metrics.violations_by_category || {}).map(([category, count]) => ({
    category,
    count
  }));

  return (
    <div className="space-y-6">
      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-panel glass-panel-hover border border-dark-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-muted">Total Processed</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-white mt-2 font-mono">{metrics.total_processed}</p>
          <span className="text-xs text-brand-accent mt-1 inline-block font-medium">Real-time Multi-Agent Ingestion</span>
        </div>

        <div className="p-5 rounded-2xl glass-panel glass-panel-hover border border-dark-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-muted">Auto Approved</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">{metrics.approved_count}</p>
          <span className="text-xs text-emerald-500/80 mt-1 inline-block font-medium">
            {metrics.total_processed > 0 ? ((metrics.approved_count / metrics.total_processed) * 100).toFixed(1) : 0}% Pass Rate
          </span>
        </div>

        <div className="p-5 rounded-2xl glass-panel glass-panel-hover border border-dark-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-muted">Escalated</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-rose-400 mt-2 font-mono">{metrics.escalated_count}</p>
          <span className="text-xs text-rose-400/80 mt-1 inline-block font-medium">High Risk & Sanctions Triggered</span>
        </div>

        <div className="p-5 rounded-2xl glass-panel glass-panel-hover border border-dark-border">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-dark-muted">Avg Processing Time</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <p className="text-3xl font-extrabold text-cyan-400 mt-2 font-mono">{metrics.avg_processing_time_ms} ms</p>
          <span className="text-xs text-cyan-300/80 mt-1 inline-block font-medium">5 Agents & RAG Vector Match</span>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart: Status Distribution */}
        <div className="p-6 rounded-2xl glass-panel border border-dark-border">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-brand-accent" />
            Compliance Status Distribution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.75rem', color: '#FFF' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-2 text-xs font-semibold">
            {pieData.map((d) => (
              <div key={d.name} className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }}></span>
                <span className="text-gray-300">{d.name} ({d.value})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar Chart: Violations by Category */}
        <div className="p-6 rounded-2xl glass-panel border border-dark-border">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Rule Violations by Regulatory Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <XAxis dataKey="category" stroke="#9CA3AF" fontSize={12} />
                <YAxis stroke="#9CA3AF" fontSize={12} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', borderRadius: '0.75rem', color: '#FFF' }}
                />
                <Bar dataKey="count" fill="#6366F1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
