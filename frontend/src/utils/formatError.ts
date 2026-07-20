/**
 * Safely extracts a user-friendly error string from Axios/FastAPI error responses.
 * Prevents React child rendering errors when FastAPI returns 422 validation error objects.
 */
export const extractErrorMessage = (
  err: any,
  fallbackMessage: string = 'Terjadi kesalahan sistem. Silakan coba lagi.'
): string => {
  if (!err) return fallbackMessage;

  const detail = err.response?.data?.detail ?? err.message ?? err.detail;

  if (!detail) return fallbackMessage;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    // Detail is an array of FastAPI Pydantic ValidationError objects: [{ msg, loc, type }, ...]
    const messages = detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object' && item.msg) return item.msg;
        return null;
      })
      .filter(Boolean);

    return messages.length > 0 ? messages.join('. ') : fallbackMessage;
  }

  if (typeof detail === 'object' && detail !== null) {
    if (detail.msg && typeof detail.msg === 'string') {
      return detail.msg;
    }
    return JSON.stringify(detail);
  }

  return String(detail);
};
