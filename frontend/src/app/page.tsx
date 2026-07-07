"use client";
import React, { useState } from 'react';
import FileUploader from '@/components/FileUploader';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import GuruAdvisor from '@/components/GuruAdvisor';

export default function Home() {
  const [persona, setPersona] = useState("buffett");

  return (
    <main className="min-h-screen bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(99,102,241,0.15),rgba(255,255,255,0))] selection:bg-indigo-500/30">
      <div className="max-w-6xl mx-auto px-6 py-12 md:py-20">
        
        {/* Header */}
        <header className="mb-16 text-center md:text-left flex flex-col md:flex-row md:items-end justify-between">
          <div>
            <h1 className="text-5xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-emerald-400 tracking-tight pb-2">
              Equil
            </h1>
            <p className="text-slate-400 mt-2 text-lg md:text-xl font-medium tracking-wide">
              The Zero-Trust Financial Intelligence Wizard.
            </p>
          </div>
          <div className="mt-6 md:mt-0 flex flex-col items-center md:items-end space-y-4">
            <div className="flex items-center space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] animate-pulse"></div>
              <span className="text-sm font-semibold text-slate-300 uppercase tracking-widest">System Secure</span>
            </div>
            
            {/* Persona Dropdown */}
            <div className="glass-panel px-4 py-2 flex items-center space-x-3 transition-colors hover:border-indigo-500/30">
              <label htmlFor="persona-select" className="text-xs text-indigo-300 font-semibold uppercase tracking-wider">Advisory Persona</label>
              <select 
                id="persona-select"
                value={persona}
                onChange={(e) => setPersona(e.target.value)}
                className="bg-transparent text-slate-100 text-sm font-medium focus:outline-none cursor-pointer"
              >
                <option className="bg-slate-900" value="buffett">Warren Buffett (Value)</option>
                <option className="bg-slate-900" value="fire">F.I.R.E. (Aggressive Savings)</option>
                <option className="bg-slate-900" value="kiyosaki">Robert Kiyosaki (Cashflow)</option>
              </select>
            </div>
          </div>
        </header>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <div className="lg:col-span-1 flex flex-col space-y-8">
            <div className="flex-1">
              <FileUploader persona={persona} />
            </div>
            <div className="flex-1">
              <GuruAdvisor />
            </div>
          </div>

          <div className="lg:col-span-2">
            <AnalyticsDashboard />
          </div>
          
        </div>
      </div>
    </main>
  );
}
