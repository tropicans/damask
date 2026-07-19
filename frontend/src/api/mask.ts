import { apiClient } from './client';

/**
 * Uploads a file with masking configurations to the backend to mask in-memory.
 * Reads the 'Content-Disposition' header from the streaming response to extract the output filename.
 * @param file - Raw CSV or Excel file to mask.
 * @param rules - Column name to masking rule name mapping.
 * @returns A promise resolving to an object containing the download blob and filename.
 */
export const maskFile = async (
  file: File,
  rules: Record<string, string>,
  generateKey: boolean = false
): Promise<{ blob: Blob; filename: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('rules', JSON.stringify(rules));
  formData.append('generate_key', generateKey ? 'true' : 'false');
  
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

/**
 * Uploads a masked file along with its reversion key JSON file to restore original values.
 * @param file - The masked CSV or Excel file.
 * @param key - The JSON reversion key file.
 * @returns A promise resolving to the restored file blob and filename.
 */
export const revertFile = async (
  file: File,
  key: File
): Promise<{ blob: Blob; filename: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('key', key);

  const response = await apiClient.post('/api/mask/revert', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    responseType: 'blob',
  });

  let filename = `${file.name.replace(/\.[^/.]+$/, '')}_reverted.${file.name.split('.').pop()}`;
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
