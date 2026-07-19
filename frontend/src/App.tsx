import { useState } from 'react';
import { ShieldCheck, Trash2 } from 'lucide-react';
import { Dropzone } from './components/Dropzone';
import { PreviewTable } from './components/PreviewTable';
import { uploadFileForPreview } from './api/preview';
import type { PreviewResponse } from './api/preview';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<PreviewResponse | null>(null);
  const [selectedRules, setSelectedRules] = useState<Record<string, string>>({});

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

  const handleRuleChange = (column: string, rule: string) => {
    setSelectedRules((prev) => ({
      ...prev,
      [column]: rule,
    }));
  };

  const handleClear = () => {
    setFile(null);
    setPreviewData(null);
    setSelectedRules({});
    setError(null);
  };

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
          <div className="text-xs text-slate-500 font-medium bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full">
            v1.0.0
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-12 flex flex-col items-center">
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

            <PreviewTable
              headers={previewData.headers}
              previewRows={previewData.preview_rows}
              recommendations={previewData.recommendations}
              selectedRules={selectedRules}
              onRuleChange={handleRuleChange}
            />

            <div className="mt-8 flex justify-end max-w-6xl mx-auto">
              <button
                disabled={true}
                className="bg-indigo-600/50 text-indigo-300 border border-indigo-500/30 px-6 py-2.5 rounded-lg text-sm font-semibold cursor-not-allowed flex items-center gap-2 transition-all duration-200"
              >
                Mulai Masking (Tersedia di Phase 2)
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-600 bg-slate-950/20">
        <p>© 2026 SecureData Web. Diproses strictly di RAM untuk menjamin kepatuhan data.</p>
      </footer>
    </div>
  );
}

export default App;
