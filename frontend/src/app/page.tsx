"use client";
import React, { useState } from 'react';
import FileUploader from '../components/FileUploader';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import GuruAdvisor from '../components/GuruAdvisor';
import { BackendResponse } from '../types/api';

type ViewState = 'upload' | 'analytics' | 'advisory';

export default function Dashboard() {
    const [view, setView] = useState<ViewState>('upload');
    const [backendData, setBackendData] = useState<BackendResponse | null>(null);
    const [globalError, setGlobalError] = useState<string | null>(null);

    const handleUploadSuccess = (data: BackendResponse) => {
        if (!data.analytics_bundle) {
            setGlobalError("The backend failed to return a valid analytics bundle.");
            return;
        }
        setGlobalError(null);
        setBackendData(data);
        setView('analytics');
    };

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 font-sans selection:bg-blue-500/30">
            {/* Top Navigation Bar */}
            <nav className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded bg-gradient-to-br from-blue-500 to-teal-400 flex items-center justify-center">
                            <span className="text-white font-bold">E</span>
                        </div>
                        <h1 className="text-xl font-bold tracking-wide">
                            Equil <span className="text-gray-500 font-normal">| The Finance Wizard</span>
                        </h1>
                    </div>
                    <div className="text-sm font-medium text-gray-400 border border-gray-700 rounded-full px-3 py-1 bg-gray-800/50">
                        Zero-Trust Sandbox Active
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
                {/* View Toggles */}
                <div className="flex flex-wrap items-center justify-center gap-2 mb-10 bg-gray-900 p-1.5 rounded-xl border border-gray-800 max-w-fit mx-auto">
                    <button 
                        onClick={() => setView('upload')} 
                        className={`px-6 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${view === 'upload' ? 'bg-gray-800 text-white shadow-sm ring-1 ring-gray-700' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'}`}
                    >
                        1. Ingestion
                    </button>
                    <button 
                        onClick={() => setView('analytics')} 
                        disabled={!backendData}
                        className={`px-6 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${view === 'analytics' ? 'bg-gray-800 text-white shadow-sm ring-1 ring-gray-700' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'} disabled:opacity-40 disabled:cursor-not-allowed`}
                    >
                        2. Analytics Suite
                    </button>
                    <button 
                        onClick={() => setView('advisory')} 
                        disabled={!backendData}
                        className={`px-6 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${view === 'advisory' ? 'bg-gray-800 text-white shadow-sm ring-1 ring-gray-700' : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'} disabled:opacity-40 disabled:cursor-not-allowed`}
                    >
                        3. Guru Advisory
                    </button>
                </div>

                {/* Dashboard Content Area */}
                <div className="transition-all duration-500 ease-in-out">
                    {globalError && (
                        <div className="max-w-2xl mx-auto mb-6 p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200">
                            {globalError}
                        </div>
                    )}
                    
                    <div className={view === 'upload' ? 'block max-w-2xl mx-auto mt-12 animate-in fade-in slide-in-from-bottom-4' : 'hidden'}>
                        <div className="mb-8 text-center">
                            <h2 className="text-3xl font-bold mb-3">Upload Financial Data</h2>
                            <p className="text-gray-400">Our Zero-Trust architecture processes your data strictly in-memory.</p>
                        </div>
                        <FileUploader onUploadSuccess={handleUploadSuccess} />
                    </div>

                    <div className={view === 'analytics' && backendData ? 'block animate-in fade-in slide-in-from-bottom-4' : 'hidden'}>
                        {backendData && <AnalyticsDashboard analyticsBundle={backendData.analytics_bundle} />}
                    </div>

                    <div className={view === 'advisory' && backendData ? 'block animate-in fade-in slide-in-from-bottom-4 max-w-4xl mx-auto' : 'hidden'}>
                        {backendData && <GuruAdvisor recommendation={backendData.multi_guru_advice || backendData.message} />}
                    </div>
                </div>
            </main>
        </div>
    );
}
