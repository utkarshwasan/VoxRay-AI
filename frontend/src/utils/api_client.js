import axios from 'axios';
import { stackApp } from '../stack';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * Creates an axios instance with automatic Stack Auth token injection.
 * Uses the 'x-stack-access-token' header for consistency with backend.
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(async (config) => {
  try {
    const user = stackApp.useUser?.(); // This might not work outside React
    // Fallback: get user from app directly
    const currentUser = user || await stackApp.getUser?.();
    
    if (currentUser) {
      const authJson = await currentUser.getAuthJson();
      if (authJson?.accessToken) {
        config.headers['x-stack-access-token'] = authJson.accessToken;
      }
    }
  } catch (error) {
    console.warn('Failed to get auth token:', error);
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default apiClient;

/**
 * Helper for FormData uploads with auth
 */
export const authenticatedUpload = async (url, formData) => {
  try {
    const user = await stackApp.getUser?.();
    const headers = {
      'Content-Type': 'multipart/form-data',
    };
    
    if (user) {
      const authJson = await user.getAuthJson();
      if (authJson?.accessToken) {
        headers['x-stack-access-token'] = authJson.accessToken;
      }
    }
    
    return axios.post(`${API_BASE_URL}${url}`, formData, { headers });
  } catch (error) {
    console.error('Authenticated upload failed:', error);
    throw error;
  }
};
