import { apiClient } from './client';

export interface PreviewResponse {
  filename: string;
  size_bytes: number;
  headers: string[];
  preview_rows: string[][];
  recommendations: Record<string, string>;
}

/**
 * Uploads a file to the backend preview endpoint to extract headers,
 * sample rows, and rule recommendations.
 * @param file - Raw CSV or Excel file to preview.
 * @returns A promise resolving to the preview details payload.
 */
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
