import api from '../api/axios';
import { fileService } from './fileService';

export const applicationService = {
  /**
   * Inisialisasi lamaran pekerjaan baru
   * @param {Object} data: Data Application
   */
  apply: async (data) => {
    const response = await api.post('/applications', data);
    return response.data;
  },

  /**
   * Perbarui status lamaran: misalnya menjadi REJECTED atau ACCEPTED setelah LoA
   * @param {string} applicationId
   * @param {Object} data: Objek data berisi status
   */
  updateStatus: async (applicationId, data) => {
    const response = await api.patch(`/applications/${applicationId}/status`, data);
    return response.data;
  },

  /**
   * Upload bukti penerimaan: Screenshot LoA
   * @param {string} applicationId
   * @param {File} file
   */
  uploadProof: async (applicationId, file) => {
    return await fileService.uploadSingle(`/applications/${applicationId}/proof`, file);
  },

  /**
   * Ambil log audit atau riwayat untuk Application tertentu
   * @param {string} applicationId
   */
  getHistory: async (applicationId) => {
    const response = await api.get(`/applications/${applicationId}/history`);
    return response.data;
  },

  /**
   * Ambil semua lamaran untuk Student saat ini
   */
  getMyApplications: async () => {
    const response = await api.get('/applications/my');
    return response.data;
  },

  replyNotes: async (applicationId, reply) => {
    const response = await api.patch(`/applications/${applicationId}/reply`, { student_reply: reply });
    return response.data;
  },
};

export default applicationService;
