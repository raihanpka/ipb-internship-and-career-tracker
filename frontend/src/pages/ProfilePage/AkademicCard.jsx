import axios from "axios";
import { useEffect, useState } from "react";

function AcademicCard() {
	const [educations, setEducations] = useState([]);

	const API_URL = "http://localhost:3000/education";

	useEffect(() => {
		getAllData();
	}, []);

	// Display Data
	async function getAllData() {
		const response = await axios.get(API_URL);
		setEducations(response.data);
	}

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
				<div>Pendidikan</div>
				<ul className="overflow-x-auto whitespace-nowrap">
					<div className="bg-[#F2F2F2] rounded-sm flex gap-1 my-1 h-10 items-center w-265">
						<div className="flex justify-center font-bold min-w-20">
							No
						</div>
						<div className="flex justify-center font-bold w-70">
							Nama Institusi
						</div>
						<div className="flex justify-center font-bold w-20">
							Jenjang
						</div>
						<div className="flex justify-center font-bold w-70">
							Jurusan
						</div>
						<div className="flex justify-center font-bold w-15">
							Nilai
						</div>
						<div className="flex justify-center font-bold w-35">
							Tanggal Lulus
						</div>
						<div className="flex justify-center font-bold w-25">
							Aksi
						</div>
					</div>
					<div className="bg-[#F2F2F2] rounded-sm w-265">
						{/* <div className="h-0.5 my-2 mx-3 bg-black w-271"></div> */}
						{educations.map((educ) => (
							<li>
								<div className="flex gap-1 items-center my-2 py-2">
									<div className="bg-blue-300 flex justify-center w-20 px-2">
										{educ.index + 1}
									</div>
									<div className="bg-blue-300 w-70 px-2 text-wrap">
										{educ.name}
									</div>
									<div className="bg-blue-300 flex justify-center w-20 px-2">
										{educ.jenjang}
									</div>
									<div className="bg-blue-300  w-70 px-2">
										{educ.jurusan}
									</div>
									<div className="bg-blue-300 flex justify-center w-15 px-2">
										{educ.nilai}
									</div>
									<div className="bg-blue-300 flex justify-center w-35 px-2">
										{educ.lulus}
									</div>
									<div className="bg-blue-300 flex justify-center w-25 px-2">
										Edit / Delete
									</div>
								</div>
							</li>
						))}
					</div>
				</ul>
				<div>+ Tambah Pendidikan</div>
			</div>
		</div>
	);
}

export default AcademicCard;

{
	/* 
	==============================
	========= OPSI TABEL =========
	==============================

	<div>Pendidikan</div>
<ul className="overflow-x-auto whitespace-nowrap">
	<div className="bg-[#F2F2F2] w-max rounded-sm flex gap-1 my-1">
		<div className="flex justify-center min-w-20">No</div>
		<div className="flex justify-center min-w-70">
			Nama Institusi
		</div>
		<div className="flex justify-center min-w-20">
			Jenjang
		</div>
		<div className="flex justify-center min-w-70">
			Jurusan
		</div>
		<div className="flex justify-center min-w-20">
			Nilai
		</div>
		<div className="flex justify-center min-w-40">
			Tanggal Lulus
		</div>
		<div className="flex justify-center min-w-25">Aksi</div>
	</div>
	{educations.map((educ) => (
		<li className="bg-[#F2F2F2] w-271 rounded-sm">
			<div className="flex gap-1 my-1">
				<div className="flex justify-center min-w-20 px-2">
					{educ.index + 1}
				</div>
				<div className="min-w-70 px-2 text-wrap">
					{educ.name}
				</div>
				<div className="flex justify-center min-w-20 px-2">
					{educ.jenjang}
				</div>
				<div className=" min-w-70 px-2">
					{educ.jurusan}
				</div>
				<div className="flex justify-center min-w-20 px-2">
					{educ.nilai}
				</div>
				<div className="flex justify-center min-w-40 px-2">
					{educ.lulus}
				</div>
				<div className="flex justify-center min-w-25 px-2">
					Edit / Delete
				</div>
			</div>
		</li>
	))}
</ul> */
}
