// In production (Koyeb), the API is on the same domain, so we use relative URLs
// In development, we need the full localhost URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const API_ENDPOINTS = {
  LOGIN: '/login',
  ISSUE_DIPLOMA: '/issue',
  VERIFY_DIPLOMA: '/verify',
  MY_DIPLOMAS: '/list',
  ALL_DIPLOMAS: '/list',
  DOWNLOAD_DIPLOMA: '/download',
};
