import { useState } from "react";
 
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { 
  PiClock, 
  PiHourglass, 
  PiCheckCircle, 
  PiLeaf, 
  PiBuilding, 
  PiMapPin, 
  PiFilePdf, 
  PiUploadSimple, 
  PiSpinner, 
  PiCalendarBlank,
  PiSparkle,
  PiChatCenteredText,
  PiLinkSimple,
  PiArrowRight,
  PiWarningCircle
} from "react-icons/pi";
import { useApplications, useApplicationHistory } from "../../hooks/useApplications";
import { usePlacements } from "../../hooks/usePlacements";
import { resolveBackendAssetUrl } from "../../utils/assetUrl";

// Utilitas pembantu untuk format tanggal secara rapi
const formatDate = (dateString) => {
	if (!dateString) return "-";
	const date = new Date(dateString);
	return new Intl.DateTimeFormat("id-ID", {
		day: "numeric",
		month: "long",
		year: "numeric",
		hour: "2-digit",
		minute: "2-digit"
	}).format(date);
};

// Pemetaan status enum backend ke format tampilan ramah pengguna
const statusMap = {
	APPLIED: {
		label: "Applied",
		color: "bg-sky-50 text-sky-700 border-sky-200",
		badge: "bg-sky-100 text-sky-800"
	},
	SCREENING: {
		label: "Screening",
		color: "bg-indigo-50 text-indigo-700 border-indigo-200",
		badge: "bg-indigo-100 text-indigo-800"
	},
	INTERVIEW: {
		label: "Interviewing",
		color: "bg-amber-50 text-amber-700 border-amber-200",
		badge: "bg-amber-100 text-amber-800"
	},
	OFFERED: {
		label: "Offer Received",
		color: "bg-purple-50 text-purple-700 border-purple-200",
		badge: "bg-purple-100 text-purple-800"
	},
	ACCEPTED: {
		label: "Diterima",
		color: "bg-emerald-50 text-emerald-700 border-emerald-200",
		badge: "bg-emerald-100 text-emerald-800"
	},
	REJECTED: {
		label: "Rejected",
		color: "bg-rose-50 text-rose-700 border-rose-200",
		badge: "bg-rose-100 text-rose-800"
	},
	WITHDRAWN: {
		label: "Withdrawn",
		color: "bg-zinc-100 text-zinc-600 border-zinc-200",
		badge: "bg-zinc-200 text-zinc-800"
	}
};

// Pemetaan jenis lowongan backend
const typeMap = {
	INTERNSHIP_GENERAL: "Magang Umum",
	MBKM_INTERNSHIP: "MBKM Magang",
	MBKM_STUDY_INDEPENDENT: "MBKM Studi Independen",
	FULL_TIME: "Full-Time"
};

// Kolom papan Kanban untuk pelacakan lamaran
const columns = [
	{
		id: "applied_screening",
		title: "Applied & Screening",
		statuses: ["APPLIED", "SCREENING"],
		color: "bg-slate-50 border-slate-100",
		icon: <PiClock className="text-sky-600" size={20} />
	},
	{
		id: "interview_offered",
		title: "Interview & Offered",
		statuses: ["INTERVIEW", "OFFERED"],
		color: "bg-amber-50/50 border-amber-100/50",
		icon: <PiHourglass className="text-amber-600" size={20} />
	},
	{
		id: "decided",
		title: "Outcomes",
		statuses: ["ACCEPTED", "REJECTED", "WITHDRAWN"],
		color: "bg-emerald-50/30 border-emerald-100/30",
		icon: <PiCheckCircle className="text-emerald-600" size={20} />
	}
];

