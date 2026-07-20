import { useState, useEffect } from 'react';
import { ShieldCheck, Trash2, Loader2, Download, AlertCircle, LogOut, User as UserIcon, CheckCircle2, AlertTriangle, UploadCloud, X, FileText, Lock, UserPlus } from 'lucide-react';
import { Dropzone } from './components/Dropzone';
import { PreviewTable } from './components/PreviewTable';
import { uploadFileForPreview } from './api/preview';
import type { PreviewResponse } from './api/preview';
import { maskFile, revertFile } from './api/mask';
import { AuthForm } from './components/AuthForm';
import { getCurrentUser, logoutUser, createInvite, type UserResponse } from './api/auth';
import { registerUnauthorizedCallback } from './api/client';
import { AuditDashboard } from './components/AuditDashboard';
import { UserManagement } from './components/UserManagement';

/**
 * Main application component. Manages authentication sessions, navigation tabs,
 * uploaded file state, and trigger functions for file previews and masking downloads.
 */
function App() {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isCheckingSession, setIsCheckingSession] = useState(true);
  const [activeTab, setActiveTab] = useState<'masking' | 'revert' | 'audit' | 'users'>('masking');

  // Invite States
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteUrl, setInviteUrl] = useState<string | null>(null);
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteCopied, setInviteCopied] = useState(false);

  // Active File States
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMasking, setIsMasking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);
  const [selectedRules, setSelectedRules] = useState<Record<string, string>>({});

  // Reversion & Success States
  const [generateKey, setGenerateKey] = useState(false);
  const [successData, setSuccessData] = useState<{ blob: Blob; filename: string; generatedKey: boolean } | null>(null);

  // Revert Page States
  const [revertFileObj, setRevertFileObj] = useState<File | null>(null);
  const [revertKeyObj, setRevertKeyObj] = useState<File | null>(null);
  const [isReverting, setIsReverting] = useState(false);
  const [revertError, setRevertError] = useState<string | null>(null);

  /**
   * Validates the active user session token on app load or token changes.
   */
  useEffect(() => {
    // Register global 401 unauthorized handler
    registerUnauthorizedCallback(() => {
      setUser(null);
      handleClear();
    });

    const verifySession = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
      } catch (err) {
        console.error("Token verification failed:", err);
        setUser(null);
      } finally {
        setIsCheckingSession(false);
      }
    };
    verifySession();
  }, []);

  /**
   * Sets token and user objects on successful authentication.
   */
  const handleAuthSuccess = (loggedInUser: UserResponse) => {
    setUser(loggedInUser);
  };

  /**
   * Clears session storage and logs out the active user.
   */
  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (err) {
      console.error("Logout request failed:", err);
    }
    setUser(null);
    setActiveTab('masking');
    handleClear();
  };

  const handleCreateInvite = async () => {
    setInviteLoading(true);
    try {
      const result = await createInvite();
      setInviteUrl(result.invite_url);
      setShowInviteModal(true);
    } catch (err: any) {
      console.error('Failed to create invite:', err);
    } finally {
      setInviteLoading(false);
    }
  };

  /**
   * Triggers the file upload and preview API.
   * Caches the output recommendations into local selectedRules state.
   */
  const handleFileSelect = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsLoading(true);
    setError(null);
    setPreviewData(null);
    setSelectedRules({});

    try {
      const data = await uploadFileForPreview(selectedFile);
      setPreviewData(data);
      const initialRules = { ...data.recommendations };
      setSelectedRules(initialRules);
    } catch (err: any) {
      console.error(err);
      const msg = err.response?.data?.detail || 'Gagal memproses pratinjau berkas.';
      setError(msg);
      setFile(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Callback fired when a rule in the PreviewTable is modified.
   */
  const handleRuleChange = (column: string, rule: string) => {
    setSelectedRules((prev) => ({
      ...prev,
      [column]: rule,
    }));
  };

  /**
   * Clears the active file selection and resets the app state.
   */
  const handleClear = () => {
    setFile(null);
    setPreviewData(null);
    setSelectedRules({});
    setError(null);
    setSuccessData(null);
  };

  /**
   * Executes the masking engine process. Submits the file along with the rules JSON.
   */
  const handleMaskExecute = async () => {
    if (!file || !previewData) return;
    setIsMasking(true);
    setError(null);
    try {
      const { blob, filename } = await maskFile(file, selectedRules, generateKey);
      setSuccessData({ blob, filename, generatedKey: generateKey });
    } catch (err: any) {
      console.error(err);
      let msg = 'Gagal memproses penyamaran berkas.';
      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const parsed = JSON.parse(text);
          msg = parsed.detail || msg;
        } catch (e) {
          // ignore parsing error, use default msg
        }
      } else if (err.response?.data?.detail) {
        msg = err.response.data.detail;
      }
      setError(msg);
    } finally {
      setIsMasking(false);
    }
  };

  /**
   * Executes the data reversion process by uploading the masked file and key.
   */
  const handleRevertExecute = async () => {
    if (!revertFileObj || !revertKeyObj) return;
    setIsReverting(true);
    setRevertError(null);
    try {
      const { blob, filename } = await revertFile(revertFileObj, revertKeyObj);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // Clear fields on success
      setRevertFileObj(null);
      setRevertKeyObj(null);
    } catch (err: any) {
      console.error(err);
      let msg = 'Gagal memproses pemulihan data.';
      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const parsed = JSON.parse(text);
          msg = parsed.detail || msg;
        } catch (e) {
          // ignore
        }
      } else if (err.response?.data?.detail) {
        msg = err.response.data.detail;
      }
      setRevertError(msg);
    } finally {
      setIsReverting(false);
    }
  };

  /**
   * Downloads the file from the success screen blob data.
   */
  const downloadSuccessFile = () => {
    if (!successData) return;
    const url = window.URL.createObjectURL(successData.blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', successData.filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  if (isCheckingSession) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="animate-spin text-indigo-500 mx-auto mb-4" size={40} />
          <p className="text-sm text-slate-400 font-medium">Memuat Sesi...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <AuthForm onAuthSuccess={handleAuthSuccess} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
              <ShieldCheck size={24} />
            </div>
            <div>
              <h1 className="font-bold text-lg leading-none text-slate-200">SecureData Web</h1>
              <span className="text-[10px] text-slate-500 font-medium">LOCAL DATA SANITIZER</span>
            </div>
          </div>

          {user && (
            <nav className="flex items-center gap-1 bg-slate-900/60 border border-slate-800/80 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('masking')}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                  activeTab === 'masking'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                Masking Engine
              </button>
              <button
                onClick={() => setActiveTab('revert')}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                  activeTab === 'revert'
                    ? 'bg-indigo-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                Revert Data
              </button>
              {(user.role === 'admin' || user.role === 'auditor') && (
                <button
                  onClick={() => setActiveTab('audit')}
                  className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                    activeTab === 'audit'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  Riwayat Audit
                </button>
              )}
              {user.role === 'admin' && (
                <button
                  onClick={() => setActiveTab('users')}
                  className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all duration-200 ${
                    activeTab === 'users'
                      ? 'bg-indigo-600 text-white shadow-md'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  Manajemen User
                </button>
              )}
            </nav>
          )}

          <div className="flex items-center gap-4">
            {user?.role === 'admin' && (
              <button
                onClick={handleCreateInvite}
                disabled={inviteLoading}
                className="px-3 py-1.5 text-xs font-semibold bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-600/40 text-emerald-400 rounded-lg transition-all duration-200 flex items-center gap-1.5"
                title="Buat tautan undangan untuk user baru"
              >
                <UserPlus size={14} />
                {inviteLoading ? 'Membuat...' : 'Undang User'}
              </button>
            )}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs font-semibold text-slate-300">
              <UserIcon size={14} className="text-indigo-400" />
              <span>{user.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 hover:text-red-400 border border-slate-800 hover:border-red-950/40 rounded-lg text-xs font-semibold text-slate-400 transition-all duration-200"
            >
              <LogOut size={14} />
              <span>Keluar</span>
            </button>
            <div className="text-xs text-slate-500 font-medium bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full">
              v1.0.0
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-12 flex flex-col items-center">
        {activeTab === 'masking' ? (
          successData ? (
            <div className="w-full max-w-xl mx-auto bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl flex flex-col items-center text-center">
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full mb-5">
                <CheckCircle2 size={44} />
              </div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2">Penyamaran Data Berhasil!</h2>
              <p className="text-sm text-slate-400 mb-6 leading-relaxed">
                Data Anda telah berhasil disamarkan di dalam memori. Silakan unduh hasil file dan kunci pemulihan di bawah ini.
              </p>

              <div className="w-full bg-slate-950 border border-slate-800/80 rounded-xl p-4 mb-6 flex flex-col gap-3 text-left">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 font-semibold uppercase">Nama Berkas</span>
                  <span className="text-slate-300 font-medium truncate max-w-xs">{successData.filename}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 font-semibold uppercase">Kunci Pemulihan</span>
                  <span className="text-slate-300 font-medium">
                    {successData.generatedKey ? "Dibuat" : "Tidak Dibuat"}
                  </span>
                </div>
              </div>

              {successData.generatedKey ? (
                <div className="w-full p-4 bg-amber-950/30 border border-amber-900/50 text-amber-300 rounded-xl text-left text-xs mb-6 flex gap-3">
                  <AlertTriangle className="shrink-0 mt-0.5 text-amber-500" size={16} />
                  <div>
                    <h5 className="font-bold mb-1">Peringatan Keamanan Utama</h5>
                    <p className="leading-relaxed text-slate-400">
                      Paket ZIP berisi berkas hasil masking dan berkas kunci pemulihan JSON. Kunci pemulihan ini disimpan secara lokal dan <strong>TIDAK disimpan di server</strong>. Simpan kunci ini dengan aman. Jika hilang, Anda tidak akan pernah bisa memulihkan data asli kembali.
                    </p>
                  </div>
                </div>
              ) : null}

              <div className="flex gap-4 w-full">
                <button
                  onClick={downloadSuccessFile}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 transition-all duration-200 shadow-md shadow-indigo-900/30"
                >
                  <Download size={16} />
                  {successData.generatedKey ? "Unduh Paket (ZIP)" : "Unduh Berkas Masking"}
                </button>
                <button
                  onClick={handleClear}
                  className="flex-1 bg-slate-950 border border-slate-800 hover:bg-slate-900 hover:border-slate-700 text-slate-300 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200"
                >
                  Kembali ke Masking
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="text-center max-w-xl mx-auto mb-10">
                <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight mb-3">
                  Sanitasi Tabular Data Anda Secara Instan
                </h2>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Unggah file CSV atau XLSX Anda untuk menyamarkan PII (Personal Identifiable Information) sebelum diunggah ke eksternal LLM. Data diproses 100% di dalam memori RAM Anda.
                </p>
              </div>

              {!previewData ? (
                <Dropzone
                  onFileSelect={handleFileSelect}
                  isLoading={isLoading}
                  error={error}
                  setError={setError}
                />
              ) : (
                <div className="w-full">
                  <div className="w-full max-w-2xl mx-auto bg-slate-900 border border-slate-800 p-5 rounded-xl flex items-center justify-between shadow-lg">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-lg">
                        <ShieldCheck size={22} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-slate-200 text-sm truncate max-w-xs md:max-w-md">
                          {file?.name}
                        </h4>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {(previewData.size_bytes / 1024).toFixed(1)} KB • {previewData.headers.length} Kolom terdeteksi
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={handleClear}
                        className="p-2 text-slate-400 hover:text-red-400 bg-slate-950 border border-slate-800 hover:border-red-950 rounded-lg transition-all duration-200"
                        title="Hapus Berkas"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  {error && (
                    <div className="mt-4 max-w-2xl mx-auto p-4 bg-red-950/40 border border-red-900/60 rounded-xl flex items-start gap-3 text-red-400 text-sm">
                      <AlertCircle className="shrink-0 mt-0.5" size={18} />
                      <div>
                        <h4 className="font-semibold mb-1">Gagal memproses penyamaran berkas</h4>
                        <p>{error}</p>
                      </div>
                    </div>
                  )}

                  <PreviewTable
                    headers={previewData.headers}
                    previewRows={previewData.preview_rows}
                    recommendations={previewData.recommendations}
                    selectedRules={selectedRules}
                    onRuleChange={handleRuleChange}
                  />

                  <div className="mt-8 flex items-center justify-between max-w-6xl mx-auto w-full">
                    <label className="flex items-center gap-2.5 cursor-pointer text-sm text-slate-300 hover:text-slate-200 select-none">
                      <input
                        type="checkbox"
                        checked={generateKey}
                        onChange={(e) => setGenerateKey(e.target.checked)}
                        className="w-4 h-4 rounded border-slate-800 bg-slate-900 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-slate-950"
                      />
                      <span>Buat Kunci Pemulihan (Generate Reversion Key)</span>
                    </label>

                    <button
                      onClick={handleMaskExecute}
                      disabled={isMasking}
                      className={`bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all duration-200 ${
                        isMasking ? 'cursor-not-allowed opacity-70' : 'shadow-md shadow-indigo-900/30'
                      }`}
                    >
                      {isMasking ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Memproses & Mengunduh...
                        </>
                      ) : (
                        <>
                          <Download size={16} />
                          Mulai Masking & Unduh
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </>
          )
        ) : activeTab === 'revert' ? (
          <div className="w-full max-w-2xl mx-auto flex flex-col">
            <div className="text-center max-w-xl mx-auto mb-10">
              <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight mb-3">
                Kembalikan Data Asli Anda
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                Unggah berkas hasil masking (.csv/.xlsx) dan berkas kunci pemulihan JSON (.json) Anda untuk memulihkan data sensitif kembali ke nilai aslinya secara lokal di memori.
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col gap-6">
              {/* File 1: Masked File */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  1. Berkas Hasil Masking (.csv / .xlsx)
                </label>
                {revertFileObj ? (
                  <div className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-800 rounded-xl">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-lg">
                        <FileText size={18} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-200 truncate">{revertFileObj.name}</p>
                        <p className="text-xs text-slate-500">{(revertFileObj.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setRevertFileObj(null)}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-200"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={() => document.getElementById('revert-file-input')?.click()}
                    className="flex flex-col items-center justify-center p-8 bg-slate-950 border border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-xl cursor-pointer hover:bg-slate-950/60 transition-all duration-200"
                  >
                    <input
                      id="revert-file-input"
                      type="file"
                      accept=".csv,.xlsx"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          const f = e.target.files[0];
                          if (f.size > 50 * 1024 * 1024) {
                            setRevertError("Ukuran berkas masking melebihi batas 50MB.");
                            return;
                          }
                          setRevertError(null);
                          setRevertFileObj(f);
                        }
                      }}
                      className="hidden"
                    />
                    <UploadCloud size={24} className="text-slate-500 mb-2" />
                    <p className="text-xs text-slate-400 font-medium">Pilih berkas hasil masking (.csv / .xlsx)</p>
                    <p className="text-[10px] text-slate-600 mt-1">Maksimal 50MB</p>
                  </div>
                )}
              </div>

              {/* File 2: Reversion Key JSON */}
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                  2. Berkas Kunci Pemulihan (.json)
                </label>
                {revertKeyObj ? (
                  <div className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-800 rounded-xl">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-lg">
                        <Lock size={18} />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-200 truncate">{revertKeyObj.name}</p>
                        <p className="text-xs text-slate-500">{(revertKeyObj.size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setRevertKeyObj(null)}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-all duration-200"
                    >
                      <X size={16} />
                    </button>
                  </div>
                ) : (
                  <div
                    onClick={() => document.getElementById('revert-key-input')?.click()}
                    className="flex flex-col items-center justify-center p-8 bg-slate-950 border border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-xl cursor-pointer hover:bg-slate-950/60 transition-all duration-200"
                  >
                    <input
                      id="revert-key-input"
                      type="file"
                      accept=".json"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          const f = e.target.files[0];
                          if (f.size > 10 * 1024 * 1024) {
                            setRevertError("Ukuran berkas kunci pemulihan melebihi batas 10MB.");
                            return;
                          }
                          setRevertError(null);
                          setRevertKeyObj(f);
                        }
                      }}
                      className="hidden"
                    />
                    <UploadCloud size={24} className="text-slate-500 mb-2" />
                    <p className="text-xs text-slate-400 font-medium">Pilih berkas kunci pemulihan (.json)</p>
                    <p className="text-[10px] text-slate-600 mt-1">Maksimal 10MB</p>
                  </div>
                )}
              </div>

              {/* Revert Action & Error displays */}
              {revertError && (
                <div className="p-4 bg-red-950/40 border border-red-900/60 rounded-xl flex items-start gap-3 text-red-400 text-sm">
                  <AlertCircle className="shrink-0 mt-0.5" size={18} />
                  <div>
                    <h4 className="font-semibold mb-1">Gagal memproses revert data</h4>
                    <p>{revertError}</p>
                  </div>
                </div>
              )}

              <div className="flex justify-end mt-2">
                <button
                  onClick={handleRevertExecute}
                  disabled={!revertFileObj || !revertKeyObj || isReverting}
                  className={`bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all duration-200 ${
                    (!revertFileObj || !revertKeyObj || isReverting)
                      ? 'cursor-not-allowed opacity-50'
                      : 'shadow-md shadow-indigo-900/30'
                  }`}
                >
                  {isReverting ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Memproses & Mengunduh...
                    </>
                  ) : (
                    <>
                      <Download size={16} />
                      Mulai Revert & Unduh
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : activeTab === 'users' && user.role === 'admin' ? (
          <UserManagement />
        ) : (user.role === 'admin' || user.role === 'auditor') ? (
          <AuditDashboard user={user} />
        ) : (
          <div className="text-center py-12">
            <p className="text-red-400 font-semibold text-sm">Akses ditolak. Peran tidak sah.</p>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-600 bg-slate-950/20">
        <p>© 2026 SecureData Web. Diproses strictly di RAM untuk menjamin kepatuhan data.</p>
      </footer>

      {showInviteModal && inviteUrl && (
        <div
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => { setShowInviteModal(false); setInviteCopied(false); }}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-lg shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-slate-100 font-bold text-lg mb-2 flex items-center gap-2">
              <UserPlus size={20} className="text-emerald-400" />
              Tautan Undangan Dibuat
            </h3>
            <p className="text-slate-400 text-sm mb-4">
              Bagikan tautan berikut kepada pengguna yang ingin didaftarkan. Tautan ini hanya dapat digunakan sekali dan berlaku selama 48 jam.
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                readOnly
                value={inviteUrl}
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-300 font-mono outline-none"
              />
              <button
                onClick={() => {
                  navigator.clipboard.writeText(inviteUrl);
                  setInviteCopied(true);
                  setTimeout(() => setInviteCopied(false), 2000);
                }}
                className="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors"
              >
                {inviteCopied ? '✓ Disalin' : 'Salin'}
              </button>
            </div>
            <p className="text-amber-500/80 text-[11px] mt-3 flex items-start gap-1.5">
              <span>⚠</span>
              Simpan tautan ini dengan aman. Siapa pun yang memiliki tautan ini dapat mendaftar sebagai pengguna baru.
            </p>
            <button
              onClick={() => { setShowInviteModal(false); setInviteCopied(false); }}
              className="mt-4 w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm rounded-lg transition-colors"
            >
              Tutup
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
