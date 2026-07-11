"use client";
import React, { useState, useRef } from "react";
import type { UploadResult } from "@/app/page";

interface FileUploaderProps {
  onUploadSuccess: (data: UploadResult) => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const ACCEPTED = [".pdf", ".png", ".jpg", ".jpeg", ".csv"];

export default function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const [isDragging, setIsDragging]     = useState(false);
  const [isUploading, setIsUploading]   = useState(false);
  const [uploadError, setUploadError]   = useState<string | null>(null);
  const [uploadedName, setUploadedName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setUploadError(null);
    setUploadedName(file.name);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_preference", "buffett"); // backend auto-selects; frontend overrides via autoSelectPersona

      const res = await fetch(`${API_BASE}/api/v1/extract/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data: UploadResult = await res.json();
      onUploadSuccess(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setUploadError(msg);
      setUploadedName(null);
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleUpload(f);
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleUpload(f);
    e.target.value = "";
  };

  return (
    <div className="glass-panel p-6 flex flex-col gap-5">

      {/* Title row */}
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-slate-200 tracking-tight flex items-center gap-2">
          <span className="w-1.5 h-4 rounded-full bg-teal-500 inline-block" />
          Secure Ingestion
        </h2>
        <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest">
          Zero-Trust
        </span>
      </div>

      {/* Drop zone */}
      <div
        onClick={() => !isUploading && fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={`
          relative cursor-pointer rounded-xl border-2 border-dashed transition-all duration-300 p-8
          flex flex-col items-center justify-center gap-3 text-center
          ${isDragging
            ? "animate-pulse-border bg-teal-500/[0.06] border-teal-500/50"
            : "border-slate-700/60 hover:border-slate-600 hover:bg-white/[0.02]"
          }
          ${isUploading ? "pointer-events-none" : ""}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept={ACCEPTED.join(",")}
          onChange={onFileSelect}
        />

        {isUploading ? (
          <>
            <div className="w-12 h-12 rounded-full border-2 border-slate-700 border-t-teal-500 animate-spin" />
            <div>
              <p className="text-sm font-semibold text-slate-300">Processing…</p>
              <p className="text-xs text-slate-500 mt-0.5 truncate max-w-[200px]">{uploadedName}</p>
            </div>
          </>
        ) : uploadedName && !uploadError ? (
          <>
            <div className="w-12 h-12 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-emerald-400">Ingested successfully</p>
              <p className="text-xs text-slate-500 mt-0.5 truncate max-w-[200px]">{uploadedName}</p>
            </div>
          </>
        ) : (
          <>
            <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700/50 flex items-center justify-center">
              <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-300">
                {isDragging ? "Drop to upload" : "Drag & drop your statement"}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">or click to browse</p>
            </div>
          </>
        )}
      </div>

      {/* Error banner */}
      {uploadError && (
        <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/25 rounded-xl px-4 py-3">
          <svg className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
          <div>
            <p className="text-xs font-semibold text-red-400">Upload failed</p>
            <p className="text-xs text-slate-400 mt-0.5">{uploadError}</p>
          </div>
          <button onClick={() => setUploadError(null)} className="ml-auto text-slate-600 hover:text-slate-400">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Accepted formats */}
      <div className="flex flex-wrap gap-2">
        {ACCEPTED.map(ext => (
          <span key={ext} className="text-[10px] font-mono font-semibold text-slate-600 bg-slate-800/60 border border-slate-700/40 px-2 py-0.5 rounded-md uppercase">
            {ext.replace(".", "")}
          </span>
        ))}
        <span className="text-[10px] text-slate-600 ml-auto self-center">Max 20 MB</span>
      </div>

    </div>
  );
}
