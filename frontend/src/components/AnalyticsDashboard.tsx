"use client";
import React, { useMemo } from "react";
import { formatCurrency } from "@/types";
import type { UploadResult } from "@/types";

interface Props { result: UploadResult; }

const CATEGORY_COLORS: Record<string, { bar: string; text: string }> = {
  Income:              { bar: "bg-emerald-500",  text: "text-emerald-400"  },
  Investment:          { bar: "bg-teal-500",     text: "text-teal-400"     },
  "Essential Living":  { bar: "bg-cyan-500",     text: "text-cyan-400"     },
  Food:                { bar: "bg-amber-500",    text: "text-amber-400"    },
  "Food & Dining":     { bar: "bg-amber-500",    text: "text-amber-400"    },
  Discretionary:       { bar: "bg-orange-500",   text: "text-orange-400"   },
  Transport:           { bar: "bg-sky-500",      text: "text-sky-400"      },
  Healthcare:          { bar: "bg-rose-500",     text: "text-rose-400"     },
  Subscriptions:       { bar: "bg-violet-500",   text: "text-violet-400"   },
  "Technology & Gaming":{ bar: "bg-fuchsia-500", text: "text-fuchsia-400"  },
  Technology:          { bar: "bg-blue-500",     text: "text-blue-400"     },
  Telecom:             { bar: "bg-indigo-500",   text: "text-indigo-400"   },
  Utilities:           { bar: "bg-lime-500",     text: "text-lime-400"     },
  Education:           { bar: "bg-yellow-500",   text: "text-yellow-400"   },
  EMI:                 { bar: "bg-red-500",      text: "text-red-400"      },
  Shopping:            { bar: "bg-pink-500",     text: "text-pink-400"     },
  Other:               { bar: "bg-slate-500",    text: "text-slate-400"    },
};

function colorFor(cat: string) { return (CATEGORY_COLORS[cat] ?? CATEGORY_COLORS.Other).bar; }
function textFor (cat: string) { return (CATEGORY_COLORS[cat] ?? CATEGORY_COLORS.Other).text; }

function healthLabel(score: number) {
  if (score >= 80) return { label: "Excellent", color: "text-emerald-400", bar: "bg-emerald-500" };
  if (score >= 65) return { label: "Good",      color: "text-teal-400",    bar: "bg-teal-500"    };
  if (score >= 45) return { label: "Fair",      color: "text-amber-400",   bar: "bg-amber-500"   };
  return               { label: "At Risk",   color: "text-red-400",     bar: "bg-red-500"     };
}

