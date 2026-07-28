'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ShieldCheck, LayoutDashboard, Activity, FileCheck, BookOpen, ShieldAlert } from 'lucide-react';

export const Navigation: React.FC = () => {
  const pathname = usePathname();

  const navItems = [
    { label: 'Overview', href: '/', icon: LayoutDashboard },
    { label: 'Live Transactions', href: '/transactions', icon: Activity },
    { label: 'Audit Inspector', href: '/audit', icon: FileCheck },
    { label: 'Policy Explorer', href: '/policies', icon: BookOpen },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-dark-border flex flex-col h-screen fixed left-0 top-0 z-40">
      {/* Brand Header */}
      <div className="p-5 border-b border-dark-border flex items-center gap-3">
        <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white shadow-lg shadow-indigo-500/30">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-white tracking-wide">THEMIS</h1>
          <p className="text-xs text-brand-accent font-medium">Policy Audit Engine</p>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="p-4 space-y-1.5 flex-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 ${
                isActive
                  ? 'bg-brand-600/20 text-white border border-brand-500/40 shadow-inner'
                  : 'text-dark-muted hover:text-white hover:bg-dark-card/50'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-brand-accent' : 'text-dark-muted'}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Live System Status Card */}
      <div className="p-4 border-t border-dark-border">
        <div className="p-3.5 rounded-xl bg-dark-card/80 border border-dark-border/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-semibold text-gray-200">5 Agents Active</span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 font-mono">
            RAG Live
          </span>
        </div>
      </div>
    </aside>
  );
};
