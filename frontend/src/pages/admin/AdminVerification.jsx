import { useState } from "react";
import {
    PiCheckCircleFill, 
    PiXCircleFill, 
    PiFilePdfFill,
    PiClockFill,
    PiWarningCircle,
    PiCaretRightBold,
    PiXBold
} from "react-icons/pi";
import { useAdminVerification } from "../../hooks/useAdminVerification";
import { resolveBackendAssetUrl } from "../../utils/assetUrl";
import toast from "react-hot-toast";

const columns = [
    {
        id: "APPLIED",
        title: "Perlu Pendaftaran (APPLIED)",
        icon: <PiClockFill />,
        bgColor: "bg-sky-50/50",
        borderColor: "border-sky-100",
        headerColor: "text-sky-800",
        badgeBg: "bg-sky-100",
        badgeText: "text-sky-700"
    },
    {
        id: "ACCEPTED",
        title: "Menunggu Validasi (ACCEPTED)",
        icon: <PiCheckCircleFill />,
        bgColor: "bg-emerald-50/50",
        borderColor: "border-emerald-100",
        headerColor: "text-emerald-800",
        badgeBg: "bg-emerald-100",
        badgeText: "text-emerald-700"
    }
];

function AdminVerification() {
    const [selectedApp, setSelectedApp] = useState(null);
    const [remarks, setRemarks] = useState("");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [adminNotes, setAdminNotes] = useState("");

    const {
        applications,
        isLoadingApplications: isLoading,
        verifyMutation,
        rejectMutation,
        addNotesMutation
    } = useAdminVerification(() => {
        setSelectedApp(null);
        setRemarks("");
        setStartDate("");
        setEndDate("");
        setAdminNotes("");
    });

    const activeApp = applications?.find(a => a.id === selectedApp?.id) || selectedApp;

    const handleVerify = (id) => {
        if (!startDate || !endDate) {
            toast.error("Harap isi tanggal mulai dan tanggal selesai penempatan.");
            return;
        }
        verifyMutation.mutate({ id, data: { start_date: startDate, end_date: endDate } });
    };

    const handleReject = (id) => {
        if (!remarks) {
            toast.error("Harap isi alasan penolakan pada catatan.");
            return;
        }
        rejectMutation.mutate({ id, data: { reason: remarks } });
    };

    if (isLoading) {
        return <div className="p-10 text-center animate-pulse">Memuat data...</div>;
    }

    return (
        <div className="font-jakarta relative min-h-screen">
            {/* Header Banner */}
            <div className="mb-8 bg-sky-950 py-6 px-5 sm:py-8 sm:px-10 rounded-xl text-white flex flex-col sm:flex-row justify-between sm:items-center gap-4 shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)]">
                <div className="flex flex-col gap-2">
                    <div className="text-2xl sm:text-3xl font-bold tracking-tight">Verifikasi Lamaran</div>
                    <div className="text-sm sm:text-base text-sky-200 font-medium max-w-xl">
                        Tinjau dan proses pendaftaran mahasiswa yang berstatus Applied dan validasi LoA untuk yang berstatus Accepted.
                    </div>
                </div>
                <div className="inline-flex bg-white/10 px-4 py-2.5 rounded-lg text-sm font-bold items-center gap-2 border border-white/10 shrink-0 self-start sm:self-auto backdrop-blur-md">
                    <PiClockFill className="text-amber-400" size={18} />
                    <span>{applications?.length || 0} Menunggu</span>
                </div>
            </div>

            {/* Kanban Board */}
            <div className="flex flex-col md:flex-row gap-5 items-start">
                {columns.map((col) => {
                    const colApps = applications?.filter(app => app.status === col.id) || [];
                    return (
                        <div key={col.id} className={`flex-1 w-full flex flex-col rounded-xl border ${col.borderColor} ${col.bgColor}`}>
                            {/* Column Header */}
                            <div className="p-4 flex items-center justify-between border-b border-inherit">
                                <h2 className={`font-bold ${col.headerColor} text-sm flex items-center gap-2`}>
                                    {col.icon}
                                    {col.title}
                                </h2>
                                <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full ${col.badgeBg} ${col.badgeText}`}>
                                    {colApps.length}
                                </span>
                            </div>

                            {/* Column Items */}
                            <div className="p-3 flex flex-col gap-3 min-h-[300px]">
                                {colApps.map(app => (
                                    <div 
                                        key={app.id}
                                        onClick={() => setSelectedApp(app)}
                                        className={`bg-white p-4 rounded-xl border shadow-sm cursor-pointer hover:border-sky-300 transition-all group ${activeApp?.id === app.id ? 'border-sky-500 ring-1 ring-sky-500/20' : 'border-slate-100'}`}
                                    >
                                        <div className="flex justify-between items-start mb-3">
                                            <div className="flex flex-col gap-1">
                                                <h4 className="font-bold text-slate-800 text-sm group-hover:text-sky-700 transition-colors line-clamp-1">{app.student?.user?.full_name}</h4>
                                                <p className="text-xs text-slate-500 line-clamp-1">{app.vacancy?.title}</p>
                                                <p className="text-[10px] font-semibold text-slate-400">{app.vacancy?.company?.name}</p>
                                            </div>
                                            <div className="w-8 h-8 rounded-full bg-sky-50 text-sky-700 flex items-center justify-center font-bold text-xs shrink-0 ml-2">
                                                {app.student?.user?.full_name?.charAt(0)}
                                            </div>
                                        </div>
                                        <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-50">
                                            <span className="text-[10px] font-medium text-slate-400">
                                                {new Date(app.created_at).toLocaleDateString('id-ID')}
                                            </span>
                                            <span className="text-[10px] font-bold text-sky-600 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                                                Tinjau <PiCaretRightBold />
                                            </span>
                                        </div>
                                    </div>
                                ))}
                                {colApps.length === 0 && (
                                    <div className="py-10 text-center text-[11px] font-medium text-slate-400 italic">
                                        Tidak ada lamaran
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Sliding Drawer for Application Detail */}
            <div className={`fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm transition-opacity duration-300 ${activeApp ? "opacity-100 visible" : "opacity-0 invisible"}`} onClick={() => setSelectedApp(null)}></div>
            
            <div className={`fixed top-0 right-0 z-50 h-full w-full max-w-xl bg-white shadow-2xl transition-transform duration-300 ease-in-out transform ${activeApp ? "translate-x-0" : "translate-x-full"} flex flex-col`}>
                <div className="p-4 sm:p-5 flex items-center justify-between border-b border-gray-100 shrink-0 bg-white">
                    <h2 className="text-base font-bold text-gray-900">Detail Lamaran</h2>
                    <button 
                        onClick={() => setSelectedApp(null)}
                        className="p-2 hover:bg-gray-100 rounded-full text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <PiXBold size={18} />
                    </button>
                </div>

                <div className="overflow-y-auto flex-1 bg-slate-50/50">
                    {activeApp && (
                        <div className="p-4 sm:p-6 flex flex-col gap-6">
                            {/* Info Pekerjaan & User */}
                            <div className="bg-white p-5 rounded-xl border border-slate-200/60 shadow-sm">
                                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4">Profil Pendaftar</h3>
                                <div className="flex items-center gap-4 mb-4 pb-4 border-b border-slate-100">
                                    <div className="w-12 h-12 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-xl">
                                        {activeApp.student?.user?.full_name?.charAt(0)}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-800">{activeApp.student?.user?.full_name}</h4>
                                        <p className="text-xs text-slate-500">{activeApp.student?.nim} • {activeApp.student?.user?.email}</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <p className="text-[10px] text-gray-400 font-bold uppercase">Posisi Dilamar</p>
                                        <p className="font-semibold text-gray-800 mt-0.5">{activeApp.vacancy?.title}</p>
                                    </div>
                                    <div>
                                        <p className="text-[10px] text-gray-400 font-bold uppercase">Perusahaan</p>
                                        <p className="font-semibold text-gray-800 mt-0.5">{activeApp.vacancy?.company?.name}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Dokumen */}
                            <div className="bg-white p-5 rounded-xl border border-slate-200/60 shadow-sm">
                                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4">Dokumen Tersedia</h3>
                                <div className="space-y-3">
                                    <a 
                                        href={resolveBackendAssetUrl(activeApp.cv_url)} 
                                        target="_blank" 
                                        rel="noreferrer"
                                        className="flex items-center gap-3 p-3 rounded-lg bg-slate-50 border border-slate-100 hover:border-sky-300 hover:bg-sky-50 transition-colors group"
                                    >
                                        <PiFilePdfFill className="text-red-500" size={24} />
                                        <div className="flex-1">
                                            <p className="text-sm font-bold text-slate-900 group-hover:text-sky-800">Curriculum Vitae</p>
                                            <p className="text-[10px] text-slate-500 uppercase">Lihat Dokumen</p>
                                        </div>
                                        <PiCaretRightBold className="text-slate-300 group-hover:text-sky-500" />
                                    </a>
                                    {activeApp.proof_url && (
                                        <a 
                                            href={resolveBackendAssetUrl(activeApp.proof_url)} 
                                            target="_blank" 
                                            rel="noreferrer"
                                            className="flex items-center gap-3 p-3 rounded-lg bg-emerald-50 border border-emerald-100 hover:border-emerald-300 hover:bg-emerald-100 transition-colors group"
                                        >
                                            <PiFilePdfFill className="text-emerald-500" size={24} />
                                            <div className="flex-1">
                                                <p className="text-sm font-bold text-emerald-900">Bukti Penerimaan (LoA)</p>
                                                <p className="text-[10px] text-emerald-600 uppercase">Lihat Dokumen</p>
                                            </div>
                                            <PiCaretRightBold className="text-emerald-400 group-hover:text-emerald-600" />
                                        </a>
                                    )}
                                </div>
                            </div>

                            {/* Aksi Berdasarkan Status */}
                            {activeApp.status === "APPLIED" ? (
                                <div className="bg-white p-5 rounded-xl border border-slate-200/60 shadow-sm border-t-4 border-t-sky-400">
                                    <h3 className="text-xs font-bold text-sky-800 uppercase tracking-wider mb-4">Aksi: Permintaan Data</h3>
                                    <p className="text-xs text-slate-600 mb-4">
                                        Mahasiswa ini berstatus APPLIED. Silakan daftarkan mahasiswa ke portal perusahaan. Jika butuh data tambahan, Anda bisa mengirim pesan di bawah.
                                    </p>
                                    <textarea
                                        value={adminNotes || activeApp.admin_notes || ""}
                                        onChange={(e) => setAdminNotes(e.target.value)}
                                        placeholder="Ketik pesan untuk meminta data tambahan ke mahasiswa..."
                                        className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 outline-none min-h-[100px] mb-3"
                                    />
                                    
                                    {activeApp.student_reply && (
                                        <div className="mb-4 bg-emerald-50 border border-emerald-100 p-3 rounded-lg">
                                            <span className="text-[10px] font-bold text-emerald-700 block mb-1">Balasan Mahasiswa:</span>
                                            <p className="text-xs text-emerald-900 italic">"{activeApp.student_reply}"</p>
                                        </div>
                                    )}
                                    
                                    <div className="flex justify-end">
                                        <button 
                                            onClick={() => {
                                                if(!adminNotes) return toast.error('Pesan tidak boleh kosong!');
                                                addNotesMutation.mutate({ id: activeApp.id, notes: adminNotes });
                                            }}
                                            disabled={addNotesMutation.isPending}
                                            className="px-5 py-2 bg-sky-600 text-white font-bold text-sm rounded-lg hover:bg-sky-700 transition-colors shadow-sm"
                                        >
                                            {addNotesMutation.isPending ? 'Mengirim...' : 'Kirim Pesan'}
                                        </button>
                                    </div>
                                </div>
                            ) : activeApp.status === "ACCEPTED" ? (
                                <div className="bg-white p-5 rounded-xl border border-slate-200/60 shadow-sm border-t-4 border-t-emerald-400">
                                    <h3 className="text-xs font-bold text-emerald-800 uppercase tracking-wider mb-4">Aksi: Validasi Bukti (LoA)</h3>
                                    
                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <span className="text-[10px] font-bold text-slate-400 uppercase">Mulai Magang</span>
                                            <input
                                                type="date"
                                                value={startDate}
                                                onChange={(e) => setStartDate(e.target.value)}
                                                className="mt-1 w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                                            />
                                        </div>
                                        <div>
                                            <span className="text-[10px] font-bold text-slate-400 uppercase">Selesai Magang</span>
                                            <input
                                                type="date"
                                                value={endDate}
                                                min={startDate || undefined}
                                                onChange={(e) => setEndDate(e.target.value)}
                                                className="mt-1 w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                                            />
                                        </div>
                                    </div>

                                    <div className="mb-4">
                                        <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Catatan Verifikasi / Penolakan</span>
                                        <textarea 
                                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none h-20"
                                            placeholder="Opsional jika diterima, Wajib jika ditolak..."
                                            value={remarks}
                                            onChange={(e) => setRemarks(e.target.value)}
                                        />
                                    </div>

                                    <div className="grid grid-cols-2 gap-3">
                                        <button 
                                            onClick={() => handleReject(activeApp.id)}
                                            disabled={rejectMutation.isPending || verifyMutation.isPending}
                                            className="flex items-center justify-center gap-2 py-2.5 bg-white border border-red-200 text-red-600 font-bold text-sm rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
                                        >
                                            <PiXCircleFill size={18} /> Tolak LoA
                                        </button>
                                        <button 
                                            onClick={() => handleVerify(activeApp.id)}
                                            disabled={rejectMutation.isPending || verifyMutation.isPending}
                                            className="flex items-center justify-center gap-2 py-2.5 bg-emerald-600 text-white font-bold text-sm rounded-lg hover:bg-emerald-700 transition-colors shadow-sm disabled:opacity-50"
                                        >
                                            <PiCheckCircleFill size={18} /> Validasi Sah
                                        </button>
                                    </div>
                                </div>
                            ) : null}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AdminVerification;
