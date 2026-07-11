"use client";
import React, { useState } from "react";
import MultiSourceUploader from "@/components/MultiSourceUploader";
import AnalyticsDashboard from "@/components/AnalyticsDashboard";
import GuruAdvisor from "@/components/GuruAdvisor";
import GoalTracker from "@/components/GoalTracker";
import { PERSONA_META, autoSelectPersona } from "@/types";
import type { Persona, UploadResult } from "@/types";

import BudgetManager from "@/components/BudgetManager";

type ActiveTab = "analytics" | "advisory" | "goals" | "budgets";

export type { Persona, UploadResult };

export default function Home() {
  const [result, setResult]       = useState<UploadResult | null>(null);
  const [persona, setPersona]     = useState<Persona>("buffett");
  const [activeTab, setActiveTab] = useState<ActiveTab>("analytics");

  const handleUploadSuccess = (data: UploadResult) => {
    const chosen = autoSelectPersona(data);
    setPersona(chosen);
    setResult(data);
    setActiveTab("analytics");
  };

  const ALL_PERSONAS = Object.keys(PERSONA_META) as Persona[];

  const TABS: { key: ActiveTab; label: string }[] = [
    { key: "analytics", label: "📊 Analytics" },
    { key: "advisory",  label: "🧠 Advisory"  },
    { key: "budgets",   label: "💸 Budgets"   },
    { key: "goals",     label: "🎯 Goals"      },
  ];

  return (
    <main className="min-h-screen bg-slate-950 selection:bg-teal-500/25 overflow-x-hidden">

      {/* Ambient glows */}
      <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden>
        <div className="animate-float absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-teal-500/[0.06] blur-3xl" />
        <div className="animate-float absolute top-1/2 -right-60 w-[420px] h-[420px] rounded-full bg-emerald-500/[0.05] blur-3xl" style={{ animationDelay: "3s" }} />
        <div className="animate-float absolute bottom-0 left-1/3 w-[360px] h-[360px] rounded-full bg-cyan-500/[0.04] blur-3xl" style={{ animationDelay: "5s" }} />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">

        {/* Header */}
        <header className="mb-10 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/20 flex-shrink-0">
              <span className="text-white font-black text-lg leading-none">E</span>
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-white tracking-tight leading-none">
                Equil
                <span className="ml-2 text-slate-500 font-normal text-base">/ Finance Wizard</span>
              </h1>
              <p className="text-xs text-slate-500 mt-0.5 font-medium tracking-wide">
                Zero-Trust AI Financial Intelligence · Track B
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {result?.analytics?.currency === "INR" && (
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/25 px-3 py-1.5 rounded-full">
                🇮🇳 INR Mode
              </span>
            )}
            <span className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 bg-slate-800/60 border border-slate-700/50 px-3 py-1.5 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Sandbox Active
            </span>
          </div>
        </header>

        {/* Main grid */}
        <div className="grid grid-cols-1 xl:grid-cols-[380px_1fr] gap-6">

          {/* Left — uploader + persona badge */}
          <div className="flex flex-col gap-5">
            <MultiSourceUploader sessionId={result?.session_id} onUploadSuccess={handleUploadSuccess} />

            {/* Persona badge */}
            {result && (
              <div className="fade-up glass-panel p-5 flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700/50 flex items-center justify-center text-2xl flex-shrink-0">
                  {PERSONA_META[persona].icon}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold mb-0.5">
                    Auto-Selected Advisor
                  </p>
                  <p className={`text-base font-bold ${PERSONA_META[persona].color} leading-tight`}>
                    {PERSONA_META[persona].label}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5 leading-snug">
                    {PERSONA_META[persona].description}
                  </p>
                </div>
                <button
                  onClick={() => {
                    const next = ALL_PERSONAS[(ALL_PERSONAS.indexOf(persona) + 1) % ALL_PERSONAS.length];
                    setPersona(next);
                  }}
                  className="ml-auto flex-shrink-0 text-[10px] text-slate-500 hover:text-slate-300 border border-slate-700 hover:border-slate-500 px-2.5 py-1 rounded-lg transition-colors"
                  title="Cycle to next guru"
                >
                  Switch
                </button>
              </div>
            )}

            {/* All 5 guru chips */}
            {result && (
              <div className="fade-up flex flex-wrap gap-2 px-1">
                {ALL_PERSONAS.map(p => (
                  <button
                    key={p}
                    onClick={() => setPersona(p)}
                    className={`flex items-center gap-1.5 text-[10px] font-semibold px-2.5 py-1 rounded-full border transition-all ${
                      persona === p
                        ? `${PERSONA_META[p].badge} border-opacity-50`
                        : "text-slate-600 border-slate-800 hover:text-slate-400"
                    }`}
                  >
                    <span>{PERSONA_META[p].icon}</span>
                    <span>{PERSONA_META[p].label.split(" ")[0]}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Session chip */}
            {result?.session_id && (
              <div className="fade-up flex items-center gap-2 text-[10px] text-slate-600 font-mono px-3">
                <span className="text-slate-700">SESSION</span>
                <span className="text-slate-500 truncate">{result.session_id}</span>
              </div>
            )}
          </div>

          {/* Right — tabs */}
          <div className="flex flex-col gap-5">

            {!result ? (
              /* Empty state */
              <div className="glass-panel p-12 flex flex-col items-center justify-center text-center min-h-[480px] fade-up">
                <div className="w-16 h-16 rounded-2xl bg-slate-800/80 border border-slate-700/50 flex items-center justify-center mb-5">
                  <svg className="w-7 h-7 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-slate-400 font-semibold text-base mb-1">No data yet</p>
                <p className="text-slate-600 text-sm max-w-xs">
                  Upload a bank statement, paste UPI SMS messages, or sync Splitwise to generate your report.
                </p>

                {/* 5 guru preview */}
                <div className="mt-8 grid grid-cols-5 gap-2 w-full max-w-sm">
                  {ALL_PERSONAS.map(p => (
                    <div key={p} className="rounded-xl bg-slate-800/50 border border-slate-700/40 p-2 text-center">
                      <div className="text-lg mb-0.5">{PERSONA_META[p].icon}</div>
                      <div className="text-[9px] text-slate-500 font-semibold leading-tight truncate">
                        {PERSONA_META[p].label.split(" ")[0]}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Also show goals tab is accessible before upload */}
                <button
                  onClick={() => setActiveTab("goals")}
                  className="mt-6 text-xs text-teal-400 hover:text-teal-300 flex items-center gap-1.5 transition-colors"
                >
                  🎯 Set financial goals before uploading
                </button>
              </div>
            ) : null}

            {/* Tab bar — always visible once result exists, or for goals */}
            {(result || activeTab === "goals") && (
              <>
                <div className="flex items-center gap-1 bg-slate-900/60 border border-slate-800/60 rounded-xl p-1 w-fit">
                  {TABS.map(tab => (
                    <button
                      key={tab.key}
                      onClick={() => setActiveTab(tab.key)}
                      disabled={!result && tab.key !== "goals"}
                      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                        activeTab === tab.key
                          ? "bg-slate-800 text-white shadow-sm"
                          : "text-slate-500 hover:text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed"
                      }`}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>

                <div className="fade-up">
                  {activeTab === "analytics" && result && (
                    <AnalyticsDashboard result={result} />
                  )}
                  {activeTab === "advisory" && result && (
                    <GuruAdvisor report={result.advisory_report} persona={persona} />
                  )}
                  {activeTab === "goals" && (
                    <GoalTracker
                      sessionId={result?.session_id ?? "pre-session"}
                      currency={result?.analytics?.currency ?? "USD"}
                      income={
                        Object.values(result?.analytics?.categories ?? {})
                          .filter(v => v > 0)
                          .reduce((a, b) => a + b, 0)
                      }
                    />
                  )}
                  {activeTab === "budgets" && (
                    <div className="fade-up">
                      <BudgetManager data={result} />
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-14 pt-6 border-t border-slate-800/50 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-700">
          <span>Equil Financial Intelligence · Zero-Trust Architecture · Track B</span>
          <span>Strictly educational guidance · Not certified financial advice</span>
        </footer>
      </div>
    </main>
  );
}
