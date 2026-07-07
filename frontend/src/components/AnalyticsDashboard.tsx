import React from 'react';

export default function AnalyticsDashboard() {
  return (
    <div className="glass-panel p-8 h-full flex flex-col">
      <h2 className="text-xl font-bold text-slate-100 mb-8 flex items-center tracking-tight">
        <svg className="w-5 h-5 mr-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        Transaction Topography
      </h2>
      
      <div className="space-y-6 flex-grow flex flex-col justify-center">
        {/* Mock progress bars for categorization */}
        <div className="group">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-300 font-medium">Software & Subscriptions</span>
            <span className="text-indigo-400 font-bold">$12,450 <span className="text-slate-500 font-normal ml-1">(45%)</span></span>
          </div>
          <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden shadow-inner">
            <div className="bg-gradient-to-r from-indigo-600 to-indigo-400 h-full rounded-full transition-all duration-1000 ease-out group-hover:opacity-80" style={{ width: '45%' }}></div>
          </div>
        </div>

        <div className="group">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-300 font-medium">Cloud Infrastructure</span>
            <span className="text-emerald-400 font-bold">$8,300 <span className="text-slate-500 font-normal ml-1">(30%)</span></span>
          </div>
          <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden shadow-inner">
            <div className="bg-gradient-to-r from-emerald-600 to-emerald-400 h-full rounded-full transition-all duration-1000 ease-out group-hover:opacity-80" style={{ width: '30%' }}></div>
          </div>
        </div>

        <div className="group">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-300 font-medium">Legal & Compliance</span>
            <span className="text-amber-400 font-bold">$6,916 <span className="text-slate-500 font-normal ml-1">(25%)</span></span>
          </div>
          <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden shadow-inner">
            <div className="bg-gradient-to-r from-amber-600 to-amber-400 h-full rounded-full transition-all duration-1000 ease-out group-hover:opacity-80" style={{ width: '25%' }}></div>
          </div>
        </div>
      </div>
    </div>
  );
}
