export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  LOGIN: '/api/login',
  ISSUE_DIPLOMA: '/api/issue',
  VERIFY_DIPLOMA: '/api/verify',
  MY_DIPLOMAS: '/api/my-diplomas',
  ALL_DIPLOMAS: '/api/diplomas',
  DOWNLOAD_DIPLOMA: '/api/download',
};
