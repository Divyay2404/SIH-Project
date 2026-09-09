/**
 * StudyForge OS - API Client Configuration
 * Supports both local development (via Vite dev proxy) and deployed environments
 * (via VITE_API_BASE_URL environment variable).
 */

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export const apiUrl = (path) => {
  const cleanPath = (path || '').startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};

export const isProductionBackendConfigured = () => {
  return Boolean(API_BASE_URL);
};
