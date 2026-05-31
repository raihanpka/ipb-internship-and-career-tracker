import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { PiEnvelopeSimple, PiArrowRight, PiSpinnerGap, PiCheckCircle } from "react-icons/pi";

function ForgotPassword() {
	const navigate = useNavigate();
	const { forgotPassword, isRequestingReset, resetSent, resetError } = useAuth();
	const [email, setEmail] = useState("");

	const handleSubmit = (e) => {
		e.preventDefault();
		forgotPassword(email);
	};

	return (
		<div className="min-h-dvh w-full bg-gradient-to-br from-[#F8FAFF] via-[#F0F5FF] to-[#E8F1FF] flex flex-col items-center justify-center p-4 sm:p-6 font-jakarta overflow-y-auto relative">
			{/* Decorative glows */}
			<div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-200/20 rounded-full blur-[120px]" />
			<div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-sky-200/20 rounded-full blur-[120px]" />

			<div className="relative z-10 w-full max-w-lg flex flex-col items-center">
				{/* Brand Header */}
				<div className="mb-8 sm:mb-10 text-center space-y-4">
					<img 
						src="/logo/laras.png" 
						alt="LARAS Logo" 
						className="h-16 w-auto mx-auto"
					/>
					<div className="space-y-1">
						<h1 className="text-[32px] font-extrabold text-[#002957] tracking-tight">LARAS IPB</h1>
						<p className="text-sm font-medium text-zinc-500">
							Direktorat Kemahasiswaan dan Pengembangan Karir
						</p>
					</div>
				</div>

				{/* Card */}
				<div className="w-full bg-white rounded-[1.75rem] sm:rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,41,87,0.06)] border border-white/50 p-6 sm:p-12 space-y-8 sm:space-y-10">
					<div className="space-y-4">
						<h2 className="text-2xl sm:text-3xl font-extrabold text-[#002957]">Lupa Password?</h2>
						<p className="text-zinc-500 font-medium leading-relaxed">
							Masukkan email IPB Anda (@apps.ipb.ac.id). Kami akan mengirimkan tautan untuk mengatur ulang password Anda.
						</p>
					</div>

					{resetSent ? (
						<div className="space-y-8 py-4">
							<div className="flex flex-col items-center gap-4 text-center">
								<div className="w-16 h-16 bg-green-50 text-green-600 rounded-full flex items-center justify-center">
									<PiCheckCircle size={48} weight="fill" />
								</div>
								<div className="space-y-2">
									<h3 className="text-xl font-bold text-zinc-800">Email Terkirim!</h3>
									<p className="text-sm text-zinc-500">
										Silakan periksa kotak masuk email <strong>{email}</strong> untuk melanjutkan proses reset password.
									</p>
								</div>
							</div>
							<button 
								onClick={() => navigate("/reset-password")}
								className="w-full py-4 bg-[#002957] text-white rounded-xl font-bold transition-all hover:bg-[#001f42]"
							>
								Masukkan Token Reset
							</button>
						</div>
					) : (
						<form onSubmit={handleSubmit} className="space-y-8">
							<div className="space-y-2.5">
								<label className="text-sm font-bold text-[#002957] ml-1">Email IPB</label>
								<div className="relative group">
									<PiEnvelopeSimple className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-sky-600 transition-colors" size={22} />
									<input
										type="email"
										required
										value={email}
										onChange={(e) => setEmail(e.target.value)}
										placeholder="NIM@apps.ipb.ac.id"
										className="w-full pl-12 pr-4 py-4.5 bg-[#E8F1FF] border-none rounded-xl focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium text-zinc-800"
									/>
								</div>
							</div>

							{resetError && (
								<div className="p-3 bg-red-50 border border-red-100 rounded-lg text-red-600 text-xs font-bold">
									{resetError.response?.data?.detail || "Gagal mengirim permintaan reset password."}
								</div>
							)}

							<button
								type="submit"
								disabled={isRequestingReset}
								className="w-full py-4.5 bg-[#002957] hover:bg-[#001f42] text-white rounded-xl shadow-lg shadow-sky-950/20 font-bold text-base transition-all flex items-center justify-center gap-2 active:scale-[0.98] disabled:opacity-70"
							>
								{isRequestingReset ? (
									<PiSpinnerGap size={24} className="animate-spin" />
								) : (
									<>
										<span>Kirim Tautan Reset</span>
										<PiArrowRight size={20} weight="bold" />
									</>
								)}
							</button>
						</form>
					)}

					<div className="text-center pt-2">
						<button 
							onClick={() => navigate("/login")}
							className="text-[#002957] font-bold text-base hover:underline"
						>
							Kembali ke Halaman Masuk
						</button>
					</div>
				</div>

				{/* Footer Help */}
				<div className="mt-12 text-center">
					<p className="text-sm font-medium text-zinc-500">
						Butuh bantuan? <a href="#" className="text-sky-600 font-bold hover:underline">Hubungi Helpdesk CDA IPB</a>
					</p>
				</div>
			</div>
		</div>
	);
}

export default ForgotPassword;
