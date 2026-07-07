import React, { useState } from 'react';
import { uploadDocument } from '../services/api';
import { BackendResponse } from '../types/api';

export default function FileUploader({ onUploadSuccess }: { onUploadSuccess: (data: BackendResponse) => void }) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleUpload(e.dataTransfer.files[0]);
        }
    };

    const handleUpload = async (file: File) => {
        setIsUploading(true);
        setError(null);
        try {
            const result = await uploadDocument(file);
            onUploadSuccess(result);
        } catch (err: any) {
            console.error("Upload failed", err);
            setError(err.message || "An unknown error occurred during upload.");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="flex flex-col gap-4">
            <div 
                className={`p-10 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${isDragging ? 'border-blue-500 bg-gray-800' : 'border-gray-600 hover:border-blue-400 bg-gray-900'}`}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                onClick={() => document.getElementById('fileUpload')?.click()}
            >
                <input 
                    type="file" 
                    id="fileUpload" 
                    className="hidden" 
                    onChange={(e) => e.target.files && handleUpload(e.target.files[0])} 
                />
                {isUploading ? (
                    <p className="text-blue-400 font-semibold animate-pulse">Uploading and running Zero-Trust Ingestion Engine...</p>
                ) : (
                    <p className="text-gray-300">Drag & Drop your financial statement (CSV/Image/PDF) here or click to browse.</p>
                )}
            </div>
            {error && (
                <div className="p-3 bg-red-900/50 border border-red-500 text-red-200 text-sm rounded">
                    {error}
                </div>
            )}
        </div>
    );
}
