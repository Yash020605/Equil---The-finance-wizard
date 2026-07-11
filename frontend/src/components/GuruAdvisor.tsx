import React from "react";
import { PERSONA_META } from "@/types";
import type { Persona } from "@/types";

interface Props {
  report:  string;
  persona: Persona;
}

export default function GuruAdvisor({ report, persona }: Props) {
  const meta = PERSONA_META[persona];

  if (!report) {
    return (
      <div className="glass-panel p-10 flex flex-col items-center justify-center text-center min-h-[300px]">
        <div className="text-3xl mb-3">{meta.icon}</div>
        <p className="text-slate-400 font-semibold">No report generated yet.</p>
        <p className="text-slate-600 text-sm mt-1">Upload a document to generate your advisory report.</p>
      </div>
    );
  }

  const paragraphs = report.split(/\n+/).filter(Boolean);

  return (
    <div className={`glass-panel p-6 border-l-4 ${meta.border} flex flex-col gap-6`}>

      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700/50 flex items-center justify-center text-2xl flex-shrink-0">
          {meta.icon}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h2 className={`text-base font-extrabold ${meta.color} leading-tight`}>{meta.label}</h2>
            <span className={`text-[10px] font-semibold border px-2 py-0.5 rounded-full uppercase tracking-wide ${meta.badge}`}>
              Auto-selected
            </span>
          </div>
          <p className="text-xs text-slate-500">{meta.description}</p>
        </div>
        <div className="flex-shrink-0 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] text-slate-600 font-semibold uppercase tracking-wider">Verified</span>
        </div>
      </div>

      {/* Report body */}
      <div className="bg-slate-900/50 rounded-xl border border-white/[0.05] p-5 flex flex-col gap-3 max-h-[60vh] overflow-y-auto">
        {paragraphs.map((para, i) => {
          const isHeading = /^(#{1,3})\s/.test(para) || /^\*\*[^*]+\*\*$/.test(para);
          const isTableRow = para.startsWith("|");
          const cleaned = para.replace(/^#{1,3}\s/, "").replace(/\*\*/g, "");

          if (isHeading) {
            return (
              <p key={i} className={`text-sm font-bold ${meta.color} tracking-tight mt-2 first:mt-0`}>
                {cleaned}
              </p>
            );
          }

          if (isTableRow) {
            return (
              <p key={i} className="text-xs text-slate-400 font-mono leading-relaxed border-b border-slate-800/50 pb-1">
                {cleaned}
              </p>
            );
          }

          const hasObservation    = /\bobserv|\bdetect|\bnotice|\bflag/i.test(para);
          const hasRecommendation = /\brecomm|\bsugg|\bconsider|\bshould|\bcould|\badvise/i.test(para);

          return (
            <p key={i} className="text-sm text-slate-300 leading-relaxed">
              {hasObservation && !hasRecommendation && (
                <span className="text-emerald-400 font-semibold mr-1">Observation:</span>
              )}
              {hasRecommendation && !hasObservation && (
                <span className={`${meta.color} font-semibold mr-1`}>Recommendation:</span>
              )}
              {cleaned}
            </p>
          );
        })}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-[10px] text-slate-700 border-t border-white/[0.04] pt-4">
        <span className="flex items-center gap-1.5">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
          Passed Advisory Critique Node
        </span>
        <span>Strictly educational · Not certified financial advice</span>
      </div>
    </div>
  );
}
