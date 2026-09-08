/**
 * StudyForge OS - API Client Configuration
 * Supports both local development (via Vite dev proxy) and deployed environments
 * (via VITE_API_BASE_URL environment variable).
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

export const apiUrl = (path) => {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
};
