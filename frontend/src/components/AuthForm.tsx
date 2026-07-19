import { useState } from 'react';
import { ShieldCheck, Loader2, AlertCircle, User, Mail, Lock } from 'lucide-react';
import { loginUser, registerUser, type UserResponse } from '../api/auth';

interface AuthFormProps {
  /** Callback fired on successful registration or login, providing user object. */
  onAuthSuccess: (user: UserResponse) => void;
}

/**
 * AuthForm component rendering Login and Registration tabs.
 * Validates inputs locally before querying the authentication endpoints.
 */
export const AuthForm = ({ onAuthSuccess }: AuthFormProps) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles form submit. Performs local validations and authenticates via API helper.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Basic Validation
    if (!email || !password) {
      setError('Semua kolom wajib diisi.');
      return;
    }
    if (password.length < 8) {
      setError('Kata sandi harus minimal 8 karakter.');
      return;
    }
    if (!isLogin && !username) {
      setError('Nama pengguna wajib diisi.');
      return;
    }

    setIsLoading(true);

    try {
      if (isLogin) {
        const user = await loginUser(email, password);
        onAuthSuccess(user);
      } else {
        // Register first
        await registerUser(username, email, password);
        // Login immediately after registration
        const user = await loginUser(email, password);
        onAuthSuccess(user);
      }
    } catch (err: any) {
      console.error(err);
      const msg = err.response?.data?.detail || 'Terjadi kesalahan sistem. Silakan coba lagi.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto my-12">
      {/* Brand Header */}
      <div className="text-center mb-8 flex flex-col items-center">
        <div className="p-3.5 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 mb-4 shadow-inner">
          <ShieldCheck size={36} className="animate-pulse" />
        </div>
        <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight">
          SecureData Web
        </h2>
        <p className="text-xs text-slate-400 font-medium tracking-widest uppercase mt-1">
          LOCAL DATA SANITIZER
        </p>
      </div>

      {/* Auth Card Container */}
      <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl p-6 md:p-8 transition-all duration-300">
        
        {/* Tab Buttons */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-900 mb-6">
          <button
            type="button"
            onClick={() => {
              setIsLogin(true);
              setError(null);
            }}
            className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
              isLogin
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Masuk
          </button>
          <button
            type="button"
            onClick={() => {
              setIsLogin(false);
              setError(null);
            }}
            className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
              !isLogin
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Daftar Akun
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-5 p-4 bg-red-950/40 border border-red-900/60 rounded-xl flex items-start gap-3 text-red-400 text-sm animate-shake">
            <AlertCircle className="shrink-0 mt-0.5" size={18} />
            <div>
              <p className="font-semibold">Terjadi Masalah</p>
              <p className="text-xs text-red-300/90 mt-0.5 leading-relaxed">{error}</p>
            </div>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Nama Pengguna
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <User size={16} />
                </span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Masukkan nama pengguna"
                  className="w-full bg-slate-950/80 border border-slate-800 hover:border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all duration-200"
                  disabled={isLoading}
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Alamat Email
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                <Mail size={16} />
              </span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="nama@perusahaan.com"
                className="w-full bg-slate-950/80 border border-slate-800 hover:border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all duration-200"
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Kata Sandi
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                <Lock size={16} />
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950/80 border border-slate-800 hover:border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-100 placeholder-slate-600 outline-none transition-all duration-200"
                disabled={isLoading}
              />
            </div>
            <p className="text-[10px] text-slate-500 mt-2 font-medium">
              * Minimal 8 karakter
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl font-semibold text-sm shadow-lg shadow-indigo-900/25 flex items-center justify-center gap-2 transition-all duration-200 mt-6 ${
              isLoading ? 'cursor-not-allowed opacity-75' : ''
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                {isLogin ? 'Memverifikasi...' : 'Mendaftar...'}
              </>
            ) : (
              isLogin ? 'Masuk ke Aplikasi' : 'Daftar & Masuk'
            )}
          </button>
        </form>
      </div>
      
      {/* Subtitle Security Note */}
      <p className="text-center text-slate-600 text-xs mt-6 max-w-xs mx-auto leading-relaxed">
        Sesi Anda dienkripsi secara lokal via JWT. Data tabular diproses strictly di dalam RAM server.
      </p>
    </div>
  );
};