export default function AnalyticsDashboard({ result }: Props) {
  const cats        = result.analytics?.categories   ?? {};
  const score       = result.analytics?.health_score ?? 0;
  const anomalies   = result.analytics?.anomalies    ?? [];
  const projections = result.analytics?.projections  ?? [];
  const currency    = result.analytics?.currency     ?? "USD";
  const budgets     = result.analytics?.budget_status ?? [];

  const { label: hlabel, color: hcolor, bar: hbar } = healthLabel(score);

  const income = useMemo(
    () => Object.values(cats).filter(v => v > 0).reduce((a, b) => a + b, 0),
    [cats]
  );
  const totalSpend = useMemo(
    () => Object.entries(cats).filter(([k]) => k !== "Income").reduce((s, [, v]) => s + Math.abs(v), 0),
    [cats]
  );
  const sorted = useMemo(
    () => Object.entries(cats).sort(([, a], [, b]) => Math.abs(b) - Math.abs(a)),
    [cats]
  );

  // 6-month savings projection data points
  const savingsPerPeriod = income - totalSpend;
  const projectionPoints = useMemo(() =>
    Array.from({ length: 6 }, (_, i) => ({
      month: `M${i + 1}`,
      value: Math.max(0, savingsPerPeriod * (i + 1)),
    })), [savingsPerPeriod]);
  const maxProjection = Math.max(...projectionPoints.map(p => p.value), 1);

  return (
    <div className="flex flex-col gap-5">

      {/* ── Anomaly banner ── */}
      {anomalies.length > 0 && (
        <div className="glass-panel px-5 py-4 border-l-4 border-l-amber-500 flex items-start gap-3">
          <svg className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="text-xs font-bold text-amber-400 uppercase tracking-wide mb-1">Anomalies Detected</p>
            {anomalies.map((a, i) => <p key={i} className="text-sm text-slate-300">{a}</p>)}
          </div>
        </div>
      )}

      {/* ── Top KPI row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">

        {/* Health score */}
        <div className="glass-panel p-5 flex flex-col gap-2 col-span-2 sm:col-span-1">
          <p className="text-[10px] uppercase tracking-widest text-slate-600 font-bold">Health Score</p>
          <div className="flex items-end gap-2">
            <span className={`text-4xl font-extrabold leading-none ${hcolor}`}>{score}</span>
            <span className="text-slate-600 text-lg mb-0.5">/100</span>
          </div>
          <span className={`text-xs font-semibold ${hcolor}`}>{hlabel}</span>
          <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mt-1">
            <div className={`h-full rounded-full bar-animate ${hbar}`} style={{ width: `${score}%` }} />
          </div>
        </div>

        {/* Income */}
        <div className="glass-panel p-5 flex flex-col gap-1">
          <p className="text-[10px] uppercase tracking-widest text-slate-600 font-bold">Income</p>
          <p className="text-2xl font-extrabold text-emerald-400 leading-none">
            {formatCurrency(income, currency)}
          </p>
          <p className="text-xs text-slate-500 mt-1">This period</p>
        </div>

        {/* Total spend */}
        <div className="glass-panel p-5 flex flex-col gap-1">
          <p className="text-[10px] uppercase tracking-widest text-slate-600 font-bold">Total Spend</p>
          <p className="text-2xl font-extrabold text-white leading-none">
            {formatCurrency(totalSpend, currency)}
          </p>
          <p className="text-xs text-slate-500 mt-1">{sorted.length} categories</p>
        </div>
      </div>

      {/* ── Spend breakdown ── */}
      <div className="glass-panel p-6">
        <h3 className="text-sm font-bold text-slate-300 mb-5 flex items-center gap-2">
          <span className="w-1.5 h-4 rounded-full bg-teal-500 inline-block" />
          Spend Breakdown
        </h3>
        <div className="flex flex-col gap-4">
          {sorted.map(([cat, amount]) => {
            const pct      = totalSpend > 0 ? (Math.abs(amount) / totalSpend) * 100 : 0;
            const isIncome = cat === "Income";
            const budget   = budgets.find(b => b.category === cat);
            return (
              <div key={cat} className="group">
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="text-slate-300 font-medium">{cat}</span>
                  <div className="flex items-center gap-2">
                    <span className={`font-bold ${textFor(cat)}`}>
                      {isIncome ? "+" : "-"}{formatCurrency(Math.abs(amount), currency)}
                    </span>
                    {!isIncome && (
                      <span className="text-slate-600 text-xs w-9 text-right">{pct.toFixed(0)}%</span>
                    )}
                  </div>
                </div>
                {!isIncome && (
                  <div className="relative w-full h-2 bg-slate-800/80 rounded-full overflow-hidden">
                    <div
                      className={`absolute left-0 top-0 h-full rounded-full bar-animate opacity-80 group-hover:opacity-100 transition-opacity ${colorFor(cat)}`}
                      style={{ width: `${pct}%` }}
                    />
                    {/* Budget limit marker */}
                    {budget && (
                      <div
                        className="absolute top-0 h-full w-0.5 bg-white/30"
                        style={{ left: `${Math.min(100, (budget.allocated / totalSpend) * 100)}%` }}
                        title={`Budget: ${formatCurrency(budget.allocated, currency)}`}
                      />
                    )}
                  </div>
                )}
                {/* Budget status row */}
                {budget && !isIncome && (
                  <div className="flex items-center justify-between mt-1">
                    <span className={`text-[10px] font-semibold ${
                      budget.status === "over" ? "text-red-400" :
                      budget.status === "warning" ? "text-amber-400" : "text-slate-600"
                    }`}>
                      {budget.status === "over" ? "⚠ Over budget" :
                       budget.status === "warning" ? `${budget.pct_used.toFixed(0)}% of budget` :
                       `${budget.pct_used.toFixed(0)}% of budget`}
                    </span>
                    <span className="text-[10px] text-slate-600">
                      Limit: {formatCurrency(budget.allocated, currency)}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 6-Month Savings Projection chart (pure CSS bar chart) ── */}
      {savingsPerPeriod > 0 && (
        <div className="glass-panel p-6">
          <h3 className="text-sm font-bold text-slate-300 mb-5 flex items-center gap-2">
            <span className="w-1.5 h-4 rounded-full bg-emerald-500 inline-block" />
            6-Month Savings Projection
          </h3>
          <div className="flex items-end gap-2 h-28" aria-label="6-month savings projection chart">
            {projectionPoints.map((p, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-[9px] text-slate-600 font-mono">
                  {formatCurrency(p.value, currency).replace(/\.00$/, "")}
                </span>
                <div
                  className="w-full rounded-t-md bg-emerald-500/70 hover:bg-emerald-500 transition-all bar-animate"
                  style={{ height: `${(p.value / maxProjection) * 80}px` }}
                  title={`${p.month}: ${formatCurrency(p.value, currency)}`}
                />
                <span className="text-[9px] text-slate-600">{p.month}</span>
              </div>
            ))}
          </div>
          <p className="text-[10px] text-slate-600 mt-2">
            Based on {formatCurrency(savingsPerPeriod, currency)}/period savings rate
          </p>
        </div>
      )}

      {/* ── Goal projections ── */}
      {projections.length > 0 && (
        <div className="glass-panel p-6">
          <h3 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
            <span className="w-1.5 h-4 rounded-full bg-teal-500 inline-block" />
            Goal Projections
          </h3>
          <ul className="flex flex-col gap-2.5">
            {projections.map((p, i) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <span className="w-5 h-5 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                </span>
                <span className="text-slate-300 leading-snug">{p}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Indian tax note ── */}
      {currency === "INR" && (
        <div className="glass-panel px-5 py-4 border-l-4 border-l-emerald-500 flex items-start gap-3">
          <span className="text-lg flex-shrink-0">🇮🇳</span>
          <div>
            <p className="text-xs font-bold text-emerald-400 mb-1">Indian Financial Context Active</p>
            <p className="text-xs text-slate-400 leading-relaxed">
              Amounts in ₹ INR. Advisor switched to Indian CFP persona. Tax planning (80C/HRA/NPS) and SIP guidance included in advisory report.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
