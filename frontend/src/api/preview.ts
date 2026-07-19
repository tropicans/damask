import { apiClient } from './client';

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
