import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { authService } from "../../services/authService";
import { z } from "zod";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { 
  PiUser, 
  PiIdentificationCard, 
  PiEnvelopeSimple, 
  PiLockKey, 
  PiEye, 
  PiEyeSlash, 
  PiGraduationCap,
  PiArrowRight,
  PiGraph,
  PiSpinnerGap,
  PiBookOpenText,
  PiArrowLeft,
  PiBuildings,
  PiCaretDown
} from "react-icons/pi";

const registrationSchema = z.object({
  full_name: z.string().min(3, "Nama lengkap minimal 3 karakter"),
  nim: z.string()
    .min(6, "NIM minimal 6 karakter")
    .max(20, "NIM maksimal 20 karakter")
    .regex(/^[A-Za-z][A-Za-z0-9]+$/, "Format NIM tidak valid. Harus diawali dengan huruf dan hanya berisi huruf/angka (Contoh: G64012012)"),
  semester: z.coerce.number().min(1, "Semester minimal 1").max(14, "Semester maksimal 14"),
  department_id: z.string().min(1, "Wajib memilih departemen"),
  email: z.string().email("Format email tidak valid").endsWith("@apps.ipb.ac.id", "Wajib menggunakan email institusi @apps.ipb.ac.id"),
  password: z.string().min(8, "Kata sandi minimal 8 karakter")
});

