import { useState } from "react";
import {
    PiMagnifyingGlassBold,
    PiIdentificationCardBold,
    PiGraduationCapBold,
    PiToggleLeftFill,
    PiToggleRightFill,
    PiEnvelopeBold,
    PiEyeBold,
    PiXCircleFill,
    PiLinkedinLogoFill,
    PiFilePdfBold,
    PiPhoneBold,
    PiCalendarBlankBold,
    PiBriefcaseBold,
    PiCaretDown,
    PiClockThin
} from "react-icons/pi";
import { useAdminUsers } from "../../hooks/useAdminUsers";
import ConfirmModal from "../../components/ConfirmModal";
import { resolveBackendAssetUrl } from "../../utils/assetUrl";

function AdminUsers() {
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [studentToToggle, setStudentToToggle] = useState(null);

    const [sortBy, setSortBy] = useState("last_login"); // "last_login" or "name"
    const [deptFilter, setDeptFilter] = useState("all");

    const {
        students,
        isLoadingStudents: isLoading,
        departments,
        toggleActiveMutation
    } = useAdminUsers();

    const handleToggleClick = (student) => {
        setStudentToToggle(student);
        setIsConfirmOpen(true);
    };

    const confirmToggle = () => {
        if (studentToToggle) toggleActiveMutation.mutate(studentToToggle.id);
    };

    const viewDetail = (student) => {
        setSelectedStudent(student);
        setIsDetailOpen(true);
    };

    const filteredStudents = students?.filter(s => {
        const matchesSearch =
            s.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            s.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            s.nim?.includes(searchTerm);

        const matchesDept = deptFilter === "all" || s.department_id === deptFilter;
        // Backend now filters role=STUDENT, but we keep a safe check
        const isStudent = !s.role || s.role.toUpperCase() === "STUDENT";

        return matchesSearch && matchesDept && isStudent;
    }).sort((a, b) => {
        if (sortBy === "last_login") {
            return new Date(b.last_login_at || 0) - new Date(a.last_login_at || 0);
        }
        return (a.full_name || "").localeCompare(b.full_name || "");
    });

    const [isDeptOpen, setIsDeptOpen] = useState(false);

    return (
        <div className="font-jakarta space-y-8 pb-20">
            {/* Header Banner */}
            <div className="bg-sky-950 py-8 px-5 sm:py-12 sm:px-10 rounded-[1.5rem] sm:rounded-[2.5rem] text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                    <h1 className="text-2xl sm:text-3xl font-extrabold mb-2 tracking-tight">Manajemen Mahasiswa</h1>
                    <p className="text-sky-200 max-w-xl text-sm sm:text-lg opacity-80 font-medium">
                        Pantau aktivitas akademik, verifikasi data profil, dan kelola aksesibilitas akun mahasiswa IPB.
                    </p>
                </div>
                <div className="absolute top-0 right-0 w-80 h-80 bg-white/5 rounded-full -mr-24 -mt-24 blur-3xl"></div>
            </div>

            {/* Toolbar */}
            <div className="flex flex-col xl:flex-row gap-6 items-center justify-between bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div className="flex flex-col md:flex-row gap-4 w-full xl:w-auto">
                    <div className="relative w-full md:w-80 group">
                        <PiMagnifyingGlassBold className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-sky-600 transition-colors" />
                        <input
                            type="text"
                            placeholder="Cari nama, NIM, atau email..."
                            className="w-full pl-12 pr-4 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl text-sm focus:ring-4 focus:ring-sky-500/10 focus:border-sky-500 outline-none transition-all font-medium"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <div className="relative w-full md:w-64">
                        <button
                            onClick={() => setIsDeptOpen(!isDeptOpen)}
                            className="w-full pl-4 pr-10 py-3.5 bg-slate-50 border border-slate-100 rounded-2xl text-sm focus:ring-4 focus:ring-sky-500/10 outline-none transition-all font-bold text-left flex items-center justify-between"
                        >
                            <span className="truncate">{deptFilter === "all" ? "Semua Departemen" : departments?.find(d => d.id === deptFilter)?.name || "Semua Departemen"}</span>
                            <PiCaretDown size={18} className={`text-slate-400 transition-transform ${isDeptOpen ? 'rotate-180' : ''}`} />
                        </button>
                        {isDeptOpen && (
                            <>
                                <div className="fixed inset-0 z-40" onClick={() => setIsDeptOpen(false)}></div>
                                <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-100 rounded-2xl shadow-xl z-50 max-h-64 overflow-y-auto">
                                    <button
                                        onClick={() => { setDeptFilter("all"); setIsDeptOpen(false); }}
                                        className={`w-full text-left px-4 py-3 text-sm transition-colors ${deptFilter === "all" ? "bg-sky-50 font-bold text-sky-900" : "hover:bg-slate-50 font-medium text-slate-700"}`}
                                    >
                                        Semua Departemen
                                    </button>
                                    {departments?.map(d => (
                                        <button
                                            key={d.id}
                                            onClick={() => { setDeptFilter(d.id); setIsDeptOpen(false); }}
                                            className={`w-full text-left px-4 py-3 text-sm transition-colors border-t border-slate-50 ${deptFilter === d.id ? "bg-sky-50 font-bold text-sky-900" : "hover:bg-slate-50 font-medium text-slate-700"}`}
                                        >
                                            {d.name}
                                        </button>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>
                </div>

                <div className="flex bg-slate-50 p-1.5 rounded-2xl border border-slate-100 w-full xl:w-auto">
                    {[
                        { id: "last_login", label: "Login Terakhir" },
                        { id: "name", label: "Nama (A-Z)" }
                    ].map(sort => (
                        <button
                            key={sort.id}
                            onClick={() => setSortBy(sort.id)}
                            className={`flex-1 md:flex-none px-6 py-2.5 rounded-xl text-xs font-extrabold transition-all ${sortBy === sort.id ? 'bg-white text-sky-950 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-sky-900'}`}
                        >
                            {sort.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Students Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[920px] text-left border-collapse">
                        <thead className="bg-slate-50/50 border-b border-slate-100">
                            <tr>
                                <th className="px-8 py-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-[0.2em]">Mahasiswa</th>
                                <th className="px-8 py-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-[0.2em]">Akademik</th>
                                <th className="px-8 py-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-[0.2em]">Aktivitas</th>
                                <th className="px-8 py-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-[0.2em]">Status</th>
                                <th className="px-8 py-5 text-[10px] font-extrabold text-slate-400 uppercase tracking-[0.2em] text-right">Aksi</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {isLoading ? (
                                <tr>
                                    <td colSpan="4" className="px-8 py-32 text-center text-slate-400 italic">Memuat data basis mahasiswa...</td>
                                </tr>
                            ) : filteredStudents?.length > 0 ? (
                                filteredStudents.map((student) => (
                                    <tr key={student.id} className="hover:bg-slate-50/50 transition-colors group">
                                        <td className="px-8 py-6">
                                            <div className="flex items-center gap-5">
                                                <div className="w-12 h-12 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center font-extrabold shadow-inner group-hover:scale-110 transition-transform">
                                                    {student.full_name?.charAt(0)}
                                                </div>
                                                <div>
                                                    <p className="font-extrabold text-slate-900 leading-tight text-base tracking-tight">{student.full_name}</p>
                                                    <p className="text-xs text-slate-500 font-bold mt-0.5">{student.email}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-8 py-6">
                                            <div className="space-y-1.5">
                                                <div className="flex items-center gap-2 text-xs font-extrabold text-slate-700">
                                                    <PiGraduationCapBold className="text-sky-600" size={16} />
                                                    <span>{student.department_name || 'Departemen Belum Diatur'}</span>
                                                </div>
                                                <div className="flex items-center gap-3">
                                                    <span className="text-[10px] text-slate-400 font-extrabold uppercase tracking-widest">NIM: {student.nim || '-'}</span>
                                                    <div className="w-1 h-1 rounded-full bg-slate-300"></div>
                                                    <span className="text-[10px] text-sky-700 font-extrabold uppercase bg-sky-50 px-2 py-0.5 rounded">Semester {student.semester || '-'}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-8 py-6">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-2 text-xs font-bold text-slate-600">
                                                    <PiClockThin className="text-sky-500" size={16} />
                                                    <span>{student.last_login_at ? new Date(student.last_login_at).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : 'Belum pernah login'}</span>
                                                </div>
                                                <span className="text-[10px] text-slate-400 font-medium">Terdaftar: {new Date(student.created_at).toLocaleDateString('id-ID')}</span>
                                            </div>
                                        </td>
                                        <td className="px-8 py-6">
                                            <span className={`px-4 py-1.5 rounded-xl text-[10px] font-extrabold uppercase tracking-[0.15em] border ${student.is_active
                                                    ? 'bg-emerald-50 text-emerald-600 border-emerald-100'
                                                    : 'bg-red-50 text-red-600 border-red-100'
                                                }`}>
                                                {student.is_active ? 'Aktif' : 'Nonaktif'}
                                            </span>
                                        </td>
                                        <td className="px-8 py-6 text-right">
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    onClick={() => viewDetail(student)}
                                                    className="p-3 text-slate-400 hover:text-sky-600 hover:bg-sky-50 rounded-xl transition-all shadow-sm border border-transparent hover:border-sky-100"
                                                    title="Lihat Profil Lengkap"
                                                >
                                                    <PiEyeBold size={24} />
                                                </button>
                                                <button
                                                    onClick={() => handleToggleClick(student)}
                                                    className={`p-2 transition-all ${student.is_active ? 'text-emerald-600 hover:text-emerald-700' : 'text-slate-300 hover:text-slate-400'}`}
                                                    title={student.is_active ? 'Nonaktifkan Akun' : 'Aktifkan Akun'}
                                                >
                                                    {student.is_active ? <PiToggleRightFill size={36} /> : <PiToggleLeftFill size={36} />}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="4" className="px-8 py-32 text-center text-slate-400 italic">Tidak ada mahasiswa yang ditemukan.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Student Detail Modal */}
            {isDetailOpen && selectedStudent && (
                <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4">
                    <div className="absolute inset-0 bg-sky-950/60 backdrop-blur-md" onClick={() => setIsDetailOpen(false)}></div>
                    <div className="relative bg-white rounded-t-[2rem] sm:rounded-[2.5rem] shadow-2xl w-full max-w-2xl max-h-[92dvh] sm:max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-300">
                        {/* Modal Cover */}
                        <div className="h-32 bg-sky-950 relative shrink-0">
                            <div className="absolute -bottom-12 left-5 sm:left-10 w-24 h-24 rounded-[2rem] bg-white p-2 shadow-xl">
                                <div className="w-full h-full rounded-[1.5rem] bg-sky-100 text-sky-700 flex items-center justify-center text-3xl font-extrabold">
                                    {selectedStudent.full_name?.charAt(0)}
                                </div>
                            </div>
                            <button onClick={() => setIsDetailOpen(false)} className="absolute top-6 right-6 p-2 bg-white/10 hover:bg-white/20 rounded-xl text-white transition-all">
                                <PiXCircleFill size={32} />
                            </button>
                        </div>

                        {/* Modal Body */}
                        <div className="pt-24 p-5 sm:p-10 overflow-y-auto space-y-8 sm:space-y-10">
                            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-5">
                                <div>
                                    <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">{selectedStudent.full_name}</h2>
                                    <p className="text-sky-600 font-bold flex items-center gap-2 mt-1">
                                        <PiIdentificationCardBold /> {selectedStudent.nim || 'NIM Tidak Tersedia'}
                                    </p>
                                </div>
                                <div className="sm:text-right">
                                    <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest">Akademik GPA</p>
                                    <p className="text-3xl font-black text-sky-950">{selectedStudent.gpa?.toFixed(2) || '0.00'}</p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                                <div className="space-y-6">
                                    <div className="space-y-3">
                                        <h4 className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                            <PiEnvelopeBold size={14} className="text-sky-600" /> Kontak & Informasi
                                        </h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex items-center gap-3 text-slate-600">
                                                <PiPhoneBold className="text-slate-400" />
                                                <span>{selectedStudent.phone_number || 'Tidak ada telepon'}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-slate-600">
                                                <PiCalendarBlankBold className="text-slate-400" />
                                                <span>Bergabung {new Date(selectedStudent.created_at).toLocaleDateString('id-ID')}</span>
                                            </div>
                                            <div className="flex items-center gap-3 text-slate-600">
                                                <PiClockThin className="text-slate-400" />
                                                <span className="font-bold">Login Terakhir: {selectedStudent.last_login_at ? new Date(selectedStudent.last_login_at).toLocaleString('id-ID') : 'Belum pernah login'}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-3">
                                        <h4 className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                                            <PiBriefcaseBold size={14} className="text-sky-600" /> Akademik
                                        </h4>
                                        <div className="space-y-2 text-sm">
                                            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                                <p className="text-[10px] font-extrabold text-sky-800 uppercase mb-1">
                                                    {selectedStudent.department_name ? `Departemen ${selectedStudent.department_name}` : 'Departemen Belum Diatur'}
                                                </p>
                                                <p className="text-slate-600 font-bold leading-snug">Semester {selectedStudent.semester || 'Belum Diatur'}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div className="space-y-3">
                                        <h4 className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest">Tautan</h4>
                                        <div className="flex flex-col gap-3">
                                            <a
                                                href={selectedStudent.linkedin_url || "#"}
                                                target="_blank"
                                                onClick={(e) => { if (!selectedStudent.linkedin_url) { e.preventDefault(); toast.error("LinkedIn belum ditambahkan oleh mahasiswa."); } }}
                                                className="flex items-center justify-between p-4 rounded-2xl border transition-all bg-sky-50 border-sky-100 text-sky-700 hover:bg-sky-100 cursor-pointer" rel="noreferrer"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <PiLinkedinLogoFill size={20} />
                                                    <span className="text-sm font-bold">LinkedIn Profile</span>
                                                </div>
                                            </a>
                                            <a
                                                href={selectedStudent.cv_url ? resolveBackendAssetUrl(selectedStudent.cv_url) : "#"}
                                                target="_blank"
                                                onClick={(e) => { if (!selectedStudent.cv_url) { e.preventDefault(); toast.error("CV belum diunggah oleh mahasiswa."); } }}
                                                className="flex items-center justify-between p-4 rounded-2xl border transition-all bg-indigo-50 border-indigo-100 text-indigo-700 hover:bg-indigo-100 cursor-pointer" rel="noreferrer"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <PiFilePdfBold size={20} />
                                                    <span className="text-sm font-bold">Download CV</span>
                                                </div>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div className="p-4 sm:p-8 bg-slate-50 border-t border-slate-100">
                            <button
                                onClick={() => setIsDetailOpen(false)}
                                className="w-full py-4 bg-sky-950 text-white rounded-2xl font-extrabold shadow-xl shadow-sky-900/20"
                            >
                                Tutup Detail
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <ConfirmModal
                isOpen={isConfirmOpen}
                onClose={() => setIsConfirmOpen(false)}
                onConfirm={confirmToggle}
                title={studentToToggle?.is_active ? "Nonaktifkan Akun?" : "Aktifkan Akun?"}
                message={`Anda akan mengubah status akses untuk "${studentToToggle?.full_name}". Akun yang nonaktif tidak dapat masuk ke dalam platform.`}
                confirmText="Lanjutkan"
                type={studentToToggle?.is_active ? "danger" : "default"}
            />
        </div>
    );
}

export default AdminUsers;
