import { Link } from "react-router-dom";
import { 
    PiUsersThin, 
    PiBriefcaseThin, 
    PiBuildingsThin, 
    PiCheckCircleThin,
    PiClockThin,
    PiChartBarThin
} from "react-icons/pi";
import { useAdminDashboard } from "../../hooks/useAdminDashboard";
import { useAuth } from "../../hooks/useAuth";

function AdminDashboard() {
    const { user } = useAuth();
    
    const {
        pendingApplications,
        loadingApps,
        companies,
        students,
        vacancyStats,
        applicationStats,
        distribution
    } = useAdminDashboard();

    const stats = [
        { 
            label: "Verifikasi Tertunda", 
            value: pendingApplications?.length || 0, 
            icon: PiClockThin, 
            color: "text-amber-600",
            bg: "bg-amber-50" 
        },
        { 
            label: "Total Perusahaan", 
            value: companies?.length || 0, 
            icon: PiBuildingsThin, 
            color: "text-sky-600",
            bg: "bg-sky-50" 
        },
        { 
            label: "Lowongan Aktif", 
            value: vacancyStats?.total_active_vacancies ?? 0, 
            icon: PiBriefcaseThin, 
            color: "text-emerald-600",
            bg: "bg-emerald-50" 
        },
        { 
            label: "Total Mahasiswa", 
            value: students?.length || 0, 
            icon: PiUsersThin, 
            color: "text-indigo-600",
            bg: "bg-indigo-50" 
        },
        {
            label: "Conversion Rate",
            value: applicationStats?.conversion_rate != null ? `${Math.round(applicationStats.conversion_rate)}%` : "0%",
            icon: PiChartBarThin,
            color: "text-violet-600",
            bg: "bg-violet-50"
        }
    ];

    return (
        <div className="font-jakarta space-y-8">
            {/* Header / Welcome Area */}
            <div className="bg-sky-950 py-8 px-5 sm:py-10 sm:px-10 rounded-[1.5rem] sm:rounded-[2.5rem] text-white shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                    <h1 className="text-2xl sm:text-3xl font-bold mb-2">Panel Administrator CDA</h1>
                    <p className="text-sky-200 max-w-xl">
                        Selamat datang kembali, {user?.full_name || 'Admin'}. Kelola data master, verifikasi dokumen, dan pantau aktivitas karir mahasiswa IPB di sini.
                    </p>
                </div>
                {/* Decorative background element */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-20 -mt-20 blur-3xl"></div>
            </div>

            {/* Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-6">
                {stats.map((stat, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-5 transition-all hover:shadow-md">
                        <div className={`${stat.bg} ${stat.color} p-4 rounded-xl`}>
                            <stat.icon size={28} weight="thin" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                            <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Main Content Areas */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Verification Queue Preview */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden text-sm">
                    <div className="p-5 sm:p-6 border-b border-slate-50 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
                        <h2 className="font-bold text-slate-900 text-lg">Verifikasi Perlu Tindakan</h2>
                        <Link to="/app/admin/verifikasi" className="text-sky-700 font-bold hover:underline">Lihat Semua</Link>
                    </div>
                    <div className="divide-y divide-slate-50">
                        {loadingApps ? (
                            <div className="p-10 text-center text-slate-400">Memuat antrean...</div>
                        ) : pendingApplications?.length > 0 ? (
                            pendingApplications.slice(0, 5).map((app) => (
                                <div key={app.id} className="p-4 hover:bg-slate-50 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 transition-colors">
                                    <div className="flex gap-4 items-center">
                                        <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-600">
                                            {app.student?.user?.full_name?.charAt(0)}
                                        </div>
                                        <div>
                                            <p className="font-bold text-slate-900">{app.student?.user?.full_name}</p>
                                            <p className="text-slate-500 text-xs">{app.vacancy?.title} • {app.vacancy?.company?.name}</p>
                                        </div>
                                    </div>
                                    <span className="text-xs px-3 py-1 bg-sky-50 text-sky-700 rounded-full font-bold">
                                        {app.status}
                                    </span>
                                </div>
                            ))
                        ) : (
                            <div className="p-10 text-center text-slate-400">Tidak ada antrean verifikasi saat ini.</div>
                        )}
                    </div>
                </div>

                {/* Quick Actions / Master Data Summary */}
                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 italic text-slate-500 text-sm">
                        &ldquo;Efisienkan proses administrasi untuk mempercepat karir mahasiswa IPB.&rdquo;
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Link 
                            to="/app/admin/perusahaan"
                            className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-sky-200 hover:bg-sky-50 transition-all flex flex-col items-center gap-3"
                        >
                            <PiBuildingsThin size={32} className="text-sky-900" />
                            <span className="font-bold text-slate-900">Kelola PT</span>
                        </Link>
                        <Link 
                            to="/app/admin/verifikasi"
                            className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:border-sky-200 hover:bg-sky-50 transition-all flex flex-col items-center gap-3"
                        >
                            <PiCheckCircleThin size={32} className="text-sky-900" />
                            <span className="font-bold text-slate-900">Validasi</span>
                        </Link>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="p-6 border-b border-slate-50">
                        <h2 className="font-bold text-slate-900 text-lg">Status Lamaran</h2>
                    </div>
                    <div className="p-6 space-y-4">
                        {(applicationStats?.status_breakdown || []).length > 0 ? (
                            (() => {
                                const validItems = applicationStats.status_breakdown.filter(item => item.status.toUpperCase() !== 'WITHDRAWN');
                                const validTotal = validItems.reduce((sum, item) => sum + item.total, 0);
                                return validItems.length > 0 ? validItems.map((item) => (
                                    <div key={item.status} className="flex items-center justify-between gap-4">
                                        <span className="text-sm font-bold text-slate-600">{item.status}</span>
                                        <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-sky-700 rounded-full"
                                                style={{
                                                    width: `${validTotal > 0 ? Math.min(100, (item.total / validTotal) * 100) : 0}%`
                                                }}
                                            />
                                        </div>
                                        <span className="text-sm font-bold text-slate-900 w-8 text-right">{item.total}</span>
                                    </div>
                                )) : <div className="py-8 text-center text-slate-400 text-sm">Belum ada data lamaran.</div>;
                            })()
                        ) : (
                            <div className="py-8 text-center text-slate-400 text-sm">Belum ada data lamaran.</div>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="p-6 border-b border-slate-50">
                        <h2 className="font-bold text-slate-900 text-lg">Distribusi Penempatan</h2>
                    </div>
                    <div className="p-6 space-y-4">
                        {(distribution?.top_companies || []).length > 0 ? (
                            distribution.top_companies.slice(0, 5).map((company) => (
                                <div key={company.company_id} className="flex items-center justify-between gap-4">
                                    <div>
                                        <p className="text-sm font-bold text-slate-800">{company.company_name}</p>
                                        <p className="text-xs text-slate-400">{company.company_industry || "Industri belum diisi"}</p>
                                    </div>
                                    <span className="px-3 py-1 rounded-full bg-sky-50 text-sky-800 text-xs font-bold">
                                        {company.total_students} mahasiswa
                                    </span>
                                </div>
                            ))
                        ) : (
                            <div className="py-8 text-center text-slate-400 text-sm">Belum ada data penempatan.</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default AdminDashboard;
