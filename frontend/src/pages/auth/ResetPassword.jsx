import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { 
  PiLockKey, 
  PiEye, 
  PiEyeSlash, 
  PiGraduationCap,
  PiArrowRight,
  PiGraph,
  PiSpinnerGap,
  PiArrowLeft,
  PiKey
} from "react-icons/pi";

const resetSchema = z.object({
  token: z.string().min(1, "Token tidak boleh kosong"),
  new_password: z.string().min(8, "Kata sandi minimal 8 karakter")
});

function ResetPassword() {
	const navigate = useNavigate();
	const [searchParams] = useSearchParams();
	const tokenFromUrl = searchParams.get("token") || "";

	const { resetPassword, isResettingPassword, resetPasswordError, resetPasswordSuccess } = useAuth();
	
	const [showPassword, setShowPassword] = useState(false);

	const { register, handleSubmit, formState: { errors } } = useForm({
		resolver: zodResolver(resetSchema),
		defaultValues: { token: tokenFromUrl, new_password: "" }
	});

	const onSubmit = async (data) => {
		try {
			await resetPassword(data);
		} catch (error) {
			// Error di-handle oleh react-query mutation
		}
	};

	return (
		<div className="grid min-h-dvh bg-white grid-cols-1 md:grid-cols-2 font-jakarta overflow-hidden">
			{/* Left Side: Form Section */}
			<div className="flex items-center justify-center bg-white p-5 sm:p-8 md:p-20 overflow-y-auto order-1">
				<div className="w-full max-w-md space-y-8 sm:space-y-10 py-8 sm:py-10">
					<div className="space-y-4">
						<button 
							onClick={() => navigate("/login")}
							className="text-xs font-bold text-sky-800 hover:text-[#001f42] flex items-center gap-1.5 transition-colors uppercase tracking-wider mb-2"
						>
							<PiArrowLeft size={16} />
							Kembali ke Halaman Masuk
						</button>
						<div className="space-y-3">
							<h2 className="text-3xl sm:text-4xl font-extrabold text-[#002957] tracking-tight">
								Reset Password
							</h2>
							<p className="text-zinc-500 font-medium text-base">
								Masukkan token dari email Anda dan password baru.
							</p>
						</div>
					</div>

					{resetPasswordSuccess ? (
						<div className="space-y-6">
							<div className="p-4 bg-emerald-50 border border-emerald-100 rounded-xl text-emerald-700 font-medium text-center">
								Password Anda berhasil direset. Silakan login menggunakan password baru.
							</div>
							<button
								onClick={() => navigate("/login")}
								className="w-full py-4 bg-[#002957] hover:bg-[#001f42] text-white rounded-xl shadow-lg shadow-sky-950/20 font-bold text-base transition-all"
							>
								Kembali ke Login
							</button>
						</div>
					) : (
						<form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
							<div className="space-y-5">
								{/* Token */}
								<div className="space-y-2">
									<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Token Reset</label>
									<div className="relative group">
										<PiKey className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
										<input
											type="text"
											{...register("token")}
											placeholder="Masukkan Token dari Email"
											className="w-full pl-12 pr-4 py-3.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-sm text-zinc-800"
										/>
									</div>
									{errors.token && <p className="text-xs font-bold text-red-500">{errors.token.message}</p>}
								</div>

								{/* New Password */}
								<div className="space-y-2">
									<label className="text-sm font-bold text-[#002957] ml-1 uppercase tracking-wider">Kata Sandi Baru</label>
									<div className="relative group">
										<PiLockKey className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={20} />
										<input
											type={showPassword ? "text" : "password"}
											{...register("new_password")}
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
									{errors.new_password && <p className="text-xs font-bold text-red-500">{errors.new_password.message}</p>}
								</div>
							</div>

							{resetPasswordError && (
								<div className="p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-xs font-bold">
									{typeof resetPasswordError.response?.data?.detail === 'string'
										? resetPasswordError.response.data.detail
										: "Reset password gagal. Token tidak valid atau sudah kadaluarsa."}
								</div>
							)}

							<button
								type="submit"
								disabled={isResettingPassword}
								className="w-full py-4 bg-[#002957] hover:bg-[#001f42] text-white rounded-xl shadow-lg shadow-sky-950/20 font-bold text-base transition-all flex items-center justify-center gap-2 active:scale-[0.98] disabled:opacity-70"
							>
								{isResettingPassword ? (
									<PiSpinnerGap size={24} className="animate-spin" />
								) : (
									<>
										<span>Reset Password</span>
										<PiArrowRight size={20} weight="bold" />
									</>
								)}
							</button>
						</form>
					)}
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
							Akses Kembali
						</h3>
						<p className="text-sm font-medium text-zinc-600 leading-relaxed">
							Atur ulang password Anda untuk kembali mengakses layanan LARAS dan mengelola perjalanan karir Anda di IPB University.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}

export default ResetPassword;
