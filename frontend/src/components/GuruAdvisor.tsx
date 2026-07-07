import React from 'react';

export default function GuruAdvisor() {
  return (
    <div className="glass-panel p-6 border-l-4 border-l-indigo-500 transition-all hover:-translate-y-1 hover:shadow-indigo-500/10">
      <div className="flex items-center mb-5">
        <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
        </div>
        <div className="ml-4">
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">AI Advisory Report</h2>
          <div className="flex items-center mt-1">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-2"></div>
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">LangGraph Synced</p>
          </div>
        </div>
      </div>
      
      <div className="bg-slate-900/40 rounded-xl p-5 text-sm text-slate-300 leading-relaxed border border-white/5 backdrop-blur-sm shadow-inner">
        <p className="mb-3"><span className="text-emerald-400 font-semibold">Observation:</span> We detected a 15% increase in cloud infrastructure spend month-over-month. This correlates with the staging deployment spike on the 14th.</p>
        <p><span className="text-amber-400 font-semibold">Recommendation:</span> Consider migrating idle staging databases to serverless instances. <span className="text-slate-400 italic">The automated critique node verified this against historical burn rates.</span></p>
      </div>
    </div>
  );
}
