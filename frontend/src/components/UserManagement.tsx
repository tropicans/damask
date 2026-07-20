import { useState, useEffect } from 'react';
import { 
  Loader2, 
  ChevronLeft, 
  ChevronRight, 
  AlertTriangle, 
  UserCheck, 
  UserX, 
  X,
  ShieldAlert,
  Users
} from 'lucide-react';
import { getUsers, updateUserStatus, updateUserRole } from '../api/admin';
import type { UserResponse } from '../api/auth';
import { extractErrorMessage } from '../utils/formatError';

interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDanger?: boolean;
}

function ConfirmationModal({
  isOpen,
  title,
  message,
  confirmLabel,
  cancelLabel = 'Batal',
  onConfirm,
  onCancel,
  isDanger = false
}: ConfirmationModalProps) {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl animate-in fade-in duration-200">
        <h3 className="text-slate-100 font-bold text-lg mb-2 flex items-center gap-2">
          <AlertTriangle className={isDanger ? 'text-red-500' : 'text-amber-500'} size={20} />
          {title}
        </h3>
        <p className="text-slate-400 text-sm mb-6 leading-relaxed">
          {message}
        </p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors duration-200"
          >
            {cancelLabel}
          </button>
          <button
            onClick={onConfirm}
            className={`px-4 py-2 text-xs font-semibold rounded-lg text-white transition-colors duration-200 ${
              isDanger 
                ? 'bg-red-600 hover:bg-red-500' 
                : 'bg-indigo-600 hover:bg-indigo-500'
            }`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export function UserManagement() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 10;
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    confirmLabel: string;
    onConfirm: () => void;
    isDanger: boolean;
  }>({
    isOpen: false,
    title: '',
    message: '',
    confirmLabel: '',
    onConfirm: () => {},
    isDanger: false
  });

  const fetchUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await getUsers(page, limit);
      setUsers(res.items);
      setTotal(res.total);
    } catch (err: any) {
      console.error(err);
      setError(extractErrorMessage(err, 'Gagal memuat daftar pengguna.'));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page]);

  const handleToggleStatus = (user: UserResponse) => {
    const nextStatus = !user.is_active;
    setConfirmModal({
      isOpen: true,
      title: nextStatus ? 'Aktifkan Akun' : 'Nonaktifkan Akun',
      message: nextStatus 
        ? `Apakah Anda yakin ingin mengaktifkan kembali akun pengguna ${user.email}? Pengguna ini akan dapat masuk kembali.`
        : `Apakah Anda yakin ingin menonaktifkan akun ${user.email}? Pengguna ini tidak akan dapat login lagi secara instan.`,
      confirmLabel: nextStatus ? 'Aktifkan' : 'Nonaktifkan',
      isDanger: !nextStatus,
      onConfirm: async () => {
        setConfirmModal((prev) => ({ ...prev, isOpen: false }));
        setIsLoading(true);
        try {
          await updateUserStatus(user.id, nextStatus);
          await fetchUsers();
        } catch (err: any) {
          setError(extractErrorMessage(err, 'Gagal mengubah status pengguna.'));
          setIsLoading(false);
        }
      }
    });
  };

  const handleRoleChange = (user: UserResponse, newRole: string) => {
    if (user.role === newRole) return;
    setConfirmModal({
      isOpen: true,
      title: 'Ubah Peran Pengguna',
      message: `Apakah Anda yakin ingin mengubah peran ${user.email} menjadi "${newRole.toUpperCase()}"?`,
      confirmLabel: 'Ubah Peran',
      isDanger: newRole === 'user',
      onConfirm: async () => {
        setConfirmModal((prev) => ({ ...prev, isOpen: false }));
        setIsLoading(true);
        try {
          await updateUserRole(user.id, newRole);
          await fetchUsers();
        } catch (err: any) {
          setError(extractErrorMessage(err, 'Gagal mengubah peran pengguna.'));
          setIsLoading(false);
        }
      }
    });
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString('id-ID', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  if (isLoading && users.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <div className="text-center">
          <Loader2 className="animate-spin text-indigo-500 mx-auto mb-4" size={40} />
          <p className="text-sm text-slate-400 font-medium">Memuat Daftar Pengguna...</p>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="w-full max-w-6xl mx-auto py-6">
      <div className="text-center max-w-xl mx-auto mb-10">
        <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight mb-3">
          Manajemen User
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed">
          Kelola peran pengguna (promote/demote) dan aktifkan atau nonaktifkan akun akses sistem secara instan.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-950/40 border border-red-900/60 rounded-xl flex items-start gap-3 text-red-400 text-sm">
          <ShieldAlert className="shrink-0 mt-0.5" size={18} />
          <div className="flex-1">
            <h4 className="font-semibold mb-1">Terjadi Kesalahan</h4>
            <p>{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-slate-400 hover:text-slate-200">
            <X size={16} />
          </button>
        </div>
      )}

      {/* User Management Table */}
      <div className="bg-slate-900/30 border border-slate-900 rounded-xl shadow-2xl backdrop-blur-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-900 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-base text-slate-200">Daftar Pengguna Terdaftar</h3>
            <p className="text-xs text-slate-500 mt-1">Total {total} pengguna dalam sistem</p>
          </div>
          <Users size={20} className="text-indigo-400" />
        </div>

        {users.length === 0 ? (
          <div className="py-16 text-center text-slate-500">
            <Users size={48} className="mx-auto mb-4 text-slate-600 opacity-50" />
            <p className="font-medium text-sm">Tidak ada pengguna yang terdaftar.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-900/80 bg-slate-950/20 text-xs font-semibold text-slate-400 uppercase">
                  <th className="px-6 py-4">Username</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Tanggal Daftar</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Peran (Role)</th>
                  <th className="px-6 py-4 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-sm">
                {users.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/10 transition-colors duration-150">
                    <td className="px-6 py-4 font-semibold text-slate-200">{item.username}</td>
                    <td className="px-6 py-4 text-slate-300 font-medium">{item.email}</td>
                    <td className="px-6 py-4 text-slate-400">{formatDate(item.created_at)}</td>
                    <td className="px-6 py-4">
                      {item.is_active ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                          Aktif
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 border border-red-500/30 text-red-400">
                          Nonaktif
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={item.role}
                        onChange={(e) => handleRoleChange(item, e.target.value)}
                        className="bg-slate-950 border border-slate-800 text-slate-300 text-xs rounded-lg px-2.5 py-1.5 focus:border-indigo-500 focus:ring-0 cursor-pointer outline-none transition-colors"
                      >
                        <option value="user">User</option>
                        <option value="auditor">Auditor</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleToggleStatus(item)}
                        className={`inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-200 ${
                          item.is_active
                            ? 'bg-red-950/20 hover:bg-red-950/40 text-red-400 border-red-950/40'
                            : 'bg-emerald-950/20 hover:bg-emerald-950/40 text-emerald-400 border-emerald-950/40'
                        }`}
                      >
                        {item.is_active ? (
                          <>
                            <UserX size={12} />
                            Nonaktifkan
                          </>
                        ) : (
                          <>
                            <UserCheck size={12} />
                            Aktifkan
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {users.length > 0 && (
          <div className="px-6 py-4 border-t border-slate-900/80 flex items-center justify-between bg-slate-950/10">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1 || isLoading}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
            >
              <ChevronLeft size={14} />
              Sebelumnya
            </button>
            <span className="text-xs font-medium text-slate-500">
              Halaman {page} dari {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages || isLoading}
              className="flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150"
            >
              Berikutnya
              <ChevronRight size={14} />
            </button>
          </div>
        )}
      </div>

      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        title={confirmModal.title}
        message={confirmModal.message}
        confirmLabel={confirmModal.confirmLabel}
        isDanger={confirmModal.isDanger}
        onConfirm={confirmModal.onConfirm}
        onCancel={() => setConfirmModal((prev) => ({ ...prev, isOpen: false }))}
      />
    </div>
  );
}
