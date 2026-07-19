import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
});

export const maskFile = async (
  file: File,
  rules: Record<string, string>
): Promise<{ blob: Blob; filename: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('rules', JSON.stringify(rules));
  
  const response = await apiClient.post('/api/mask', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
  });
  
  // Extract filename from Content-Disposition header
  let filename = `${file.name.replace(/\.[^/.]+$/, '')}_masked.${file.name.split('.').pop()}`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.indexOf('attachment') !== -1) {
    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
    const matches = filenameRegex.exec(disposition);
    if (matches != null && matches[1]) { 
      filename = matches[1].replace(/['"]/g, '');
    }
  }
  
  return {
    blob: response.data,
    filename,
  };
};
