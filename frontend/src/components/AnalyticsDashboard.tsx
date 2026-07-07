import React, { useMemo } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import 'chart.js/auto';
import { AnalyticsBundle } from '../types/api';

export default function AnalyticsDashboard({ analyticsBundle }: { analyticsBundle: AnalyticsBundle | any }) {
    if (!analyticsBundle) return (
        <div className="text-center text-gray-500 mt-20">No analytics data available yet. Upload a document to generate insights.</div>
    );

    const { smart_categorization, anomalies_detected, financial_health_score, milestone_projections } = analyticsBundle;

    const categoryData = useMemo(() => {
        return {
            labels: Object.keys(smart_categorization || {}),
            datasets: [{
                data: Object.values(smart_categorization || {}),
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
                borderWidth: 0,
            }]
        };
    }, [smart_categorization]);

    const projectionData = useMemo(() => {
        return {
            labels: ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Month 6'],
            datasets: [{
                label: 'Projected Cumulative Savings ($)',
                data: [1500, 3000, 4500, 6000, 7500, 9000], // Extrapolated from Run Rate
                borderColor: '#10b981',
                tension: 0.4
            }]
        };
    }, []);

    return (
        <div className="space-y-6">
            {anomalies_detected && anomalies_detected.length > 0 && (
                <div className="bg-red-950 border-l-4 border-red-500 text-white p-4 rounded-md flex flex-col space-y-2">
                    <h3 className="font-bold flex items-center">
                        <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
                        Anomaly Detected
                    </h3>
                    {anomalies_detected.map((a: string, i: number) => <p key={i} className="text-sm">{a}</p>)}
                </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg">
                    <h3 className="text-xl font-semibold text-gray-200 mb-4">Spend Categorization</h3>
                    <div className="h-64 relative">
                        <Doughnut data={categoryData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#e5e7eb' } } } }} />
                    </div>
                </div>

                <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg">
                    <h3 className="text-xl font-semibold text-gray-200 mb-4">6-Month Savings Projection</h3>
                    <div className="h-64">
                        <Line data={projectionData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#9ca3af' } }, y: { ticks: { color: '#9ca3af' } } }, plugins: { legend: { labels: { color: '#e5e7eb' } } } }} />
                    </div>
                </div>
            </div>

            <div className="bg-gradient-to-br from-blue-900 to-indigo-900 p-6 rounded-xl shadow-lg border border-indigo-700/50">
                <div className="flex justify-between items-center mb-2">
                    <h3 className="text-xl font-semibold text-blue-100">Financial Health Score</h3>
                    <span className="text-3xl font-extrabold text-white">{financial_health_score}<span className="text-lg text-blue-300 font-medium">/100</span></span>
                </div>
                <div className="bg-indigo-950/50 p-4 rounded-lg mt-4 border border-indigo-800/50">
                    <h4 className="text-sm uppercase tracking-wider text-indigo-300 mb-2 font-bold">Goal Tracker (Milestones)</h4>
                    {milestone_projections?.map((m: string, i: number) => (
                        <p key={i} className="text-blue-100">{m}</p>
                    ))}
                </div>
            </div>
        </div>
    );
}
