import { useState, useEffect } from 'react';
import { 
  FileText, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Info, 
  Calendar, 
  Database, 
  Percent, 
  ChevronLeft, 
  ChevronRight, 
  X,
  ShieldAlert
} from 'lucide-react';
import { 
  getJobs, 
  getJobStats, 
  getJobDetails, 
  type MaskingJobResponse, 
  type JobStatsResponse, 
  type JobDetailResponse 
} from '../api/jobs';

export function AuditDashboard() {
  const [jobs, setJobs] = useState<MaskingJobResponse[]>([]);
  const [stats, setStats] = useState<JobStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Pagination
  const [page, setPage] = useState(0);
  const limit = 10;
  const [hasMore, setHasMore] = useState(false);

  // Modal State
  const [selectedJob, setSelectedJob] = useState<MaskingJobResponse | null>(null);
  const [jobDetails, setJobDetails] = useState<JobDetailResponse[]>([]);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [detailsError, setDetailsError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [jobsData, statsData] = await Promise.all([
        getJobs(page * limit, limit + 1), // fetch limit + 1 to check if there is a next page
        getJobStats()
      ]);

      if (jobsData.length > limit) {
        setHasMore(true);
        setJobs(jobsData.slice(0, limit));
      } else {
        setHasMore(false);
        setJobs(jobsData);
      }

      setStats(statsData);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Gagal memuat data riwayat audit.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [page]);

  const handleOpenDetails = async (job: MaskingJobResponse) => {
    setSelectedJob(job);
    setDetailsError(null);
    setJobDetails([]);

    if (job.status === 'SUCCESS') {
      setIsLoadingDetails(true);
      try {
        const details = await getJobDetails(job.id);
        setJobDetails(details);
      } catch (err: any) {
        console.error(err);
        setDetailsError(err.response?.data?.detail || 'Gagal memuat rincian penyamaran.');
      } finally {
        setIsLoadingDetails(false);
      }
    }
  };

  const handleCloseModal = () => {
    setSelectedJob(null);
    setJobDetails([]);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  if (isLoading && page === 0) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="animate-spin text-indigo-500 mx-auto mb-4" size={40} />
          <p className="text-sm text-slate-400 font-medium">Memuat Riwayat Audit...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto py-6">
      {error && (
        <div className="mb-6 p-4 bg-red-950/40 border border-red-900/60 rounded-xl flex items-start gap-3 text-red-400 text-sm">
          <ShieldAlert className="shrink-0 mt-0.5" size={18} />
          <div>
            <h4 className="font-semibold mb-1">Gagal memuat data</h4>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="bg-slate-900/40 border border-slate-900 rounded-xl p-6 flex items-center gap-5 backdrop-blur-sm">
            <div className="p-4 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 shadow-inner">
              <FileText size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Berkas</p>
              <h3 className="text-2xl font-bold text-slate-100 mt-1">{stats.total_files}</h3>
            </div>
          </div>

          <div className="bg-slate-900/40 border border-slate-900 rounded-xl p-6 flex items-center gap-5 backdrop-blur-sm">
            <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shadow-inner">
              <Database size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Baris Disanitasi</p>
              <h3 className="text-2xl font-bold text-slate-100 mt-1">{stats.total_rows.toLocaleString('id-ID')}</h3>
            </div>
          </div>

          <div className="bg-slate-900/40 border border-slate-900 rounded-xl p-6 flex items-center gap-5 backdrop-blur-sm">
            <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 shadow-inner">
              <Percent size={24} />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Rasio Keberhasilan</p>
              <h3 className="text-2xl font-bold text-slate-100 mt-1">{stats.success_rate}%</h3>
            </div>
          </div>
        </div>
      )}

      {/* History Log Table */}
      <div className="bg-slate-900/30 border border-slate-900 rounded-xl shadow-2xl backdrop-blur-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-900">
          <h3 className="font-bold text-base text-slate-200">Riwayat Penyamaran Berkas</h3>
          <p className="text-xs text-slate-500 mt-1">Daftar lengkap pengerjaan audit yang dilakukan secara lokal</p>
        </div>
        
        {jobs.length === 0 ? (
          <div className="py-16 text-center text-slate-500">
            <Calendar size={48} className="mx-auto mb-4 text-slate-600 opacity-50" />
            <p className="font-medium text-sm">Belum ada riwayat pekerjaan penyamaran.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-900/80 bg-slate-950/20 text-xs font-semibold text-slate-400 uppercase">
                  <th className="px-6 py-4">Waktu</th>
                  <th className="px-6 py-4">Nama Berkas</th>
                  <th className="px-6 py-4">Ukuran</th>
                  <th className="px-6 py-4">Jumlah Baris</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-sm">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-900/10 transition-colors duration-150">
                    <td className="px-6 py-4 font-medium text-slate-300">{formatDate(job.created_at)}</td>
                    <td className="px-6 py-4 font-semibold text-slate-200 truncate max-w-xs">{job.file_name}</td>
                    <td className="px-6 py-4 text-slate-400">{formatSize(job.file_size_bytes)}</td>
                    <td className="px-6 py-4 text-slate-400">
                      {job.row_count !== null ? job.row_count.toLocaleString('id-ID') : '-'}
                    </td>
                    <td className="px-6 py-4">
                      {job.status === 'SUCCESS' ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                          <CheckCircle2 size={12} />
                          Sukses
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 border border-red-500/30 text-red-400">
                          <XCircle size={12} />
                          Gagal
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleOpenDetails(job)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-indigo-400 border border-slate-800/80 transition-all duration-200"
                      >
                        <Info size={12} />
                        Detail
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {jobs.length > 0 && (
          <div className="px-6 py-4 border-t border-slate-900/80 flex items-center justify-between">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
            >
              <ChevronLeft size={14} />
              Sebelumnya
            </button>
            <span className="text-xs font-medium text-slate-500">Halaman {page + 1}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasMore}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
            >
              Berikutnya
              <ChevronRight size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Details Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm transition-opacity">
          <div className="relative w-full max-w-xl bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/20">
              <div>
                <h3 className="font-bold text-slate-200 text-base">Detail Riwayat Audit</h3>
                <p className="text-xs text-slate-500 mt-0.5 truncate max-w-sm">{selectedJob.file_name}</p>
              </div>
              <button
                onClick={handleCloseModal}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-transparent hover:border-slate-700 transition-all duration-200"
              >
                <X size={16} />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 text-sm text-slate-300">
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-slate-950/30 border border-slate-800/50 rounded-xl">
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Waktu Eksekusi</p>
                  <p className="mt-1 font-medium text-slate-300">{formatDate(selectedJob.created_at)}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Status Akhir</p>
                  <p className="mt-1">
                    {selectedJob.status === 'SUCCESS' ? (
                      <span className="text-emerald-400 font-semibold">SUKSES</span>
                    ) : (
                      <span className="text-red-400 font-semibold">GAGAL</span>
                    )}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Ukuran Berkas</p>
                  <p className="mt-1 font-medium text-slate-300">{formatSize(selectedJob.file_size_bytes)}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-500 font-semibold uppercase">Jumlah Baris</p>
                  <p className="mt-1 font-medium text-slate-300">
                    {selectedJob.row_count !== null ? selectedJob.row_count.toLocaleString('id-ID') : '-'}
                  </p>
                </div>
              </div>

              {selectedJob.status === 'SUCCESS' ? (
                <div>
                  <h4 className="font-bold text-slate-200 text-sm mb-3">Kolom yang Disamarkan</h4>
                  {isLoadingDetails ? (
                    <div className="py-10 text-center">
                      <Loader2 className="animate-spin text-indigo-500 mx-auto mb-2" size={24} />
                      <p className="text-xs text-slate-500">Memuat rincian...</p>
                    </div>
                  ) : detailsError ? (
                    <p className="text-red-400 text-xs">{detailsError}</p>
                  ) : jobDetails.length === 0 ? (
                    <p className="text-slate-500 text-xs py-4 text-center">Tidak ada kolom yang disamarkan (seluruhnya diabaikan).</p>
                  ) : (
                    <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-950/20">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-950/40 text-[10px] font-semibold text-slate-500 uppercase border-b border-slate-800">
                            <th className="px-4 py-2.5">Nama Kolom</th>
                            <th className="px-4 py-2.5">Aturan Masking</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/40 text-xs">
                          {jobDetails.map((detail) => (
                            <tr key={detail.id} className="hover:bg-slate-900/20">
                              <td className="px-4 py-2.5 font-semibold text-slate-300">{detail.column_name}</td>
                              <td className="px-4 py-2.5">
                                <span className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-medium">
                                  {detail.rule_name}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ) : (
                <div>
                  <h4 className="font-bold text-slate-200 text-sm mb-2">Pesan Kesalahan (Error)</h4>
                  <div className="p-4 bg-red-950/10 border border-red-900/20 rounded-xl text-red-400 font-mono text-xs leading-relaxed break-all">
                    {selectedJob.error_message || 'Terjadi kesalahan sistem yang tidak diketahui.'}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-slate-800 flex justify-end bg-slate-950/20">
              <button
                onClick={handleCloseModal}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all duration-150"
              >
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
