import { useState } from "react";
import {
    PiCheckCircleFill, 
    PiXCircleFill, 
    PiFilePdfFill,
    PiEyeFill,
    PiClockFill
} from "react-icons/pi";
import { useAdminVerification } from "../../hooks/useAdminVerification";
import { resolveBackendAssetUrl } from "../../utils/assetUrl";

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

    const handleVerify = (id) => {
        if (!startDate || !endDate) {
            alert("Harap isi tanggal mulai dan tanggal selesai penempatan.");
            return;
        }
        verifyMutation.mutate({ id, data: { start_date: startDate, end_date: endDate } });
    };

    const handleReject = (id) => {
        if (!remarks) {
            alert("Harap isi alasan penolakan pada catatan.");
            return;
        }
        rejectMutation.mutate({ id, data: { reason: remarks } });
    };

    return (
        <div className="font-jakarta space-y-8 pb-20">
            {/* Header Banner */}
            <div className="bg-sky-950 py-8 px-5 sm:py-12 sm:px-10 rounded-[1.5rem] sm:rounded-[2.5rem] text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                    <h1 className="text-2xl sm:text-3xl font-extrabold mb-2 tracking-tight">Verifikasi Lamaran</h1>
                    <p className="text-sky-200 max-w-xl text-sm sm:text-lg opacity-80 font-medium leading-relaxed">
                        Tinjau dokumen pendukung dan syarat lamaran mahasiswa. Pastikan semua data valid sebelum menyetujui penempatan magang.
                    </p>
                    <div className="mt-6 sm:mt-8 inline-flex bg-white/10 backdrop-blur-md px-4 sm:px-6 py-3 rounded-2xl text-sm font-bold items-center gap-3 border border-white/10 shadow-lg shadow-sky-900/20">
                        <PiClockFill className="text-amber-400" size={20} />
                        <span>{applications?.length || 0} Perlu Diverifikasi</span>
                    </div>
                </div>
                <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -mr-32 -mt-32 blur-[100px]"></div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* List Area */}
                <div className={`lg:col-span-2 space-y-4 ${selectedApp ? 'hidden lg:block' : 'block'}`}>
                    {isLoading ? (
                        <div className="p-10 text-center text-slate-400 bg-white rounded-2xl border border-slate-100 italic">
                            Memuat daftar lamaran...
                        </div>
                    ) : applications?.length > 0 ? (
                        applications.map((app) => (
                            <div 
                                key={app.id} 
                                onClick={() => setSelectedApp(app)}
                                className={`p-4 sm:p-5 bg-white rounded-2xl border transition-all cursor-pointer flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 ${
                                    selectedApp?.id === app.id ? 'border-sky-500 shadow-md ring-1 ring-sky-500/20' : 'border-slate-100 hover:border-sky-200 shadow-sm'
                                }`}
                            >
                                <div className="flex gap-4 w-full min-w-0">
                                    <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-700 flex items-center justify-center font-bold text-lg">
                                        {app.student?.user?.full_name?.charAt(0)}
                                    </div>
                                    <div className="min-w-0">
                                        <h3 className="font-bold text-slate-900 truncate flex items-center gap-2">
                                            {app.student?.user?.full_name}
                                            {app.status === 'APPLIED' && <span className="text-[9px] px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">Minta Didaftarkan</span>}
                                            {app.status === 'ACCEPTED' && <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">Butuh Validasi</span>}
                                        </h3>
                                        <p className="text-slate-500 text-xs">{app.vacancy?.title} • {app.vacancy?.company?.name}</p>
                                        <div className="mt-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                            Diunggah: {new Date(app.created_at).toLocaleDateString('id-ID')}
                                        </div>
                                    </div>
                                </div>
                                <PiEyeFill size={20} className={`${selectedApp?.id === app.id ? 'text-sky-500' : 'text-slate-300'} self-end sm:self-auto`} />
                            </div>
                        ))
                    ) : (
                        <div className="p-10 text-center text-slate-400 bg-white rounded-2xl border border-slate-100 italic">
                            Belum ada lamaran yang perlu diverifikasi.
                        </div>
                    )}
                </div>

                {/* Detail/Action Area */}
                <div className={`lg:col-span-1 ${selectedApp ? 'block' : 'hidden lg:block'}`}>
                    {selectedApp ? (
                        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 sm:p-6 lg:sticky lg:top-6 space-y-6">
                            <div className="flex items-center justify-between border-b pb-4">
                                <h2 className="font-bold text-slate-900 text-lg">Dokumen Pendukung</h2>
                                <button 
                                    onClick={() => setSelectedApp(null)}
                                    className="lg:hidden text-xs text-sky-700 font-extrabold hover:underline flex items-center gap-1"
                                >
                                    ← Kembali
                                </button>
                            </div>
                            
                            <div className="space-y-3">
                                <a 
                                    href={resolveBackendAssetUrl(selectedApp.cv_url)} 
                                    target="_blank" 
                                    rel="noreferrer"
                                    className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors group"
                                >
                                    <PiFilePdfFill className="text-red-500" size={24} />
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-slate-900">Curriculum Vitae</p>
                                        <p className="text-[10px] text-slate-500 uppercase">Klik untuk pratinjau</p>
                                    </div>
                                </a>
                                {selectedApp.portfolio_url && (
                                    <a 
                                        href={resolveBackendAssetUrl(selectedApp.portfolio_url)} 
                                        target="_blank" 
                                        rel="noreferrer"
                                        className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors group"
                                    >
                                        <PiFilePdfFill className="text-sky-500" size={24} />
                                        <div className="flex-1">
                                            <p className="text-sm font-bold text-slate-900">Portfolio</p>
                                            <p className="text-[10px] text-slate-500 uppercase tracking-widest">Klik untuk pratinjau</p>
                                        </div>
                                    </a>
                                )}
                                {selectedApp.proof_url && (
                                    <a
                                        href={resolveBackendAssetUrl(selectedApp.proof_url)}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="flex items-center gap-3 p-3 rounded-xl bg-emerald-50 hover:bg-emerald-100 transition-colors group border border-emerald-100"
                                    >
                                        <PiFilePdfFill className="text-emerald-600" size={24} />
                                        <div className="flex-1">
                                            <p className="text-sm font-bold text-slate-900">Bukti LoA / Penerimaan</p>
                                            <p className="text-[10px] text-slate-500 uppercase">Klik untuk pratinjau</p>
                                        </div>
                                    </a>
                                )}
                            </div>

                            {selectedApp.status === 'ACCEPTED' ? (
                                <>
                                    <div className="space-y-3">
                                        <label className="text-xs font-bold text-slate-500 uppercase">Periode Penempatan</label>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                            <div>
                                                <span className="text-[10px] font-bold text-slate-400 uppercase">Mulai</span>
                                                <input
                                                    type="date"
                                                    value={startDate}
                                                    onChange={(e) => setStartDate(e.target.value)}
                                                    className="mt-1 w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-sky-500 outline-none"
                                                />
                                            </div>
                                            <div>
                                                <span className="text-[10px] font-bold text-slate-400 uppercase">Selesai</span>
                                                <input
                                                    type="date"
                                                    value={endDate}
                                                    min={startDate || undefined}
                                                    onChange={(e) => setEndDate(e.target.value)}
                                                    className="mt-1 w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-sky-500 outline-none"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <label className="text-xs font-bold text-slate-500 uppercase">Catatan Verifikasi</label>
                                        <textarea 
                                            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-sky-500 outline-none h-32"
                                            placeholder="Tambahkan catatan untuk mahasiswa..."
                                            value={remarks}
                                            onChange={(e) => setRemarks(e.target.value)}
                                        />
                                    </div>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4">
                                        <button 
                                            onClick={() => handleReject(selectedApp.id)}
                                            disabled={rejectMutation.isPending || verifyMutation.isPending}
                                            className="flex items-center justify-center gap-2 py-3 bg-white border border-red-200 text-red-600 font-bold rounded-xl hover:bg-red-50 transition-colors disabled:opacity-50"
                                        >
                                            <PiXCircleFill size={20} />
                                            Tolak
                                        </button>
                                        <button 
                                            onClick={() => handleVerify(selectedApp.id)}
                                            disabled={rejectMutation.isPending || verifyMutation.isPending}
                                            className="flex items-center justify-center gap-2 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-200 disabled:opacity-50"
                                        >
                                            <PiCheckCircleFill size={20} />
                                            Terima
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div className="p-4 bg-sky-50 rounded-xl border border-sky-100 mt-4 space-y-4">
                                    <div>
                                        <p className="text-sm font-bold text-sky-800 mb-1">Aksi Admin</p>
                                        <p className="text-xs text-sky-700 leading-relaxed">
                                            Mahasiswa ini baru saja mengajukan lamaran. Silakan gunakan <b>Curriculum Vitae</b> dan <b>Portfolio</b> di atas untuk mendaftarkan mahasiswa ke portal perusahaan secara manual.
                                        </p>
                                    </div>
                                    <div className="pt-2 border-t border-sky-200/60">
                                        <p className="text-xs font-bold text-sky-800 mb-2">Permintaan Data Tambahan</p>
                                        <textarea
                                            value={adminNotes || selectedApp.admin_notes || ""}
                                            onChange={(e) => setAdminNotes(e.target.value)}
                                            placeholder="Tulis pesan jika Anda butuh data tambahan dari mahasiswa..."
                                            className="w-full p-3 bg-white border border-sky-200 rounded-xl text-xs focus:ring-2 focus:ring-sky-500 outline-none min-h-[80px]"
                                        />
                                        <div className="mt-2 flex justify-between items-center">
                                            {selectedApp.student_reply ? (
                                                <div className="flex-1 bg-white p-3 rounded-lg border border-emerald-200 mr-3">
                                                    <span className="text-[10px] font-bold text-emerald-700 block mb-1">Balasan Mahasiswa:</span>
                                                    <p className="text-xs text-slate-700 italic">"{selectedApp.student_reply}"</p>
                                                </div>
                                            ) : (
                                                <span className="text-[10px] text-slate-400 italic">Belum ada balasan</span>
                                            )}
                                            <button 
                                                onClick={() => {
                                                    if(!adminNotes) return alert('Pesan kosong!');
                                                    addNotesMutation.mutate({ id: selectedApp.id, notes: adminNotes });
                                                }}
                                                disabled={addNotesMutation.isPending}
                                                className="px-4 py-2 bg-sky-600 text-white font-bold text-xs rounded-lg hover:bg-sky-700 transition-colors whitespace-nowrap self-end"
                                            >
                                                {addNotesMutation.isPending ? 'Mengirim...' : 'Kirim Pesan'}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="bg-slate-50 rounded-2xl border border-dashed border-slate-200 p-10 text-center text-slate-400 text-sm italic">
                            Pilih lamaran dari daftar untuk melihat detail verifikasi.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default AdminVerification;
