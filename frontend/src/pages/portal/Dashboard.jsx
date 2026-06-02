import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { usePlacements, useActivityLogs, useReportStatus } from "../../hooks/usePlacements";
import { useApplications } from "../../hooks/useApplications";
import { useJobMatches } from "../../hooks/useVacancies";
import { 
	PiBookmarkSimple, 
	PiClock, 
	PiCheckCircle,
	PiArrowRight,
	PiFolder,
	PiWarningCircle
} from "react-icons/pi";

const statusMap = {
	APPLIED: { label: "Applied", badge: "bg-sky-100 text-sky-800 border-sky-200" },
	SCREENING: { label: "Screening", badge: "bg-indigo-100 text-indigo-800 border-indigo-200" },
	INTERVIEW: { label: "Interviewing", badge: "bg-amber-100 text-amber-800 border-amber-200" },
	OFFERED: { label: "Offer Received", badge: "bg-purple-100 text-purple-800 border-purple-200" },
	ACCEPTED: { label: "Diterima", badge: "bg-emerald-100 text-emerald-800 border-emerald-200" },
	REJECTED: { label: "Rejected", badge: "bg-rose-100 text-rose-800 border-rose-200" },
	WITHDRAWN: { label: "Withdrawn", badge: "bg-zinc-100 text-zinc-600 border-zinc-200" }
};