function Lamaran() {
	const { 
		applications, 
		isLoading: loading, 
		isError, 
		updateStatus, 
		uploadProof,
		replyNotes,
		isReplyingNotes,
		refetch
	} = useApplications();
	const { data: placements = [] } = usePlacements();
	
	// State laci geser detail lamaran
	const [selectedApp, setSelectedApp] = useState(null);
	
	// Hook untuk query riwayat lamaran terpilih
	const { data: history = [], isLoading: loadingHistory } = useApplicationHistory(selectedApp?.id);

	// Mengambil referensi data dinamis lamaran aktif dari daftar query
	const activeApp = applications.find(a => a.id === selectedApp?.id) || selectedApp;

	// State lokal untuk form aksi lamaran
	const [isSubmittingAction, setIsSubmittingAction] = useState(false);
	const [withdrawReason, setWithdrawReason] = useState("");
	const [selectedFile, setSelectedFile] = useState(null);

	// Menangani pemilihan kartu lamaran
	const handleCardClick = (app) => {
		setSelectedApp(app);
		setWithdrawReason("");
		setSelectedFile(null);
	};

	// Menangani aksi pembatalan lamaran
	const handleWithdraw = async () => {
		if (!activeApp) return;
		try {
			setIsSubmittingAction(true);
			await updateStatus({
				id: activeApp.id,
				data: {
					status: "WITHDRAWN",
					reason: withdrawReason || "Mengundurkan diri atas permintaan sendiri"
				}
			});
			toast.success("Lamaran berhasil ditarik.");
			setWithdrawReason("");
		} catch (err) {
			console.error("Withdraw failed:", err);
			toast.error(err.response?.data?.detail || "Gagal menarik lamaran.");
		} finally {
			setIsSubmittingAction(false);
		}
	};

	// Menangani persetujuan penawaran pekerjaan
	const handleAcceptOffer = async () => {
		if (!activeApp) return;
		if (!selectedFile) {
			toast.error("Unggah bukti LoA terlebih dahulu sebelum menerima tawaran.");
			return;
		}
		try {
			setIsSubmittingAction(true);
			await uploadProof({
				id: activeApp.id,
				file: selectedFile
			});
			toast.success("Tawaran diterima dan bukti penerimaan berhasil diunggah.");
			setSelectedFile(null);
		} catch (err) {
			console.error("Accept offer failed:", err);
			toast.error(err.response?.data?.detail || err.message || "Gagal menyetujui tawaran.");
		} finally {
			setIsSubmittingAction(false);
		}
	};

	// Menangani unggah bukti penerimaan pekerjaan
	const handleUploadProof = async (e) => {
		e.preventDefault();
		if (!activeApp || !selectedFile) return;

		try {
			setIsSubmittingAction(true);
			await uploadProof({
				id: activeApp.id,
				file: selectedFile
			});
			toast.success("Bukti penerimaan berhasil diunggah! Menunggu verifikasi CDA.");
			setSelectedFile(null);
		} catch (err) {
			console.error("Proof upload failed:", err);
			toast.error(err.message || "Gagal mengunggah bukti penerimaan.");
		} finally {
			setIsSubmittingAction(false);
		}
	};

	// Render papan loading skeleton
	if (loading) {
		return (
			<div className="font-jakarta animate-pulse">
				<div className="mb-5 bg-slate-200 py-12 px-10 rounded-xl h-36"></div>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-5">
					{[1, 2, 3].map((col) => (
						<div key={col} className="p-5 bg-white border border-gray-100 rounded-xl min-h-[300px]">
							<div className="h-6 bg-slate-200 w-1/2 mb-4 rounded"></div>
							<div className="h-32 bg-slate-100 rounded-xl mb-4"></div>
							<div className="h-32 bg-slate-100 rounded-xl"></div>
						</div>
					))}
				</div>
			</div>
		);
	}

	if (isError) {
		return (
			<div className="font-jakarta flex flex-col items-center justify-center py-20 text-center">
				<div className="p-4 rounded-full bg-rose-50 border border-rose-100 text-rose-500 mb-4">
					<PiWarningCircle size={40} />
				</div>
				<h3 className="text-xl font-bold text-gray-900 mb-2">Terjadi Kesalahan</h3>
				<p className="text-gray-500 max-w-md mb-6">Gagal memuat lamaran. Pastikan server backend Anda menyala.</p>
				<button 
					onClick={() => refetch()}
					className="px-5 py-2.5 bg-sky-950 text-white rounded-lg hover:bg-sky-900 transition-colors text-sm font-semibold shadow-sm"
				>
					Coba Lagi
				</button>
			</div>
		);
	}

	return (
		<div className="font-jakarta relative min-h-screen">
			{/* Banner Utama */}
			<div className="mb-8 bg-sky-950 py-6 px-5 sm:py-8 sm:px-10 rounded-xl text-white flex flex-col sm:flex-row justify-between sm:items-center gap-4 shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)]">
				<div className="flex flex-col gap-2">
					<div className="text-2xl sm:text-3xl font-bold tracking-tight">Lacak Lamaranmu</div>
					<div className="text-sm opacity-80 font-medium">
						Pantau status lamaran magang dan karir kamu secara real-time. Kelola penawaran dan unggah bukti penerimaan dengan aman.
					</div>
				</div>
			</div>

			{/* Tampilan Papan Kanban */}
			<div className="grid grid-cols-1 xl:grid-cols-3 gap-5 items-start">
				{columns.map((column) => {
					// Filter lamaran berdasarkan daftar status kolom ini
					const colApps = applications.filter((app) => column.statuses.includes(app.status));

					return (
						<div 
							key={column.id} 
							className={`p-4 sm:p-5 bg-white border border-gray-200/60 rounded-xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.03)] flex flex-col gap-4 min-h-[280px] xl:min-h-[500px] ${column.color}`}
						>
							<div className="flex justify-between items-center border-b border-gray-100 pb-3">
								<div className="flex items-center gap-2 font-bold text-gray-900">
									{column.icon}
									<span>{column.title}</span>
								</div>
								<span className="px-2 py-0.5 bg-gray-100 text-xs font-semibold text-gray-600 rounded-full">
									{colApps.length}
								</span>
							</div>

							{colApps.length === 0 ? (
								<div className="flex flex-col items-center justify-center py-16 border-2 border-dashed border-gray-200/50 rounded-xl text-gray-400 gap-2">
									<PiLeaf size={24} className="text-gray-300 animate-pulse" />
									<span className="text-xs">Tidak ada lamaran</span>
								</div>
							) : (
								<div className="flex flex-col gap-3.5">
									{colApps.map((app) => {
										const matchedStatus = statusMap[app.status];
										const vac = app.vacancy || {};
										let label = matchedStatus.label;
										if (app.status === "ACCEPTED") {
											const isVerified = placements.some(p => p.application_id === app.id);
											if (!isVerified) label = "Pending Accepted";
										}

										return (
											<motion.div
												layoutId={`card-${app.id}`}
												key={app.id}
												onClick={() => handleCardClick(app)}
												whileHover={{ y: -3, boxShadow: "0 10px 20px -5px rgba(0,41,87,0.08)" }}
												className="p-5 bg-white rounded-xl border border-gray-200 flex flex-col gap-4 transition-all cursor-pointer group active:scale-[0.98]"
											>
												<div className="flex justify-between items-start gap-2">
													<span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${matchedStatus.badge}`}>
														{label}
													</span>
													{app.match_percentage && (
														<span className="text-[10px] bg-emerald-50 text-emerald-700 font-bold px-1.5 py-0.5 rounded-full border border-emerald-100 flex items-center gap-0.5">
															<PiSparkle /> {Math.round(app.match_percentage)}% Match
														</span>
													)}
												</div>

												<div>
													<h4 className="text-base font-bold text-gray-900 group-hover:text-sky-950 transition-colors leading-tight">
														{vac.title || "Unknown Role"}
													</h4>
													<p className="text-sm text-gray-500 font-medium mt-1 flex items-center gap-1">
														<PiBuilding size={14} className="text-gray-400" />
														{vac.company_name || "Unknown Company"}
													</p>
												</div>

												<div className="flex flex-wrap gap-2.5 pt-1 border-t border-dashed border-gray-100">
													{vac.type && (
														<span className="px-2 py-0.5 bg-gray-50 text-[10px] text-gray-600 font-semibold rounded border border-gray-200/50">
															{typeMap[vac.type] || vac.type}
														</span>
													)}
													{vac.location && (
														<span className="px-2 py-0.5 bg-gray-50 text-[10px] text-gray-600 font-semibold rounded border border-gray-200/50 flex items-center gap-0.5">
															<PiMapPin size={10} /> {vac.location}
														</span>
													)}
												</div>
											</motion.div>
										);
									})}
								</div>
							)}
						</div>
					);
				})}
			</div>

			{/* Laci Geser Detail Lamaran */}
			<AnimatePresence>
				{activeApp && (
					<>
						{/* Hamparan Latar Belakang */}
						<motion.div
							initial={{ opacity: 0 }}
							animate={{ opacity: 0.5 }}
							exit={{ opacity: 0 }}
							onClick={() => setSelectedApp(null)}
							className="fixed inset-0 bg-black z-40"
						></motion.div>

						{/* Panel Geser Kanan */}
						<motion.div
							initial={{ x: "100%" }}
							animate={{ x: 0 }}
							exit={{ x: "100%" }}
							transition={{ type: "spring", damping: 25, stiffness: 220 }}
							className="fixed inset-x-0 bottom-0 h-[92dvh] w-full rounded-t-3xl sm:inset-y-0 sm:left-auto sm:right-0 sm:h-full sm:max-w-lg sm:rounded-none bg-white shadow-2xl z-50 overflow-y-auto flex flex-col border-l border-gray-100"
						>
							{/* Bagian Kepala Header */}
							<div className="p-5 sm:p-6 bg-sky-950 text-white flex justify-between items-start relative overflow-hidden">
								<div className="absolute top-0 right-0 w-32 h-32 bg-sky-900 rounded-full translate-x-16 -translate-y-16 blur-2xl"></div>
								<div className="flex flex-col gap-1 relative z-10">
									{(() => {
										let label = statusMap[activeApp.status]?.label;
										if (activeApp.status === "ACCEPTED") {
											const isVerified = placements.some(p => p.application_id === activeApp.id);
											if (!isVerified) label = "Pending Accepted";
										}
										return (
											<span className={`self-start px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-white/20 text-white border border-white/10 mb-2`}>
												{label}
											</span>
										);
									})()}
									<h2 className="text-xl font-bold leading-tight">{activeApp.vacancy?.title}</h2>
									<p className="text-sm text-sky-200 font-medium flex items-center gap-1.5">
										<PiBuilding /> {activeApp.vacancy?.company_name}
									</p>
								</div>
								<button 
									onClick={() => setSelectedApp(null)}
									className="p-1.5 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors relative z-10"
								>
									<PiArrowRight size={18} />
								</button>
							</div>

							{/* Kontainer Konten Utama */}
							<div className="p-4 sm:p-6 flex flex-col gap-6 flex-1">
								{/* Kartu Detail Lowongan Pekerjaan */}
								<div className="p-4 bg-slate-50 border border-slate-200/60 rounded-xl flex flex-col gap-3">
									<h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Detail Pekerjaan</h3>
									<div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-700">
										<div>
											<p className="text-xs text-gray-400 font-medium">Tipe Lowongan</p>
											<p className="font-semibold text-gray-800 mt-0.5">{typeMap[activeApp.vacancy?.type] || activeApp.vacancy?.type}</p>
										</div>
										<div>
											<p className="text-xs text-gray-400 font-medium">Lokasi</p>
											<p className="font-semibold text-gray-800 mt-0.5">{activeApp.vacancy?.location || "-"}</p>
										</div>
										<div>
											<p className="text-xs text-gray-400 font-medium">Kompensasi</p>
											<p className="font-semibold text-gray-800 mt-0.5">
												{activeApp.vacancy?.payment_type === "PAID" ? "Berbayar (Paid)" : "Tidak Berbayar"}
											</p>
										</div>
										<div>
											<p className="text-xs text-gray-400 font-medium">Snapshot CV</p>
											<a 
												href={resolveBackendAssetUrl(activeApp.cv_snapshot_url)} 
												target="_blank" 
												rel="noopener noreferrer"
												className="font-semibold text-sky-600 hover:text-sky-800 underline inline-flex items-center gap-1 mt-0.5"
											>
												<PiFilePdf size={16} /> Lihat CV
											</a>
										</div>
									</div>
								</div>

								{/* Bagian Pesan Admin (Jika Ada) */}
								{activeApp.admin_notes && (
									<div className="p-4 bg-sky-50/50 border border-sky-100 rounded-xl flex flex-col gap-3">
										<h3 className="text-xs font-bold text-sky-800 uppercase tracking-wider flex items-center gap-1.5">
											<PiWarningCircle size={16} /> Pesan Admin
										</h3>
										<p className="text-xs text-sky-900 leading-relaxed bg-white/70 p-3 rounded-lg border border-sky-100">
											"{activeApp.admin_notes}"
										</p>
										
										{activeApp.student_reply ? (
											<div className="mt-2 pl-3 border-l-2 border-emerald-300">
												<p className="text-[10px] font-bold text-slate-500 mb-1">Balasan Anda:</p>
												<p className="text-xs text-slate-700 italic">"{activeApp.student_reply}"</p>
											</div>
										) : (
											<div className="mt-2 flex flex-col gap-2">
												<textarea
													id="studentReplyBox"
													placeholder="Ketik balasan / lengkapi data tambahan di sini..."
													className="w-full p-3 bg-white border border-sky-200 rounded-lg text-xs focus:ring-2 focus:ring-sky-500 outline-none"
													rows={2}
												/>
												<button
													onClick={() => {
														const el = document.getElementById('studentReplyBox');
														if(!el.value) return;
														replyNotes({ id: activeApp.id, reply: el.value })
															.then(() => toast.success('Balasan berhasil dikirim!'))
															.catch(() => toast.error('Gagal mengirim balasan.'));
													}}
													disabled={isReplyingNotes}
													className="self-end px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs rounded-lg transition-colors shadow-sm"
												>
													{isReplyingNotes ? 'Mengirim...' : 'Kirim Balasan'}
												</button>
											</div>
										)}
									</div>
								)}

								{/* Bagian Aksi Tindakan */}
								<div className="border-t border-gray-100 pt-5">
									<h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-1.5">
										<PiSparkle className="text-sky-600" /> Aksi Lamaran
									</h3>

									{/* Aksi khusus jika status penawaran diterima */}
									{activeApp.status === "OFFERED" && (
										<div className="p-4 border border-purple-100 bg-purple-50/40 rounded-xl flex flex-col gap-4">
											<p className="text-xs text-purple-800 leading-relaxed">
												Selamat! Unggah bukti LoA atau email penerimaan untuk menerima tawaran dan mengirimkannya ke antrean verifikasi CDA.
											</p>
											<label className="flex flex-col items-center justify-center w-full h-24 border-2 border-purple-300/40 border-dashed rounded-lg cursor-pointer bg-white hover:bg-purple-50/40 transition-colors">
												<div className="flex flex-col items-center justify-center pt-2 pb-2 text-center">
													<PiUploadSimple className="text-purple-500 mb-1" size={24} />
													<p className="text-xs text-gray-500 font-medium">
														{selectedFile ? selectedFile.name : "Pilih file LoA (PDF/Image)"}
													</p>
													<p className="text-[9px] text-gray-400 mt-0.5">Maksimal file 10MB</p>
												</div>
												<input
													type="file"
													accept=".pdf,.jpg,.jpeg,.png"
													onChange={(e) => setSelectedFile(e.target.files[0])}
													className="hidden"
												/>
											</label>
											<div className="flex flex-col sm:flex-row gap-3">
												<button
													onClick={handleAcceptOffer}
													disabled={isSubmittingAction}
													className="flex-1 px-4 py-2.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-bold text-sm shadow-sm transition-colors flex items-center justify-center gap-1"
												>
													{isSubmittingAction ? <PiSpinner className="animate-spin" /> : "Terima & Unggah Bukti"}
												</button>
												<button
													onClick={() => {
														setWithdrawReason("Menerima tawaran di lowongan lain.");
														handleWithdraw();
													}}
													disabled={isSubmittingAction}
													className="px-4 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-bold text-sm transition-colors"
												>
													Tolak Penawaran
												</button>
											</div>
										</div>
									)}

									{/* Aksi khusus jika status disetujui: Unggah Bukti Penerimaan LoA */}
									{activeApp.status === "ACCEPTED" && (
										<div className="p-4 border border-emerald-100 bg-emerald-50/40 rounded-xl flex flex-col gap-4">
											<div className="flex flex-col gap-1">
												<span className="text-xs font-bold text-emerald-800">Bukti Penerimaan (Letter of Acceptance)</span>
												<p className="text-[11px] text-emerald-600 leading-normal">
													Untuk melengkapi verifikasi administrasi CDA, silakan unggah bukti LoA (PDF / Gambar) resmi Anda.
												</p>
											</div>

											{/* Tautan unduhan bukti LoA terbaru */}
											{history.find(log => log.proof_url) && (
												<div className="p-3 bg-white/80 rounded-lg border border-emerald-200/50 flex justify-between items-center text-xs">
													<span className="font-medium text-emerald-800 flex items-center gap-1.5">
														<PiFilePdf size={16} className="text-red-500" /> Bukti LoA Diunggah
													</span>
													<a 
														href={resolveBackendAssetUrl(history.find(log => log.proof_url).proof_url)} 
														target="_blank" 
														rel="noopener noreferrer"
														className="text-sky-600 font-bold hover:underline inline-flex items-center gap-0.5"
													>
														Lihat Bukti <PiLinkSimple />
													</a>
												</div>
											)}

											<form onSubmit={handleUploadProof} className="flex flex-col gap-3">
												<div className="flex items-center justify-center w-full">
													<label className="flex flex-col items-center justify-center w-full h-24 border-2 border-emerald-300/40 border-dashed rounded-lg cursor-pointer bg-white hover:bg-emerald-50/20 transition-colors">
														<div className="flex flex-col items-center justify-center pt-2 pb-2 text-center">
															<PiUploadSimple className="text-emerald-500 mb-1" size={24} />
															<p className="text-xs text-gray-500 font-medium">
																{selectedFile ? selectedFile.name : "Pilih file LoA (PDF/Image)"}
															</p>
															<p className="text-[9px] text-gray-400 mt-0.5">Maksimal file 10MB</p>
														</div>
														<input 
															type="file" 
															accept=".pdf,.jpg,.jpeg,.png"
															onChange={(e) => setSelectedFile(e.target.files[0])}
															className="hidden" 
														/>
													</label>
												</div>
												{selectedFile && (
													<button
														type="submit"
														disabled={isSubmittingAction}
														className="w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-1.5 shadow-sm"
													>
														{isSubmittingAction ? (
															<>
																<PiSpinner className="animate-spin" /> Mengunggah...
															</>
														) : (
															<>Unggah & Terapkan Bukti</>
														)}
													</button>
												)}
											</form>
										</div>
									)}

									
									{/* Form Perbarui Status Mandiri */}
									{["APPLIED", "SCREENING", "INTERVIEW"].includes(activeApp.status) && (
										<div className="p-4 bg-sky-50/50 border border-sky-100 rounded-xl flex flex-col gap-3 mt-4">
											<span className="text-xs font-bold text-sky-800">Perbarui Status (Self-Reported)</span>
											<p className="text-[11px] text-sky-600/80 leading-normal mb-1">
												Anda menerima pembaruan email dari perusahaan? Perbarui status Kanban Anda di sini.
											</p>
											<div className="flex flex-col sm:flex-row gap-2">
												<select 
													id="newStatus"
													className="flex-1 px-3 py-2 bg-white border border-sky-200 rounded-lg text-xs focus:ring-1 focus:ring-sky-500 outline-none text-slate-700 font-medium"
													defaultValue=""
												>
													<option value="" disabled>Pilih Status Baru...</option>
													<option value="SCREENING">Lolos Seleksi Berkas (Screening)</option>
													<option value="INTERVIEW">Panggilan Wawancara (Interview)</option>
													<option value="OFFERED">Mendapat Tawaran (Offered)</option>
													<option value="REJECTED">Ditolak Perusahaan (Rejected)</option>
												</select>
												<button
													onClick={() => {
														const el = document.getElementById('newStatus');
														if(!el.value) return;
														updateStatus({ id: activeApp.id, data: { status: el.value, reason: 'Diperbarui mandiri oleh mahasiswa.' }})
															.then(() => {
																toast.success('Status berhasil diperbarui!');
																el.value = '';
															})
															.catch(err => toast.error('Gagal memperbarui status.'));
													}}
													disabled={isSubmittingAction}
													className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-bold text-xs rounded-lg transition-colors shadow-sm whitespace-nowrap"
												>
													Perbarui
												</button>
											</div>
										</div>
									)}

									{/* Pilihan pembatalan lamaran aktif */}
									{["APPLIED", "SCREENING", "INTERVIEW"].includes(activeApp.status) && (
										<div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col gap-3">
											<span className="text-xs font-bold text-gray-500">Tarik Lamaran ini</span>
											<p className="text-[11px] text-gray-400 leading-normal">
												Jika Anda memutuskan untuk membatalkan atau tidak melanjutkan lamaran ini, Anda dapat menarik lamaran Anda secara permanen.
											</p>
											<div className="flex flex-col gap-2">
												<input
													type="text"
													value={withdrawReason}
													onChange={(e) => setWithdrawReason(e.target.value)}
													placeholder="Alasan penarikan lamaran (opsional)..."
													className="px-3 py-2 border border-slate-200 rounded-lg text-xs w-full focus:outline-none focus:ring-1 focus:ring-sky-500 bg-white"
												/>
												<button
													onClick={handleWithdraw}
													disabled={isSubmittingAction}
													className="px-4 py-2 bg-rose-50 border border-rose-100 hover:bg-rose-100 text-rose-700 font-bold text-xs rounded-lg transition-colors flex items-center justify-center gap-1.5"
												>
													{isSubmittingAction ? (
														<>
															<PiSpinner className="animate-spin" /> Menarik...
														</>
													) : (
														<>Tarik Lamaran</>
													)}
												</button>
											</div>
										</div>
									)}
								</div>

								{/* Bagian Riwayat Perjalanan Lamaran */}
								<div className="border-t border-gray-100 pt-5 flex-1 flex flex-col min-h-[220px]">
									<h3 className="text-sm font-bold text-gray-900 mb-4 flex items-center gap-1.5">
										<PiCalendarBlank className="text-sky-600" /> Riwayat Perjalanan Lamaran
									</h3>

									{loadingHistory ? (
										<div className="flex items-center justify-center py-10 flex-grow">
											<PiSpinner size={24} className="animate-spin text-sky-950" />
										</div>
									) : history.length === 0 ? (
										<div className="text-center py-10 text-gray-400 text-xs">
											Belum ada riwayat aktivitas.
										</div>
									) : (
										<div className="relative border-l border-gray-200 pl-4 ml-2 flex flex-col gap-5">
											{history.map((log) => (
												<div key={log.id} className="relative">
													{/* Penanda Titik Garis Waktu */}
													<span className="absolute -left-[21px] top-1.5 bg-white border-2 border-sky-600 rounded-full w-2.5 h-2.5"></span>
													<div className="flex flex-col gap-0.5">
														<div className="flex justify-between items-center text-xs">
															<span className="font-bold text-gray-800">
																{statusMap[log.new_status]?.label || log.new_status}
															</span>
															<span className="text-[10px] text-gray-400">
																{formatDate(log.created_at)}
															</span>
														</div>
														{log.reason && (
															<p className="text-[11px] text-gray-500 italic flex items-center gap-1 mt-0.5 bg-gray-50 p-1.5 rounded border border-gray-100">
																<PiChatCenteredText size={12} className="text-gray-400 shrink-0" />
																<span>&ldquo;{log.reason}&rdquo;</span>
															</p>
														)}
														{log.proof_url && (
															<a 
																href={resolveBackendAssetUrl(log.proof_url)} 
																target="_blank" 
																rel="noopener noreferrer"
																className="text-[10px] text-sky-600 font-bold hover:underline inline-flex items-center gap-0.5 mt-1"
															>
																Unduh Bukti <PiLinkSimple />
															</a>
														)}
													</div>
												</div>
											))}
										</div>
									)}
								</div>
							</div>
						</motion.div>
					</>
				)}
			</AnimatePresence>
		</div>
	);
}

export default Lamaran;
