import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import adminService from "../services/adminService";
import toast from "react-hot-toast";

export function useAdminVerification(onSuccessAction) {
    const queryClient = useQueryClient();

    const pendingVerificationsQuery = useQuery({
        queryKey: ["admin", "pending-verifications"],
        queryFn: adminService.getPendingVerifications
    });

    const verifyMutation = useMutation({
        mutationFn: ({ id, data }) => adminService.verifyApplication(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries(["admin", "pending-verifications"]);
            if (onSuccessAction) onSuccessAction();
            toast.success("Lamaran berhasil disetujui");
        }
    });

    const rejectMutation = useMutation({
        mutationFn: ({ id, data }) => adminService.rejectApplication(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries(["admin", "pending-verifications"]);
            if (onSuccessAction) onSuccessAction();
            toast.success("Lamaran berhasil ditolak");
        }
    });

    const addNotesMutation = useMutation({
        mutationFn: ({ id, notes }) => adminService.addAdminNotes(id, notes),
        onSuccess: () => {
            queryClient.invalidateQueries(["admin", "pending-verifications"]);
            toast.success("Catatan permintaan data berhasil dikirim");
        }
    });

    return {
        applications: pendingVerificationsQuery.data || [],
        isLoadingApplications: pendingVerificationsQuery.isLoading,
        verifyMutation,
        rejectMutation,
        addNotesMutation
    };
}
