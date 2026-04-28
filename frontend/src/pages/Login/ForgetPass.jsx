function ForgetPass() {
	return (
		<div className="text-black bg-[#F2F2F2] h-screen flex items-center justify-center">
			<div className="relative h-full w-9/12 flex flex-col justify-center items-center">
				<div className=" w-2/4 flex flex-col gap-3">
					<div className=" flex flex-col items-center">
						<p className="font-medium text-6xl">Laras</p>
						<p className="font-medium text-4xl">Lupa Password</p>
					</div>
					<div>
						<p>Email</p>
						<input
							type="email"
							placeholder="Email"
							className="w-full bg-[#D9D9D9] h-10 rounded-md my-1 p-2"
						/>
					</div>
					<button className="text-white w-full bg-black h-10 rounded-md ">
						Daftar
					</button>
				</div>
				<div className="h-20"></div>

				{/* Footer */}
				<div className="absolute bottom-10 right-10 left-10 flex justify-between items-center">
					<p className="text-2xl font-bold">Laras</p>
					<div className="flex gap-5">
						<p>Syarat & Ketentuan</p>
						<p>Kebijakan Privasi</p>
						<p>Tentang Laras</p>
					</div>
					<p>@2026 Laras. All rights reserved</p>
				</div>
			</div>
		</div>
	);
}

export default ForgetPass;
