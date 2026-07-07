import { BackendResponse } from '../types/api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function uploadDocument(file: File, token: string = "test_token"): Promise<BackendResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/v1/extract/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData,
  });

  if (!response.ok) {
      if (response.status === 429) throw new Error("Rate limit exceeded. Please try again later.");
      if (response.status === 415) throw new Error("Unsupported file type. Please upload a valid image, CSV, or PDF.");
      if (response.status === 401) throw new Error("Unauthorized access. Invalid token.");
      
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed with status: ${response.status}`);
  }

  return response.json();
}
