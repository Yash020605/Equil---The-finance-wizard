import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function GuruAdvisor({ recommendation }: { recommendation: string }) {
    if (!recommendation) return null;

    return (
        <div className="bg-gray-900 border border-gray-800 p-8 rounded-xl shadow-xl prose prose-invert max-w-none">
            <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-teal-400 mb-6 border-b border-gray-800 pb-4">
                Multi-Perspective Advisory Report
            </h2>
            <ReactMarkdown>{recommendation}</ReactMarkdown>
        </div>
    );
}
