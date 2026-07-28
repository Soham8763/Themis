'use client';

import React, { useState } from 'react';
import { Policy } from '@/types';
import { BookOpen, Search, Filter, ShieldCheck, ChevronRight } from 'lucide-react';

interface Props {
  policies: Policy[];
}

export const PolicyExplorer: React.FC<Props> = ({ policies }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const categories = ['ALL', 'KYC', 'AML', 'Limits', 'Sanctions', 'PEP'];

  const filtered = policies.filter((p) => {
    const matchesCat = selectedCategory === 'ALL' || p.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchesSearch =
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.policy_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Search & Category Header */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl glass-panel border border-dark-border">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-dark-muted absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search policies by keyword, ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-dark-bg border border-dark-border text-white text-sm rounded-xl pl-10 pr-4 py-2 focus:outline-none focus:border-brand-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-1 bg-dark-bg p-1 rounded-xl border border-dark-border overflow-x-auto max-w-full">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 whitespace-nowrap ${
                selectedCategory === cat
                  ? 'bg-brand-600 text-white shadow-md'
                  : 'text-dark-muted hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Policies List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filtered.map((p) => (
          <div key={p.policy_id} className="p-6 rounded-2xl glass-panel glass-panel-hover border border-dark-border flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-brand-accent px-2.5 py-1 rounded bg-brand-600/10 border border-brand-500/30">
                  {p.policy_id}
                </span>
                <span className="text-xs font-mono text-dark-muted">v{p.version}</span>
              </div>
              <h3 className="text-lg font-bold text-white leading-snug">{p.title}</h3>
              <p className="text-xs text-gray-300 leading-relaxed bg-dark-bg/60 p-3 rounded-xl border border-dark-border/60">
                {p.content}
              </p>
            </div>

            {/* Rules Summary */}
            {p.rules && p.rules.length > 0 && (
              <div className="border-t border-dark-border pt-3 space-y-2">
                <span className="text-xs font-semibold text-dark-muted uppercase">Active Rules ({p.rules.length})</span>
                <div className="space-y-1.5">
                  {p.rules.map((r: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-dark-card/60">
                      <span className="font-semibold text-gray-200">{r.rule_name}</span>
                      <span className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded ${
                        r.severity === 'CRITICAL' ? 'bg-purple-950 text-purple-300' :
                        r.severity === 'HIGH' ? 'bg-rose-950 text-rose-300' : 'bg-amber-950 text-amber-300'
                      }`}>
                        {r.severity}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
