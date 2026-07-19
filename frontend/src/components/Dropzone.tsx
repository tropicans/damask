import React, { useState, useRef } from 'react';
import { Upload, AlertCircle, FileSpreadsheet } from 'lucide-react';

interface DropzoneProps {
  /** Callback fired when a valid CSV or Excel file is dropped or selected. */
  onFileSelect: (file: File) => void;
  /** Disables inputs and triggers visual loading spinner during upload/preview generation. */
  isLoading: boolean;
  /** Descriptive error message to display in the alert container. */
  error: string | null;
  /** Sets or clears the active error message. */
  setError: (error: string | null) => void;
}

/**
 * Dropzone component facilitating drag-and-drop or file system selection of CSV/XLSX datasets.
 * Includes local verification logic for size limits (50MB) and supported file extensions.
 */
export const Dropzone: React.FC<DropzoneProps> = ({ onFileSelect, isLoading, error, setError }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Toggles active state of drag-and-drop area.
   */
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  /**
   * Verifies file type and file size constraints before invoking the onFileSelect callback.
   */
  const processFile = (file: File) => {
    setError(null);
    const validExtensions = ['.csv', '.xlsx'];
    const filename = file.name.toLowerCase();
    const isValidExtension = validExtensions.some(ext => filename.endsWith(ext));
    
    if (!isValidExtension) {
      setError('Format file tidak didukung. Hanya .csv dan .xlsx yang didukung.');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('Ukuran file melebihi batas 50MB.');
      return;
    }

    onFileSelect(file);
  };

  /**
   * Event handler for drag drop events.
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  /**
   * Event handler for input file changes.
   */
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  /**
   * Click handler to trigger file selection dialog.
   */
  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
        className={`relative group cursor-pointer flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300 ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-500/10'
            : 'border-slate-700 bg-slate-800/40 hover:border-slate-500 hover:bg-slate-800/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx"
          onChange={handleFileInput}
          className="hidden"
          disabled={isLoading}
        />

        {isLoading ? (
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-sm text-slate-400 font-medium">Memproses file di RAM...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className={`p-4 rounded-full bg-slate-900 border border-slate-800 mb-4 text-indigo-400 group-hover:scale-110 transition-transform duration-300`}>
              <Upload size={32} />
            </div>
            <h3 className="text-lg font-semibold text-slate-200 mb-2">Unggah Berkas Anda</h3>
            <p className="text-sm text-slate-400 max-w-sm mb-4">
              Seret dan lepas berkas CSV atau XLSX Anda di sini, atau klik untuk memilih dari komputer Anda.
            </p>
            <div className="flex gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <FileSpreadsheet size={14} /> CSV / XLSX
              </span>
              <span>•</span>
              <span>Maksimal 50MB</span>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-950/40 border border-red-900/60 rounded-xl flex items-start gap-3 text-red-400 text-sm">
          <AlertCircle className="shrink-0 mt-0.5" size={18} />
          <div>
            <h4 className="font-semibold mb-1">Gagal memproses berkas</h4>
            <p>{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};
