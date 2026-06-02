import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import applicationService from '../services/applicationService';

/**
 * Hook Custom untuk Query dan Mutasi lamaran pekerjaan menggunakan TanStack Query
 */
export const useApplications = ({ enabled } = {}) => {
  const queryClient = useQueryClient();
  const hasAccessToken = Boolean(localStorage.getItem('token'));
  const shouldFetchApplications = enabled ?? hasAccessToken;

  // 1. Query untuk mengambil daftar lamaran milik Student saat ini
  const { 
    data: applications = [], 
    isLoading, 
    isError, 
    error,
    refetch 
  } = useQuery({
    queryKey: ['applications', 'my'],
    queryFn: applicationService.getMyApplications,
    enabled: shouldFetchApplications,
    staleTime: 5 * 60 * 1000, // Waktu stale 5 menit
    refetchOnWindowFocus: true,
  });

  // 2. Mutasi untuk memperbarui status lamaran: misalnya membatalkan atau menerima tawaran
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, data }) => applicationService.updateStatus(id, data),
    onSuccess: (updatedApp) => {
      // Batalkan validasi daftar lamaran untuk memicu refresh otomatis
      queryClient.invalidateQueries({ queryKey: ['applications', 'my'] });
      // Batalkan validasi riwayat audit lamaran yang spesifik
      queryClient.invalidateQueries({ queryKey: ['applications', updatedApp.id, 'history'] });
    },
  });

  // 3. Mutasi untuk mengunggah bukti penerimaan: Letter of Acceptance atau LoA
  const uploadProofMutation = useMutation({
    mutationFn: ({ id, file }) => applicationService.uploadProof(id, file),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['applications', 'my'] });
      queryClient.invalidateQueries({ queryKey: ['applications', variables.id, 'history'] });
    },
  });

  const applyMutation = useMutation({
    mutationFn: (data) => applicationService.apply(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications', 'my'] });
    },
  });

  const replyNotesMutation = useMutation({
    mutationFn: ({ id, reply }) => applicationService.replyNotes(id, reply),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications', 'my'] });
    },
  });

  return {
    applications,
    isLoading,
    isError,
    error,
    refetch,
    updateStatus: updateStatusMutation.mutateAsync,
    isUpdatingStatus: updateStatusMutation.isPending,
    uploadProof: uploadProofMutation.mutateAsync,
    isUploadingProof: uploadProofMutation.isPending,
    apply: applyMutation.mutateAsync,
    isApplying: applyMutation.isPending,
    replyNotes: replyNotesMutation.mutateAsync,
    isReplyingNotes: replyNotesMutation.isPending,
  };
};

/**
 * Hook Custom untuk mengambil riwayat atau audit trail dari lamaran spesifik
 * @param {string} applicationId: ID lamaran untuk mengambil riwayat
 */
export const useApplicationHistory = (applicationId) => {
  return useQuery({
    queryKey: ['applications', applicationId, 'history'],
    queryFn: () => applicationService.getHistory(applicationId),
    enabled: !!applicationId,
    staleTime: 60 * 1000, // Waktu stale 1 menit
    refetchOnWindowFocus: false,
  });
};
