'use client';

import React, { useState, useEffect } from 'react';
import { PolicyExplorer } from '@/components/PolicyExplorer';
import { Policy } from '@/types';

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);

  useEffect(() => {
    fetch('/api/v1/policies')
      .then((res) => res.json())
      .then((data) => setPolicies(data))
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-black text-white tracking-wide">Policy Explorer</h1>
        <p className="text-sm text-dark-muted mt-1">Directory of active regulatory rules, KYC/AML governance, and sanctions policy bounds</p>
      </div>

      <PolicyExplorer policies={policies} />
    </div>
  );
}
