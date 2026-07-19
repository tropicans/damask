import React from 'react';
import { Eye, HelpCircle } from 'lucide-react';

interface PreviewTableProps {
  /** Column headers of the uploaded dataset. */
  headers: string[];
  /** Sample rows containing data values for previewing. */
  previewRows: string[][];
  /** Auto-recommended masking rules suggested by regex analysis of headers. */
  recommendations: Record<string, string>;
  /** User-configured rules mapped to column names. */
  selectedRules: Record<string, string>;
  /** Callback fired when a masking rule is modified in a dropdown select. */
  onRuleChange: (column: string, rule: string) => void;
}

/**
 * Array of available masking strategy options supported by the backend engine.
 */
const MASKING_OPTIONS = [
  "No Masking",
  "Fake Name",
  "Fake Email",
  "Fake Phone",
  "Anonymize ID/Number",
  "Perturb Numeric"
];

/**
 * Renders the preview matrix of the uploaded file and provides dropdown options
 * for assigning masking strategies to each header.
 */
export const PreviewTable: React.FC<PreviewTableProps> = ({
  headers,
  previewRows,
  recommendations,
  selectedRules,
  onRuleChange,
}) => {
  return (
    <div className="w-full bg-slate-800/20 border border-slate-700/60 rounded-xl overflow-hidden mt-8 transition-all duration-300">
      <div className="p-5 border-b border-slate-700/60 flex justify-between items-center bg-slate-800/10">
        <div className="flex items-center gap-2">
          <Eye className="text-indigo-400" size={18} />
          <h3 className="font-semibold text-slate-200">Pratinjau Data & Aturan Penyamaran</h3>
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-1.5">
          <HelpCircle size={14} /> Hanya 3 baris pertama yang ditampilkan untuk pratinjau
        </div>
      </div>

      <div className="overflow-x-auto w-full">
        <table className="w-full border-collapse text-left text-sm text-slate-300">
          <thead className="bg-slate-800/40 text-slate-400 font-semibold border-b border-slate-700/60">
            <tr>
              {headers.map((header) => {
                const recommended = recommendations[header] || "No Masking";
                const activeRule = selectedRules[header] || recommended;
                return (
                  <th key={header} className="p-4 min-w-[200px] border-r border-slate-700/40 last:border-0">
                    <div className="flex flex-col gap-2">
                      <div className="font-medium text-slate-200 truncate" title={header}>
                        {header}
                      </div>
                      
                      <div className="relative">
                        <select
                          value={activeRule}
                          onChange={(e) => onRuleChange(header, e.target.value)}
                          className="w-full bg-slate-900 border border-slate-700 rounded-md p-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 cursor-pointer transition-colors duration-200"
                        >
                          {MASKING_OPTIONS.map((opt) => (
                            <option key={opt} value={opt}>
                              {opt}
                            </option>
                          ))}
                        </select>
                      </div>

                      {recommended !== "No Masking" && (
                        <div className="text-[10px] bg-indigo-500/15 border border-indigo-500/30 text-indigo-400 px-2 py-0.5 rounded-full self-start font-medium">
                          Rekomendasi: {recommended}
                        </div>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {previewRows.length === 0 ? (
              <tr>
                <td colSpan={headers.length} className="p-8 text-center text-slate-500 italic">
                  Tidak ada data untuk ditampilkan.
                </td>
              </tr>
            ) : (
              previewRows.map((row, idx) => (
                <tr
                  key={idx}
                  className="border-b border-slate-700/30 last:border-0 hover:bg-slate-800/10 transition-colors duration-150"
                >
                  {row.map((cell, cIdx) => (
                    <td
                      key={cIdx}
                      className="p-4 border-r border-slate-700/20 last:border-0 truncate max-w-xs"
                      title={String(cell)}
                    >
                      {cell === "" ? (
                        <span className="text-slate-600 font-mono italic">empty</span>
                      ) : (
                        String(cell)
                      )}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
