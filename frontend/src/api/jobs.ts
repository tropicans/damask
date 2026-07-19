import { apiClient } from './client';

export interface MaskingJobResponse {
  id: string;
  user_id: string;
  file_name: string;
  file_size_bytes: number;
  row_count: number | null;
  status: string; // "SUCCESS" or "FAILED"
  error_message: string | null;
  created_at: string;
}

export interface JobDetailResponse {
  id: string;
  job_id: string;
  column_name: string;
  rule_name: string;
}

export interface JobStatsResponse {
  total_files: number;
  total_rows: number;
  success_rate: number;
}

export const getJobs = async (skip = 0, limit = 10): Promise<MaskingJobResponse[]> => {
  const response = await apiClient.get<MaskingJobResponse[]>('/api/jobs', {
    params: { skip, limit }
  });
  return response.data;
};

export const getJobStats = async (): Promise<JobStatsResponse> => {
  const response = await apiClient.get<JobStatsResponse>('/api/jobs/stats');
  return response.data;
};

export const getJobDetails = async (jobId: string): Promise<JobDetailResponse[]> => {
  const response = await apiClient.get<JobDetailResponse[]>(`/api/jobs/${jobId}/details`);
  return response.data;
};
