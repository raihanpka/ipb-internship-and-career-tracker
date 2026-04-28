function DataCard() {
	return (
		<div className="text-black bg-[#F2F2F2] h-auto pb-10 flex flex-col items-center">
			<div className="w-3/4 bg-[#D9D9D9] p-10 rounded-xl flex flex-col ">
				<div className="flex gap-3">
					<div className="px-2 py-1 bg-[#F2F2F2] rounded-sm">
						Data Diri
					</div>
					<div className="px-2 py-1 bg-[#F2F2F2] rounded-sm">
						Data Akademik
					</div>
				</div>
				<div className="bg-black h-1 my-2"></div>

				{/* 
				================
				=== PERSONAL ===
				================
				*/}
				<div>
					<div className="flex justify-between my-2">
						<div className="w-49/100">
							<div>Nama Lengkap</div>
							<input
								type="text"
								placeholder="Nama"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>NIK</div>
							<input
								type="text"
								placeholder="NIK"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="flex justify-between my-2">
						<div className="w-49/100">
							<div>Jenis Kelamin</div>
							<input
								type="text"
								placeholder="Jenis Kelamin"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>Agama</div>
							<input
								type="text"
								placeholder="Agama"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="flex justify-between my-2">
						<div className="w-49/100">
							<div>Tempat Lahir</div>
							<input
								type="text"
								placeholder="Tempat Lahir"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>Tanggal Lahir</div>
							<input
								type="date"
								placeholder="Tanggal Lahir"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="flex justify-between my-2">
						<div className="w-49/100">
							<div>No. Handphone</div>
							<input
								type="text"
								placeholder="No. Handphone"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>Email</div>
							<input
								type="email"
								placeholder="Email"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="my-2">
						<div>Biografi Singkat</div>
						<textarea
							placeholder="Biografi"
							className="bg-[#F2F2F2] w-full rounded-sm px-2 py-2 h-30"
						></textarea>
					</div>
				</div>

				{/* 
				==============
				=== ALAMAT ===
				==============
				*/}
				<div>
					<div className="bg-black h-1"></div>

					<div className="flex justify-between my-2">
						<div className="w-49/100">
							<div>Alamat Sesuai KTP</div>
							<input
								type="text"
								placeholder="Alamat Sesuai KTP"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>Kode Pos</div>
							<input
								type="text"
								placeholder="Kode Pos"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="flex justify-between my-2">
						<div className="w-49/100">
							<div>Provinsi</div>
							<input
								type="text"
								placeholder="Provinsi"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>Kabupaten/Kota</div>
							<input
								type="text"
								placeholder="Kabupaten/Kota"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="bg-black h-1"></div>
					<div className="flex justify-between mt-2">
						<div className="w-49/100">
							<div>Alamat Domisili</div>
							<input
								type="text"
								placeholder="Alamat Domisili"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
							<div className="flex mt-1">
								<input
									type="checkbox"
									className="m-1 size-4 rounded "
								></input>
								<div>Alamat sama dengan KTP</div>
							</div>
						</div>
						<div className="w-49/100">
							<div>Kode Pos</div>
							<input
								type="text"
								placeholder="Kode Pos"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
					<div className="flex justify-between mb-2">
						<div className="w-49/100">
							<div>Provinsi</div>
							<input
								type="text"
								placeholder="Provinsi"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
						<div className="w-49/100">
							<div>Kabupaten/Kota</div>
							<input
								type="text"
								placeholder="Kabupaten/Kota"
								className="bg-[#F2F2F2] w-full rounded-sm px-2 h-10"
							/>
						</div>
					</div>
				</div>
				{/* 
				====================
				=== SOSIAL MEDIA ===
				====================
				*/}
				<div>
					<div className="bg-black h-1"></div>

					<div className="flex justify-between my-2 items-baseline-last">
						<div className="w-49/100">
							<div>Sosial Media</div>
							<div className="bg-[#F2F2F2] w-full rounded-sm h-10 flex">
								<div className="bg-gray-500 h-10 w-10 rounded-l-sm flex justify-center items-center">
									<img
										src="src\assets\instagram.svg"
										className="size-7"
									/>
								</div>
								<input
									type="text"
									placeholder="Instagram"
									className="flex-1 rounded-sm px-2 h-10"
								/>
							</div>
						</div>
						<div className="w-49/100">
							<div className="bg-[#F2F2F2] w-full rounded-sm h-10 flex">
								<div className="bg-gray-500 h-10 w-10 rounded-l-sm flex justify-center items-center">
									<img
										src="src\assets\facebook.svg"
										className="size-7"
									/>
								</div>
								<input
									type="text"
									placeholder="Facebook"
									className="flex-1 rounded-sm px-2 h-10"
								/>
							</div>
						</div>
					</div>
					<div className="flex justify-between mt-4 mb-2 items-baseline-last">
						<div className="w-49/100">
							<div className="bg-[#F2F2F2] w-full rounded-sm h-10 flex">
								<div className="bg-gray-500 h-10 w-10 rounded-l-sm flex justify-center items-center">
									<img
										src="src\assets\linkedin.svg"
										className="size-7"
									/>
								</div>
								<input
									type="text"
									placeholder="Linkedin"
									className="flex-1 rounded-sm px-2 h-10"
								/>
							</div>
						</div>
						<div className="w-49/100">
							<div className="bg-[#F2F2F2] w-full rounded-sm h-10 flex">
								<div className="bg-gray-500 h-10 w-10 rounded-l-sm flex justify-center items-center">
									<img
										src="src\assets\twitter.svg"
										className="size-7"
									/>
								</div>
								<input
									type="text"
									placeholder="Twitter"
									className="flex-1 rounded-l-sm px-2 h-10"
								/>
							</div>
						</div>
					</div>
				</div>
				<div>
					<div className="flex justify-end">
						<button className="bg-black  text-white px-4 py-1 mt-3 rounded-sm">Simpan</button>
					</div>
				</div>
			</div>
		</div>
	);
}
export default DataCard;
