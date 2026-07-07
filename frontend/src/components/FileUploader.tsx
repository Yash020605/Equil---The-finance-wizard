"use client";
import React, { useState, useRef } from 'react';

interface FileUploaderProps {
  persona: string;
}

export default function FileUploader({ persona }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    if (!file) return;
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Append the Persona Preference to the payload
      formData.append('user_preference', persona);

      const res = await fetch('http://localhost:8000/api/v1/extract/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      console.log('Upload response:', data);
      
      if (res.ok) {
        alert('File securely ingested. Graph Routed to Persona: ' + data.persona_routed);
      } else {
        alert(`Upload Failed: ${data.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Upload failed', error);
      alert('Network error connecting to Backend.');
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`glass-panel p-8 text-center transition-all duration-300 ${isDragging ? 'animate-pulse-border bg-white/10 scale-[1.02]' : 'hover:bg-white/10 hover:border-white/20'}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
    >
      <input 
        type="file" 
        className="hidden" 
        ref={fileInputRef} 
        onChange={onFileSelect}
        accept=".pdf,.png,.jpg,.jpeg,.csv" 
      />
      
      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="p-4 bg-indigo-500/20 rounded-full">
          {isUploading ? (
            <svg className="w-8 h-8 text-indigo-400 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          )}
        </div>
        <div>
          <h3 className="text-lg font-semibold text-slate-200 tracking-tight">
            {isUploading ? 'Ingesting securely...' : 'Secure Ingestion'}
          </h3>
          <p className="text-sm text-slate-400 mt-1">Routing via: <span className="text-indigo-300 font-semibold capitalize">{persona}</span></p>
          <p className="text-xs text-slate-500 mt-2">Supported: PDF, PNG, JPEG, CSV</p>
        </div>
        <button 
          disabled={isUploading}
          onClick={() => fileInputRef.current?.click()}
          className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg transition-all shadow-lg shadow-indigo-500/25 active:scale-95 disabled:opacity-50"
        >
          {isUploading ? 'Processing...' : 'Browse Files'}
        </button>
      </div>
    </div>
  );
}
