/**
 * StudyForge OS - API Client Configuration
 * Supports unified routing across both local development (via Vite dev proxy)
 * and production deployments (via vercel.json /api proxy rewrites or VITE_API_BASE_URL).
 */

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();

// If VITE_API_BASE_URL is explicitly set, normalize and use it.
// Otherwise, default to empty string so all /api requests use relative routing,
// cleanly handled by Vite dev proxy in local development and vercel.json rewrites in production.
export const API_BASE_URL = rawBaseUrl ? rawBaseUrl.replace(/\/+$/, '') : '';

export const apiUrl = (path) => {
  const cleanPath = (path || '').startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

export const isProductionBackendConfigured = () => {
  return Boolean(API_BASE_URL);
};
