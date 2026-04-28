function LoginPage() {
	return (
		<div className="text-black bg-[#F2F2F2] h-screen flex items-center justify-center">
			<div className=" relative h-full pt-13 w-9/12">
				<div className=" text-black text-6xl font-bold">Laras</div>
				<div className=" w-full flex justify-between">
					<div className=" w-49/100">
						<p className="font-bold text-4xl">
							Selamat Datang di Laras!
						</p>
						<div className="bg-[#D9D9D9] h-100 mt-3 rounded-xl"></div>
					</div>
					<div className="w-49/100">
						<div className="text-xl bg-[#D9D9D9] h-full rounded-xl p-7 flex justify-center items-center">
							<div className="flex flex-col gap-7 w-full">
								<div>
									<p>Email</p>
									<input
										type="email"
										placeholder="Email"
										className="w-full bg-[#F2F2F2] h-10 rounded-md my-1 p-2"
									/>
								</div>
								<div>
									<div className="flex justify-between">
										<p>Password</p>
										<p className="underline">
											Lupa Password?
										</p>
									</div>
									<input
										type="password"
										placeholder="Password"
										className="w-full bg-[#F2F2F2] h-10 rounded-md my-1 p-2"
									/>
								</div>
								<button className="text-white w-full bg-black h-10 rounded-md ">
									Masuk
								</button>
								<div className="flex justify-center">
									<p>Belum memiliki akun?</p>
									<p className="underline">Daftar</p>
								</div>
							</div>
						</div>
					</div>
				</div>
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

export default LoginPage;
