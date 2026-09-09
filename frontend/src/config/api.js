/**
 * StudyForge OS - API Client Configuration
 * Supports both local development (via Vite dev proxy) and deployed environments
 * (via VITE_API_BASE_URL environment variable).
 */

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();

// Verified production Render backend endpoint
export const DEFAULT_PRODUCTION_API = 'https://sih-fastapi-backend.onrender.com';

// If VITE_API_BASE_URL is explicitly provided, use it.
// If running on a deployed host (e.g. Vercel) and no env var was set, automatically fall back to Render.
// In local development (localhost / 127.0.0.1), fall back to empty string to use Vite's dev proxy.
export const API_BASE_URL = rawBaseUrl
  ? rawBaseUrl.replace(/\/+$/, '')
  : (typeof window !== 'undefined' && window.location.hostname && !['localhost', '127.0.0.1'].includes(window.location.hostname)
      ? DEFAULT_PRODUCTION_API
      : '');

export const apiUrl = (path) => {
  const cleanPath = (path || '').startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

export const isProductionBackendConfigured = () => {
  return Boolean(API_BASE_URL);
};
