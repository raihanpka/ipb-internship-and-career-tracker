import api from '../api/axios';
import { fileService } from './fileService';
import { handleApiError } from '../utils/apiUtils';

export const authService = {
  login: async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      handleApiError(error, 'Login failed');
    }
  },
  register: async (userData) => {
    try {
      const response = await api.post('/auth/register/student', userData);
      return response.data;
    } catch (error) {
      handleApiError(error, 'Registration failed');
    }
  },
  checkAvailability: async (identifier) => {
    try {
      const response = await api.get(`/auth/register/check-availability?identifier=${identifier}`);
      return response.data;
    } catch (error) {
      handleApiError(error, 'Failed to check availability');
    }
  },
  requestPasswordReset: async (email) => {
    try {
      const response = await api.post('/auth/password/reset-request', { email });
      return response.data;
    } catch (error) {
      handleApiError(error, 'Failed to request password reset');
    }
  },
  resetPassword: async ({ token, new_password }) => {
    try {
      const response = await api.post('/auth/password/reset', { token, new_password });
      return response.data;
    } catch (error) {
      handleApiError(error, 'Failed to reset password');
    }
  },
  getMe: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      handleApiError(error, 'Failed to fetch user profile');
    }
  },
  logout: async (refresh_token) => {
    try {
      const response = await api.post('/auth/logout', { refresh_token });
      return response.data;
    } catch (error) {
      handleApiError(error, 'Logout failed');
    }
  },
  verifyEmail: async (token) => {
    try {
      const response = await api.post(`/auth/verify-email?token=${token}`);
      return response.data;
    } catch (error) {
      handleApiError(error, 'Email verification failed');
    }
  },
  updateProfile: async (data) => {
    try {
      const response = await api.put('/auth/profile', data);
      return response.data;
    } catch (error) {
      handleApiError(error, 'Profile update failed');
    }
  },
  uploadAvatar: async (file) => {
    try {
      return await fileService.uploadSingle('/auth/profile/avatar', file);
    } catch (error) {
      handleApiError(error, 'Avatar upload failed');
    }
  },
  getDepartments: async () => {
    try {
      const response = await api.get('/auth/departments');
      return response.data;
    } catch (error) {
      handleApiError(error, 'Failed to fetch departments');
    }
  },
  refreshToken: async (refresh_token) => {
    try {
      const response = await api.post('/auth/refresh-token', { refresh_token });
      return response.data;
    } catch (error) {
      handleApiError(error, 'Token refresh failed');
    }
  },
};
