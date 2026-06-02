import { useState, useMemo } from "react";
import { DayPicker } from "react-day-picker";
import "react-day-picker/dist/style.css";
import { format } from "date-fns";
import { id } from "date-fns/locale";
import { PiWarning, PiClock, PiUpload, PiCheckCircleFill, PiSpinner, PiFilePdf, PiTrash, PiSparkle } from "react-icons/pi";
import toast from "react-hot-toast";

import { usePlacements, useActivityLogs, useActivityLogMutations } from "../../hooks/usePlacements";
import { resolveBackendAssetUrl } from "../../utils/assetUrl";

function JurnalForm({ activeLog, selectedDate, onSave, onDelete, onEnhance, isSaving, isDeleting, isEnhancing }) {
	const [startTimeStr, setStartTimeStr] = useState("08:00");
	
	// Inisialisasi waktu selesai berdasarkan durasi activeLog
	const initialEndTime = useMemo(() => {
		if (activeLog) {
			const durationHoursDec = parseFloat(activeLog.duration_hours);
			const endHour = Math.floor(8 + durationHoursDec);
			const endMinute = Math.round((durationHoursDec % 1) * 60);
			return `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;
		}
		return "16:00";
	}, [activeLog]);

	const [endTimeStr, setEndTimeStr] = useState(initialEndTime);
	const [description, setDescription] = useState(activeLog?.description_raw || "");
	const [selectedFile, setSelectedFile] = useState(null);

	const calculateWorkTime = (start, end) => {
		if (!start || !end) return { label: "0 Jam", error: null };
		const [sH, sM] = start.split(":").map(Number);
		const [eH, eM] = end.split(":").map(Number);
		const sTotal = sH * 60 + sM;
		const eTotal = eH * 60 + eM;
		const diff = eTotal - sTotal;
		if (diff <= 0) return { label: "-", error: "Jam selesai harus setelah jam mulai" };
		const hours = Math.floor(diff / 60);
		const minutes = diff % 60;
		return { label: `${hours} Jam ${minutes} Menit`, error: null };
	};

	const workTime = calculateWorkTime(startTimeStr, endTimeStr);

	const handleLocalSave = () => {
		onSave({
			log_date: format(selectedDate, "yyyy-MM-dd"),
			start_time: `${startTimeStr}:00`,
			end_time: `${endTimeStr}:00`,
			description_raw: description,
			file: selectedFile
		});
	};

	return (
		<div className="p-6 bg-white rounded-xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)] border border-slate-100 flex flex-col gap-6">
			{/* Header Entri */}
			<div className="text-black flex justify-between items-start border-b border-slate-100 pb-4">
				<div>
					<div className="font-bold text-slate-800 text-xl">Entri Jurnal</div>
					<div className="text-slate-500 text-sm">
						{selectedDate ? format(selectedDate, "EEEE, d MMMM yyyy", { locale: id }) : "Pilih Tanggal"}
					</div>
				</div>
				{activeLog ? (
					<div className="flex gap-1.5 items-center text-xs px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full font-bold shadow-sm">
						<PiCheckCircleFill size={16} />
						<div>Sudah Terisi</div>
					</div>
				) : (
					<div className="flex gap-1.5 items-center text-xs px-3 py-1 bg-amber-100 text-amber-800 rounded-full font-bold shadow-sm">
						<PiWarning size={16} />
						<div>Belum Terisi</div>
					</div>
				)}
			</div>

			{/* Jam */}
			<div className="space-y-4">
				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div className="flex flex-col gap-1.5">
						<label className="text-sm font-bold text-slate-700">Jam Mulai</label>
						<div className="relative">
							<PiClock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
							<input
								type="time"
								value={startTimeStr}
								onChange={(e) => setStartTimeStr(e.target.value)}
								className="pl-10 w-full py-2.5 text-slate-700 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all"
							/>
						</div>
					</div>
					<div className="flex flex-col gap-1.5">
						<label className="text-sm font-bold text-slate-700">Jam Selesai</label>
						<div className="relative">
							<PiClock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
							<input
								type="time"
								value={endTimeStr}
								onChange={(e) => setEndTimeStr(e.target.value)}
								className="pl-10 w-full py-2.5 text-slate-700 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all"
							/>
						</div>
					</div>
				</div>

				{!workTime.error ? (
					<div className="text-sky-700 bg-sky-50/50 px-3 py-2 rounded-lg text-sm font-bold border border-sky-100 w-fit">
						Durasi Kerja: {workTime.label}
					</div>
				) : (
					<div className="text-rose-700 bg-rose-50 px-3 py-2 rounded-lg text-sm font-bold border border-rose-100 w-fit flex items-center gap-2">
						<PiWarning size={16} />
						{workTime.error}
					</div>
				)}
			</div>

			{/* Input Deskripsi */}
			<div className="flex flex-col gap-1.5">
				<label className="text-sm font-bold text-slate-700">Deskripsi Aktivitas</label>
				<textarea
					value={description}
					onChange={(e) => setDescription(e.target.value)}
					placeholder="Jelaskan kegiatan yang dijalankan secara detail..."
					className="w-full h-40 p-4 text-slate-700 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-sky-500 outline-none resize-none transition-all"
				/>
				{activeLog?.description_ai_enhanced && (
					<div className="mt-2 p-3 bg-sky-50 border border-sky-100 rounded-lg">
						<div className="flex items-center gap-1.5 text-xs font-bold text-sky-800 mb-1">
							<PiSparkle size={14} /> Hasil AI Enhance
						</div>
						<p className="text-sm text-slate-700 leading-relaxed">{activeLog.description_ai_enhanced}</p>
					</div>
				)}
			</div>

			{/* Upload */}
			<div className="flex flex-col gap-1.5">
				<label className="text-sm font-bold text-slate-700">Lampiran/Dokumen Pendukung</label>
				
				{activeLog?.attachment_url && !selectedFile && (
					<div className="flex items-center justify-between p-3 bg-emerald-50 border border-emerald-100 rounded-lg mb-2">
						<div className="flex items-center gap-2 text-emerald-800 text-sm font-bold">
							<PiFilePdf size={20} className="text-red-500" /> Dokumen Terlampir
						</div>
						<a href={resolveBackendAssetUrl(activeLog.attachment_url)} target="_blank" rel="noopener noreferrer" className="text-xs text-sky-600 font-bold hover:underline">
							Lihat File
						</a>
					</div>
				)}

				<label className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-slate-200 bg-slate-50 hover:bg-sky-50/50 rounded-xl cursor-pointer hover:border-sky-300 transition-colors group">
					<PiUpload className="text-slate-400 group-hover:text-sky-500 transition-colors" size={32} />
					<span className="mt-3 font-bold text-slate-600 text-sm">
						{selectedFile ? selectedFile.name : (activeLog?.attachment_url ? "Ganti File Lampiran Baru" : "Klik untuk upload file")}
					</span>
					<span className="text-[11px] text-slate-400 mt-1">PDF, JPG, PNG (Max 5MB)</span>
					<input 
						type="file" 
						className="hidden" 
						onChange={(e) => setSelectedFile(e.target.files[0])}
						accept=".pdf,.jpg,.jpeg,.png"
					/>
				</label>
			</div>

			{/* Tombol Aksi */}
			<div className="flex gap-3 justify-end mt-2 pt-5 border-t border-slate-100">
				{activeLog && (
					<>
						<button
							onClick={onEnhance}
							disabled={isEnhancing || isSaving || isDeleting}
							className="px-4 py-2 font-bold text-sky-700 hover:bg-sky-50 rounded-lg transition-colors flex items-center gap-2 text-sm disabled:opacity-70 disabled:cursor-not-allowed"
						>
							{isEnhancing ? <PiSpinner className="animate-spin" size={18} /> : <PiSparkle size={18} />} AI Enhance
						</button>
						<button
							onClick={onDelete}
							disabled={isDeleting || isSaving || isEnhancing}
							className="px-4 py-2 font-bold text-rose-600 hover:bg-rose-50 rounded-lg transition-colors flex items-center gap-2 text-sm disabled:opacity-70 disabled:cursor-not-allowed"
						>
							<PiTrash size={18} /> Hapus
						</button>
					</>
				)}
				<button 
					onClick={() => {
						setDescription("");
						setSelectedFile(null);
					}}
					className="px-5 py-2 font-bold text-slate-600 hover:bg-slate-100 rounded-lg transition-colors text-sm"
				>
					Batal
				</button>
				<button 
					onClick={handleLocalSave}
					disabled={isSaving || isDeleting || isEnhancing}
					className="px-6 py-2.5 bg-sky-950 text-white font-bold rounded-lg shadow-md hover:bg-sky-900 hover:shadow-lg transition-all text-sm flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
				>
					{(isSaving || isDeleting) && <PiSpinner className="animate-spin" size={18} />}
					{activeLog ? "Simpan Perubahan" : "Buat Jurnal Baru"}
				</button>
			</div>
		</div>
	);
}

function Jurnal() {
	const { data: placements = [], isLoading: isLoadingPlacements } = usePlacements();
	const activePlacement = placements.length > 0 ? placements[0] : null;

	const { data: logs = [] } = useActivityLogs(activePlacement?.id);
	const {
		createLog,
		updateLog,
		deleteLog,
		uploadAttachment,
		enhanceLog,
		isCreating,
		isUpdating,
		isUploading,
		isDeleting,
		isEnhancing
	} = useActivityLogMutations(activePlacement?.id);

	const [selectedDate, setSelectedDate] = useState(new Date());

	// Cari apakah log ada untuk tanggal terpilih
	const activeLog = logs.find(
		(log) => log.activity_date === format(selectedDate, "yyyy-MM-dd")
	);

	const journalStartDate = activePlacement ? new Date(activePlacement.start_date) : new Date(2026, 1, 1);
	const totalDays = activePlacement ? Math.ceil((new Date(activePlacement.end_date) - new Date(activePlacement.start_date)) / (1000 * 60 * 60 * 24)) : 0;
	const filledDays = logs.length;
	const completionRate = totalDays > 0 ? Math.round((filledDays / totalDays) * 100) : 0;

	const handleSave = async (formData) => {
		if (!activePlacement) return;
		
		if (!formData.description_raw.trim()) {
			toast.error("Deskripsi aktivitas wajib diisi");
			return;
		}

		try {
			let logId;
			const payload = {
				log_date: formData.log_date,
				start_time: formData.start_time,
				end_time: formData.end_time,
				description_raw: formData.description_raw,
			};

			if (activeLog) {
				await updateLog({ logId: activeLog.id, data: payload });
				logId = activeLog.id;
				toast.success("Jurnal berhasil diperbarui!");
			} else {
				const result = await createLog(payload);
				logId = result.id;
				toast.success("Jurnal berhasil disimpan!");
			}

			if (formData.file && logId) {
				await uploadAttachment({ logId, file: formData.file });
				toast.success("Lampiran berhasil diunggah!");
			}

		} catch (err) {
			console.error("Save error:", err);
			toast.error(err.response?.data?.detail || "Gagal menyimpan jurnal");
		}
	};

	const handleDelete = async () => {
		if (!activeLog) return;
		if (confirm("Apakah Anda yakin ingin menghapus catatan hari ini?")) {
			try {
				await deleteLog(activeLog.id);
				toast.success("Catatan jurnal berhasil dihapus!");
			} catch {
				toast.error("Gagal menghapus jurnal");
			}
		}
	};

	const handleEnhance = async () => {
		if (!activeLog) return;
		try {
			await enhanceLog(activeLog.id);
			toast.success("Deskripsi jurnal berhasil dipoles AI.");
		} catch (err) {
			toast.error(err.response?.data?.detail || err.message || "Gagal memoles deskripsi jurnal");
		}
	};

	if (isLoadingPlacements) {
		return <div className="p-10 flex justify-center"><PiSpinner className="animate-spin text-sky-950" size={40} /></div>;
	}

	if (!activePlacement) {
		return (
			<div className="font-jakarta text-center py-20 bg-white rounded-xl shadow-sm border border-slate-100 flex flex-col items-center gap-4">
				<PiWarning size={48} className="text-amber-500" />
				<h2 className="text-2xl font-bold text-slate-800">Belum Ada Penempatan Aktif</h2>
				<p className="text-slate-500">Anda belum memiliki placement aktif. Silakan tunggu konfirmasi dari CDA.</p>
			</div>
		);
	}

	return (
		<div className="font-jakarta">
			{/* Banner */}
			<div className="mb-5 bg-sky-950 py-6 px-5 sm:py-7 sm:px-10 rounded-xl text-white flex flex-col sm:flex-row justify-between sm:items-center gap-4 shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)] relative overflow-hidden">
				<div className="flex flex-col gap-2 relative z-10">
					<div className="text-2xl sm:text-3xl font-bold">Jurnal Harian</div>
					<div className="text-sm sm:text-base opacity-90 max-w-2xl">
						Catat aktivitas internship harian Anda di <strong>{activePlacement.company_name || "Perusahaan"}</strong> secara rutin untuk mempermudah penyusunan laporan akhir.
					</div>
				</div>
				<div className="absolute top-0 right-0 w-64 h-64 bg-sky-900 rounded-full blur-3xl opacity-50 -translate-y-10 translate-x-10"></div>
			</div>

			{/* Main */}
			<div className="flex flex-col lg:flex-row gap-5">
				{/* Sisi Kiri */}
				<div className="w-full lg:w-80 flex flex-col gap-5">
					{/* Ringkasan Penempatan Aktif */}
					<div className="p-5 bg-white rounded-xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)] flex flex-col gap-3 border border-slate-100">
						<div className="text-black font-bold text-lg border-b border-slate-100 pb-2">Detail Penempatan</div>
						<div className="flex flex-col gap-2 mt-1">
							<div>
								<p className="text-xs text-slate-500 font-medium">Perusahaan</p>
								<p className="text-sm font-bold text-slate-800">{activePlacement.company_name}</p>
							</div>
							<div>
								<p className="text-xs text-slate-500 font-medium">Periode Magang</p>
								<p className="text-sm font-bold text-slate-800">{format(new Date(activePlacement.start_date), "dd MMM yyyy", { locale: id })} - {format(new Date(activePlacement.end_date), "dd MMM yyyy", { locale: id })}</p>
							</div>
							{activePlacement.external_supervisor_name && (
								<div>
									<p className="text-xs text-slate-500 font-medium">Pembimbing Lapangan</p>
									<p className="text-sm font-bold text-slate-800">{activePlacement.external_supervisor_name}</p>
								</div>
							)}
							<div>
								<p className="text-xs text-slate-500 font-medium">Status</p>
								<span className="inline-flex mt-1 items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-100 text-emerald-800">
									{activePlacement.status === "ACTIVE" ? "Aktif" : activePlacement.status}
								</span>
							</div>
						</div>
					</div>

					{/* Status Pengisian */}
					<div className="p-5 font-bold bg-white rounded-xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)] flex flex-col gap-1 border border-slate-100">
						<div className="text-black text-sm">Status Pengisian</div>
						<div className="text-black text-2xl flex justify-between items-center">
							<div>
								{filledDays} <strong className="text-sm text-zinc-500">/ {totalDays} Hari</strong>
							</div>
							<div className="text-xs px-2 py-1 bg-sky-100 text-sky-800 rounded-full flex items-center gap-1">
								{completionRate}% Selesai
							</div>
						</div>
						<div className="bg-zinc-100 h-1.5 rounded-full mt-2 overflow-hidden">
							<div className="bg-sky-500 h-full rounded-full transition-all duration-500" style={{ width: `${Math.min(completionRate, 100)}%` }}></div>
						</div>
					</div>

					{/* Kalender */}
					<div className="bg-white text-black rounded-xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.06)] border border-slate-100 overflow-x-auto flex justify-center p-2">
						<DayPicker
							locale={id}
							mode="single"
							selected={selectedDate}
							onSelect={(day) => day && setSelectedDate(day)}
							disabled={[
								{ dayOfWeek: [0] },
								{ before: journalStartDate },
								{ after: new Date() },
							]}
							modifiers={{
								hasLog: logs.map(l => new Date(l.activity_date))
							}}
							modifiersClassNames={{
								hasLog: "font-bold text-sky-600 border-b-2 border-sky-400"
							}}
							classNames={{
								selected: "bg-sky-600 text-white hover:bg-sky-700 rounded-full outline-none border-none",
								today: "text-sky-600 font-bold",
								month: "p-2",
							}}
						/>
					</div>
				</div>

				{/* Sisi Kanan */}
				<div className="flex-1 pb-10">
					<JurnalForm 
						key={`${format(selectedDate, "yyyy-MM-dd")}-${activeLog?.id || 'new'}`}
						activeLog={activeLog}
						selectedDate={selectedDate}
						onSave={handleSave}
						onDelete={handleDelete}
						onEnhance={handleEnhance}
						isSaving={isCreating || isUpdating || isUploading}
						isDeleting={isDeleting}
						isEnhancing={isEnhancing}
					/>
				</div>
			</div>
		</div>
	);
}

export default Jurnal;