function Dashboard() {
	const navigate = useNavigate();
	const { user } = useAuth();
	const displayName = user?.full_name || "Mahasiswa";

	// Fetch placement
	const { data: placements, isLoading: isLoadingPlacement } = usePlacements();
	const placement = placements?.[0]; // Get current active placement
	const placementId = placement?.id;

	// Fetch logs for active placement
	const { data: logs } = useActivityLogs(placementId);

	// Fetch report status for active placement
	const { data: report } = useReportStatus(placementId);

	// Fetch applications
	const { applications, isLoading: isLoadingApps } = useApplications();

	// Fetch AI/skill-based job matches (first page, 2 items)
	const { data: recommendedData, isLoading: isLoadingRecs, isError: isRecsError } = useJobMatches({ page: 1, perPage: 2 });
	const recommendedVacancies = recommendedData?.items || [];

	// Calculations
	let totalDays = 0;
	let daysPassed = 0;
	let daysRemaining = 0;
	let progressPercent = 0;

	if (placement) {
		const start = new Date(placement.start_date);
		const end = new Date(placement.end_date);
		const today = new Date();

		totalDays = Math.max(1, Math.ceil((end - start) / (1000 * 60 * 60 * 24)));
		if (today < start) {
			daysPassed = 0;
		} else if (today > end) {
			daysPassed = totalDays;
		} else {
			daysPassed = Math.ceil((today - start) / (1000 * 60 * 60 * 24));
		}
		daysRemaining = Math.max(0, totalDays - daysPassed);
		progressPercent = Math.min(100, (daysPassed / totalDays) * 100);
	}

	const logsFilled = logs?.length || 0;
	const expectedJournals = placement ? Math.max(1, Math.round(totalDays * 5 / 7)) : 0;
	const journalPercent = expectedJournals > 0 ? Math.min(100, (logsFilled / expectedJournals) * 100) : 0;

	const reportStatus = report?.status;
	const reportDone = reportStatus === "generated" ? 1 : 0;
	const reportPercent = reportDone ? 100 : 0;

	const sortedApplications = applications
		? [...applications].sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)).slice(0, 2)
		: [];

	return (
		<div className="font-jakarta pb-10">
			{/* Welcoming Banner */}
			<div className="mb-8 bg-gradient-to-r from-sky-950 to-blue-900 py-6 px-5 sm:py-8 sm:px-10 rounded-2xl text-white flex justify-between items-center shadow-lg relative overflow-hidden">
				<div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between w-full gap-4">
					<div>
						<h1 className="text-2xl sm:text-3xl font-bold">Selamat Datang Kembali, {displayName}!</h1>
						<p className="text-blue-100 text-sm mt-2">
							Pantau progres penempatan magang, kelola harian jurnal, dan temukan karir terbaikmu.
						</p>
					</div>
					{placement && (
						<NavLink 
							to="/app/jurnal"
							className="w-full sm:w-auto self-start md:self-center bg-white text-sm font-bold py-2.5 px-6 text-sky-950 rounded-xl hover:bg-sky-50 hover:scale-[1.02] transition-all shadow-md flex items-center justify-center gap-2"
						>
							Tulis Jurnal
						</NavLink>
					)}
				</div>
				<div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-20 -mt-20 blur-3xl"></div>
			</div>

			{/* Alert if not placed yet */}
			{!placement && !isLoadingPlacement && (
				<div className="mb-8 p-5 bg-amber-50 border border-amber-200 rounded-2xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
					<div className="flex items-start gap-3">
						<PiWarningCircle size={24} className="text-amber-600 shrink-0 mt-0.5" />
						<div>
							<h4 className="font-bold text-amber-900 text-sm">Belum Ada Penempatan Magang Aktif</h4>
							<p className="text-xs text-amber-700 mt-0.5">
								Anda saat ini belum terdaftar di penempatan magang aktif. Mulai ajukan lamaran atau unggah bukti penempatan mandiri Anda di halaman Lamaran.
							</p>
						</div>
					</div>
					<NavLink
						to="/app/lowongan"
						className="w-full sm:w-auto text-center bg-sky-950 text-white text-xs font-bold py-2 px-4 rounded-lg hover:bg-sky-900 transition-all shrink-0"
					>
						Cari Lowongan
					</NavLink>
				</div>
			)}

			{/* Progress Metrics Grid */}
			<div className="grid grid-cols-1 md:grid-cols-3 mb-8 gap-6">
				{/* Waktu Tersisa Card */}
				<div className="p-6 bg-white rounded-2xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.04)] border border-slate-100 flex flex-col justify-between min-h-[120px] transition-all hover:shadow-md">
					<div className="flex items-center justify-between mb-2">
						<span className="text-zinc-500 text-xs font-bold uppercase tracking-wider">Waktu Tersisa</span>
						<PiClock className="text-sky-700" size={20} />
					</div>
					<div>
						<div className="text-2xl font-bold text-slate-800">
							{placement ? `${daysRemaining} / ${totalDays} Hari` : "0 / 0 Hari"}
						</div>
						<span className="text-[10px] text-zinc-400 mt-1 block">
							{placement ? `Mulai ${new Date(placement.start_date).toLocaleDateString("id-ID")}` : "Belum ditempatkan"}
						</span>
					</div>
					<div className="bg-zinc-100 h-1.5 rounded-full mt-3 overflow-hidden">
						<div 
							className="bg-sky-700 h-full rounded-full transition-all duration-500" 
							style={{ width: `${progressPercent}%` }}
						></div>
					</div>
				</div>

				{/* Jurnal Terisi Card */}
				<div className="p-6 bg-white rounded-2xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.04)] border border-slate-100 flex flex-col justify-between min-h-[120px] transition-all hover:shadow-md">
					<div className="flex items-center justify-between mb-2">
						<span className="text-zinc-500 text-xs font-bold uppercase tracking-wider">Jurnal Terisi</span>
						<PiFolder className="text-sky-700" size={20} />
					</div>
					<div>
						<div className="text-2xl font-bold text-slate-800">
							{placement ? `${logsFilled} / ${expectedJournals}` : "0 / 0"}
						</div>
						<span className="text-[10px] text-zinc-400 mt-1 block">
							{placement ? "Berdasarkan perkiraan hari kerja" : "Magang belum berjalan"}
						</span>
					</div>
					<div className="bg-zinc-100 h-1.5 rounded-full mt-3 overflow-hidden">
						<div 
							className="bg-emerald-600 h-full rounded-full transition-all duration-500" 
							style={{ width: `${journalPercent}%` }}
						></div>
					</div>
				</div>

				{/* Laporan Diunggah Card */}
				<div className="p-6 bg-white rounded-2xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.04)] border border-slate-100 flex flex-col justify-between min-h-[120px] transition-all hover:shadow-md">
					<div className="flex items-center justify-between mb-2">
						<span className="text-zinc-500 text-xs font-bold uppercase tracking-wider">Laporan Akhir</span>
						<PiCheckCircle className="text-sky-700" size={20} />
					</div>
					<div>
						<div className="text-2xl font-bold text-slate-800">
							{placement ? `${reportDone} / 1` : "0 / 0"}
						</div>
						<span className="text-[10px] text-zinc-400 mt-1 block capitalize">
							{placement ? `Status: ${reportStatus || "Belum Dibuat"}` : "Magang belum berjalan"}
						</span>
					</div>
					<div className="bg-zinc-100 h-1.5 rounded-full mt-3 overflow-hidden">
						<div 
							className="bg-indigo-600 h-full rounded-full transition-all duration-500" 
							style={{ width: `${reportPercent}%` }}
						></div>
					</div>
				</div>
			</div>

			{/* Main Grid: Applications & Recommendations */}
			<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
				{/* Recent Applications Column */}
				<div className="lg:col-span-1 flex flex-col h-full">
					<div className="flex justify-between items-center py-3 font-bold mb-2">
						<h3 className="text-slate-800 font-bold text-base">Lamaran Terakhir</h3>
						<NavLink to="/app/lamaran" className="text-xs text-sky-800 font-bold hover:underline flex items-center gap-1">
							Selengkapnya <PiArrowRight size={12} />
						</NavLink>
					</div>

					<div className="flex-1 p-6 bg-white rounded-2xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.04)] border border-slate-100 flex flex-col gap-5 min-h-[220px]">
						{isLoadingApps ? (
							<div className="flex-1 flex flex-col justify-center items-center gap-2 py-10">
								<div className="w-8 h-8 border-4 border-slate-200 border-t-sky-950 rounded-full animate-spin"></div>
								<span className="text-xs text-zinc-400">Memuat data lamaran...</span>
							</div>
						) : sortedApplications.length > 0 ? (
							sortedApplications.map((app) => {
								let label = statusMap[app.status]?.label || app.status;
								if (app.status === "ACCEPTED") {
									const isVerified = placements?.some(p => p.application_id === app.id);
									if (!isVerified) label = "Pending Accepted";
								}
								return (
								<div key={app.id} className="flex justify-between items-start gap-3 border-b border-slate-50 last:border-0 pb-4 last:pb-0">
									<div className="text-sm">
										<h5 className="font-bold text-slate-800 line-clamp-1">{app.vacancy?.title || app.vacancy_title}</h5>
										<p className="text-zinc-500 text-xs mt-0.5 line-clamp-1">{app.vacancy?.company?.name || app.company_name}</p>
									</div>
									<div className={`px-2.5 py-1 text-center rounded-full text-[10px] font-bold border shrink-0 ${statusMap[app.status]?.badge || "bg-zinc-100 text-zinc-700 border-zinc-200"}`}>
										{label}
									</div>
								</div>
								);
							})
						) : (
							<div className="flex-1 flex flex-col justify-center items-center text-center p-6 gap-2">
								<p className="text-xs text-zinc-400">Belum ada riwayat lamaran.</p>
								<NavLink 
									to="/app/lowongan" 
									className="text-xs font-bold text-sky-800 hover:underline"
								>
									Kirim Lamaran Pertama Anda
								</NavLink>
							</div>
						)}
					</div>
				</div>

				{/* Recommendations Column */}
				<div className="lg:col-span-2 flex flex-col h-full">
					<div className="flex justify-between items-center py-3 font-bold mb-2">
						<h3 className="text-slate-800 font-bold text-base">Rekomendasi Magang</h3>
						<NavLink to="/app/lowongan" className="text-xs text-sky-800 font-bold hover:underline flex items-center gap-1">
							Selengkapnya <PiArrowRight size={12} />
						</NavLink>
					</div>

					<div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
						{isLoadingRecs ? (
							Array.from({ length: 2 }).map((_, idx) => (
								<div key={idx} className="p-6 bg-white rounded-2xl border border-slate-100 shadow-sm animate-pulse flex flex-col gap-4">
									<div className="h-4 bg-slate-200 rounded w-1/3"></div>
									<div className="h-6 bg-slate-200 rounded w-3/4 mt-2"></div>
									<div className="h-4 bg-slate-200 rounded w-1/2"></div>
									<div className="flex gap-2 mt-2">
										<div className="h-4 bg-slate-200 rounded w-12"></div>
										<div className="h-4 bg-slate-200 rounded w-12"></div>
									</div>
								</div>
							))
						) : recommendedVacancies.length > 0 ? (
							recommendedVacancies.map((item) => (
								<div 
									key={item.vacancy_id} 
									onClick={() => navigate(`/app/detail/${item.vacancy_id}`)}
									className="p-6 bg-white rounded-2xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.04)] border border-slate-100 hover:border-sky-200 hover:shadow-md cursor-pointer transition-all flex flex-col justify-between group hover:scale-[1.01]"
								>
									<div>
										<div className="flex gap-2 justify-between items-start mb-3">
											<span className="bg-sky-50 text-sky-800 text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
												{Math.round(item.match_percentage || 0)}% Match
											</span>
											<PiBookmarkSimple size={18} className="text-zinc-400 group-hover:text-sky-800 transition-colors" />
										</div>
										<h4 className="text-slate-800 text-sm font-bold group-hover:text-sky-950 transition-colors line-clamp-1">
											{item.vacancy_title}
										</h4>
										<p className="text-zinc-500 text-xs mt-0.5 line-clamp-1">
											{item.company_name}
										</p>
									</div>
									<div className="flex gap-2 mt-4">
										<div className="bg-slate-50 border border-slate-100 px-2 py-0.5 rounded text-[10px] text-zinc-600 font-bold">
											{item.total_matched_skills}/{item.total_required_skills} skill cocok
										</div>
										{item.missing_mandatory_skills?.length > 0 && (
											<div className="bg-amber-50 border border-amber-100 px-2 py-0.5 rounded text-[10px] text-amber-700 font-bold truncate max-w-[130px]">
												{item.missing_mandatory_skills.length} wajib kurang
											</div>
										)}
									</div>
								</div>
							))
						) : (
							<div className="md:col-span-2 bg-white rounded-2xl border border-slate-100 flex flex-col justify-center items-center text-center p-8 gap-2">
								<p className="text-xs text-zinc-400">
									{isRecsError ? "Unggah CV di profil untuk mengaktifkan rekomendasi." : "Tidak ada rekomendasi lowongan magang saat ini."}
								</p>
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}

export default Dashboard;