function Registration() {
	const navigate = useNavigate();
	const { register: registerAuth, isRegistering, registerError } = useAuth();
	
	const [showPassword, setShowPassword] = useState(false);
	const [emailCheck, setEmailCheck] = useState({ isLoading: false, isAvailable: null, message: "" });

	const { register, handleSubmit, control, setValue, watch, formState: { errors } } = useForm({
		resolver: zodResolver(registrationSchema),
		defaultValues: { semester: 1, department_id: "" }
	});

	const emailValue = useWatch({
		control,
		name: "email",
	});

	const [departments, setDepartments] = useState([]);
	const [facultyFilter, setFacultyFilter] = useState("");
	const [isFacultyOpen, setIsFacultyOpen] = useState(false);
	const [isDeptOpen, setIsDeptOpen] = useState(false);

	useEffect(() => {
		authService.getDepartments().then(data => {
			if (data) setDepartments(data);
		});
	}, []);

	const uniqueFaculties = [...new Set(departments.map(d => d.faculty))].filter(Boolean).sort();

	useEffect(() => {
		const timer = setTimeout(async () => {
			if (!emailValue || emailValue.length < 3) {
				setEmailCheck({ isLoading: false, isAvailable: null, message: "" });
				return;
			}
			setEmailCheck(prev => ({ ...prev, isLoading: true }));
			try {
				const res = await authService.checkAvailability(emailValue);
				setEmailCheck({ 
					isLoading: false, 
					isAvailable: res.available, 
					message: res.reason || (res.available ? "Email tersedia" : "Email sudah digunakan")
				});
			} catch {
				setEmailCheck({ isLoading: false, isAvailable: null, message: "" });
			}
		}, 500);
		return () => clearTimeout(timer);
	}, [emailValue]);

	const onSubmit = (data) => {
		if (emailCheck.isAvailable === false) return;
		registerAuth(data);
	};

	return (
		<div className="grid min-h-dvh bg-white grid-cols-1 md:grid-cols-2 font-jakarta overflow-hidden">
			{/* Left Side: Form Section */}
			<div className="flex items-center justify-center bg-white p-5 sm:p-8 md:p-20 overflow-y-auto order-1">
				<div className="w-full max-w-md space-y-8 sm:space-y-10 py-8 sm:py-10">
					<div className="space-y-4">
						<button 
							onClick={() => navigate("/")}
							className="text-xs font-bold text-sky-800 hover:text-[#001f42] flex items-center gap-1.5 transition-colors uppercase tracking-wider mb-2"
						>
							<PiArrowLeft size={16} />
							Kembali ke Beranda
						</button>
						<div className="space-y-3">
							<h2 className="text-3xl sm:text-4xl font-extrabold text-[#002957] tracking-tight">
								Daftar LARAS
							</h2>
							<p className="text-zinc-500 font-medium text-base">
								Mulai langkah awal karir profesional Anda bersama IPB University.
							</p>
						</div>
					</div>

					<form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
						<div className="space-y-5">
							{/* Nama Lengkap */}
							<div className="space-y-2">
								<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Nama Lengkap</label>
								<div className="relative group">
									<PiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
									<input
										type="text"
										{...register("full_name")}
										placeholder="Contoh: Windah Basudara"
										className="w-full pl-12 pr-4 py-3.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-sm text-zinc-800"
									/>
								</div>
								{errors.full_name && <p className="text-xs font-bold text-red-500">{errors.full_name.message}</p>}
							</div>

							<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
								{/* NIM */}
								<div className="space-y-2">
									<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">NIM</label>
									<div className="relative group">
										<PiIdentificationCard className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
										<input
											type="text"
											{...register("nim")}
											placeholder="G640120XXXX"
											className="w-full pl-12 pr-4 py-3.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-sm text-zinc-800"
										/>
									</div>
									{errors.nim && <p className="text-xs font-bold text-red-500">{errors.nim.message}</p>}
								</div>

								{/* Semester */}
								<div className="space-y-2">
									<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Semester</label>
									<div className="relative group">
										<PiBookOpenText className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
										<input
											type="number"
											{...register("semester")}
											className="w-full pl-12 pr-4 py-3.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-sm text-zinc-800"
										/>
									</div>
									{errors.semester && <p className="text-xs font-bold text-red-500">{errors.semester.message}</p>}
								</div>
							</div>

							{/* Fakultas & Departemen */}
							<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
								<div className="space-y-2">
									<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Fakultas</label>
									<div className="relative">
										<button
											type="button"
											onClick={() => setIsFacultyOpen(!isFacultyOpen)}
											className="w-full pl-12 pr-4 py-3.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-sm text-left flex justify-between items-center"
										>
											<PiBuildings className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" size={20} />
											<span className={`truncate ${facultyFilter ? "text-zinc-800" : "text-zinc-400"}`}>
												{facultyFilter || "Pilih Fakultas"}
											</span>
											<PiCaretDown size={18} className="text-zinc-400" />
										</button>
										{isFacultyOpen && (
											<>
												<div className="fixed inset-0 z-40" onClick={() => setIsFacultyOpen(false)}></div>
												<div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-100 rounded-2xl shadow-xl z-50 max-h-64 overflow-y-auto">
													{uniqueFaculties.map(f => (
														<button
															type="button"
															key={f}
															onClick={() => {
																setFacultyFilter(f);
																setIsFacultyOpen(false);
																setValue("department_id", "", { shouldValidate: true });
															}}
															className={`w-full text-left px-4 py-3 text-sm transition-colors border-b border-slate-50 last:border-0 ${facultyFilter === f ? "bg-sky-50 font-bold text-sky-900" : "hover:bg-slate-50 font-medium text-slate-700"}`}
														>
															{f}
														</button>
													))}
												</div>
											</>
										)}
									</div>
								</div>

								<div className="space-y-2">
									<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Departemen</label>
									<div className="relative">
										<button
											type="button"
											disabled={!facultyFilter}
											onClick={() => setIsDeptOpen(!isDeptOpen)}
											className={`w-full pl-12 pr-4 py-3.5 ${!facultyFilter ? "bg-zinc-100 cursor-not-allowed" : "bg-[#E8F1FF] focus:ring-2 focus:ring-sky-500"} border-none rounded-xl outline-none transition-all font-medium text-sm text-left flex justify-between items-center`}
										>
											<PiGraduationCap className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" size={20} />
											<span className={`truncate ${watch("department_id") ? "text-zinc-800" : "text-zinc-400"}`}>
												{watch("department_id") 
													? departments.find(d => d.id === watch("department_id"))?.name 
													: "Pilih Departemen"}
											</span>
											<PiCaretDown size={18} className="text-zinc-400" />
										</button>
										{isDeptOpen && facultyFilter && (
											<>
												<div className="fixed inset-0 z-40" onClick={() => setIsDeptOpen(false)}></div>
												<div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-100 rounded-2xl shadow-xl z-50 max-h-64 overflow-y-auto">
													{departments.filter(d => d.faculty === facultyFilter).map(d => (
														<button
															type="button"
															key={d.id}
															onClick={() => {
																setValue("department_id", d.id, { shouldValidate: true });
																setIsDeptOpen(false);
															}}
															className={`w-full text-left px-4 py-3 text-sm transition-colors border-b border-slate-50 last:border-0 ${watch("department_id") === d.id ? "bg-sky-50 font-bold text-sky-900" : "hover:bg-slate-50 font-medium text-slate-700"}`}
														>
															{d.name}
														</button>
													))}
												</div>
											</>
										)}
									</div>
									{errors.department_id && <p className="text-xs font-bold text-red-500">{errors.department_id.message}</p>}
								</div>
							</div>

							{/* Email */}
							<div className="space-y-2">
								<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Email Mahasiswa</label>
								<div className="relative group">
									<PiEnvelopeSimple className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
									<input
										type="email"
										{...register("email")}
										placeholder="username@apps.ipb.ac.id"
										className={`w-full pl-12 pr-10 py-3.5 bg-[#E8F1FF] border-2 rounded-xl focus:ring-0 outline-none transition-all font-medium text-sm text-zinc-800 ${
											emailCheck.isAvailable === false ? "border-red-400 focus:border-red-500" :
											emailCheck.isAvailable === true ? "border-emerald-400 focus:border-emerald-500" :
											"border-transparent focus:border-sky-500"
										}`}
									/>
									<div className="absolute right-4 top-1/2 -translate-y-1/2">
										{emailCheck.isLoading && <PiSpinnerGap className="animate-spin text-zinc-400" size={18} />}
									</div>
								</div>
								{errors.email && <p className="text-xs font-bold text-red-500">{errors.email.message}</p>}
								{!errors.email && emailCheck.message && (
									<p className={`text-xs font-bold ${emailCheck.isAvailable ? "text-emerald-600" : "text-red-500"}`}>
										{emailCheck.message}
									</p>
								)}
							</div>

							{/* Password */}
							<div className="space-y-2">
								<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Kata Sandi</label>
								<div className="relative group">
									<PiLockKey className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
									<input
										type={showPassword ? "text" : "password"}
										{...register("password")}
										placeholder="Minimal 8 karakter"
										className="w-full pl-12 pr-11 py-3.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-sm text-zinc-800"
									/>
									<button 
										type="button"
										onClick={() => setShowPassword(!showPassword)}
										className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-[#002957] transition-colors"
									>
										{showPassword ? <PiEyeSlash size={20} /> : <PiEye size={20} />}
									</button>
								</div>
								{errors.password && <p className="text-xs font-bold text-red-500">{errors.password.message}</p>}
							</div>
						</div>

						{registerError && (
							<div className="p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-xs font-bold">
								{typeof registerError.response?.data?.detail === 'string'
									? registerError.response.data.detail
									: Array.isArray(registerError.response?.data?.detail)
									? registerError.response.data.detail[0]?.msg
									: "Registrasi gagal. Pastikan data yang Anda masukkan benar."}
							</div>
						)}

						<button
							type="submit"
							disabled={isRegistering}
							className="w-full py-4 bg-[#002957] hover:bg-[#001f42] text-white rounded-xl shadow-lg shadow-sky-950/20 font-bold text-base transition-all flex items-center justify-center gap-2 active:scale-[0.98] disabled:opacity-70"
						>
							{isRegistering ? (
								<PiSpinnerGap size={24} className="animate-spin" />
							) : (
								<>
									<span>Daftar Sekarang</span>
									<PiArrowRight size={20} weight="bold" />
								</>
							)}
						</button>
					</form>

					<div className="text-center text-zinc-500 font-medium text-sm">
						Sudah punya akun?{" "}
						<button onClick={() => navigate("/login")} className="text-[#002957] font-bold hover:underline">
							Masuk di sini
						</button>
					</div>
				</div>
			</div>

			{/* Right Side: Hero Graphic Section with Image Background */}
			<div className="hidden md:flex relative items-center justify-center bg-[#E6EFFF] overflow-hidden order-2">
				{/* Background Image Overlay */}
				<img
					src="/assets/bg-registration.png"
					alt="Background"
					className="absolute inset-0 h-full w-full object-cover bg-blend-overlay opacity-90"
				/>

				{/* Decorative Network Icon at bottom right */}
				<div className="absolute -bottom-10 -right-10 opacity-20 text-[#002957]">
					<PiGraph size={300} />
				</div>

				{/* Floating Card */}
				<div className="relative z-10 w-full max-w-sm p-10 bg-white/80 backdrop-blur-xl rounded-[2rem] border border-white/50 shadow-[0_20px_50px_rgba(0,41,87,0.12)] space-y-8">
					<div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-md">
						<PiGraduationCap size={28} className="text-[#002957]" />
					</div>
					
					<div className="space-y-4">
						<h3 className="text-2xl font-extrabold text-[#002957]">
							Membangun Masa Depan
						</h3>
						<p className="text-sm font-medium text-zinc-600 leading-relaxed">
							LARAS menghubungkan mahasiswa IPB University dengan peluang magang dan karir profesional terkurasi, menjembatani dunia akademik dengan industri.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}

export default Registration;
