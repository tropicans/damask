import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
});

export interface PreviewResponse {
  filename: string;
  size_bytes: number;
  headers: string[];
  preview_rows: string[][];
  recommendations: Record<string, string>;
}

export const uploadFileForPreview = async (file: File): Promise<PreviewResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post<PreviewResponse>('/api/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};
