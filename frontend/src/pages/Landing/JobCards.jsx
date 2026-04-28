import axios from "axios";
import { useEffect, useState } from "react";

import { Swiper, SwiperSlide } from "swiper/react";

import { Pagination, Navigation } from "swiper/modules";

// Import Swiper styles
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";

function JobCards() {
	const [jobs, setJobs] = useState([]);

	useEffect(() => {
		getAllData();
	});

	async function getAllData() {
		const response = await axios.get(API_URL);
		setJobs(response.data);
	}

	const chunkArray = (arr, size) => {
		const chunks = [];
		for (let i = 0; i < arr.length; i += size) {
			chunks.push(arr.slice(i, i + size));
		}
		return chunks;
	};

	const userChunks = chunkArray(jobs.slice(0, 8), 2);

	const API_URL = "http://localhost:3000/vacancy";

	return (
		<div className="text-black bg-[#F2F2F2] h-auto flex flex-col items-center py-10">
			<div className="my-10  text-2xl font-bold">
				Temukan Karir yang Sesuai dengan Anda
			</div>
			<div className="w-3/4">
				<div className="grid grid-auto-rows grid-cols-3 gap-10">
					{jobs.slice(0, 6).map((job) => (
						<div className="bg-[#D9D9D9] min-w-65 p-4 rounded-xl">
							<div className="flex justify-between">
								<div>
									<div className="font-bold w-35 truncate">
										{job.name}
									</div>
									<div className="text-sm">{job.company}</div>
									<div className="text-sm w-35 truncate">
										{job.address}
									</div>
									<div className="flex gap-2">
										<div className="text-xs bg-[#F2F2F2] py-1 px-2 rounded-full">
											Internship
										</div>
										<div className="text-xs bg-[#F2F2F2] py-1 px-2 rounded-full">
											onsite
										</div>
									</div>
								</div>
								<div className="bg-[#F2F2F2] size-20 rounded-xl "></div>
							</div>
							<div className="flex justify-between items-baseline">
								<div className="text-xs">
									{job.index} hari yang lalu
								</div>
								<div className="text-sm bg-[#F2F2F2] py-1 px-4 rounded-full">
									Detail
								</div>
							</div>
						</div>
					))}
				</div>
				<div className="w-full h-10 bg-[#D9D9D9] mt-5 flex justify-center items-center rounded-xl">
					{" "}
					Selengkapnya
				</div>
			</div>

			{/* ===== TEST 2 ===== */}
			{/* <div className="w-3/4 m-auto py-10">
				<Swiper
					modules={[Pagination, Navigation]}
					spaceBetween={20}
					slidesPerView={3}
					navigation
				>
					{userChunks.map((chunk, index) => (
						<SwiperSlide key={index}>
							
							<div className="grid grid-auto-rows grid-cols-1 gap-3.75 ">
								{" "}
								{chunk.map((job) => (
									<div className="bg-[#D9D9D9] min-w-65 p-4 rounded-xl">
										<div className="flex justify-between">
											<div>
												<div className="font-bold w-35 truncate">
													{job.name}
												</div>
												<div className="text-sm">
													{job.company}
												</div>
												<div className="text-sm w-35 truncate">
													{job.address}
												</div>
												<div className="flex gap-2">
													<div className="text-xs bg-[#F2F2F2] py-1 px-2 rounded-full">
														Internship
													</div>
													<div className="text-xs bg-[#F2F2F2] py-1 px-2 rounded-full">
														onsite
													</div>
												</div>
											</div>
											<div className="bg-[#F2F2F2] size-20 rounded-xl "></div>
										</div>
										<div className="flex justify-between items-baseline">
											<div className="text-xs">
												{job.index} hari yang lalu
											</div>
											<div className="text-sm bg-[#F2F2F2] py-1 px-4 rounded-full">
												Detail
											</div>
										</div>
									</div>
								))}
							</div>
						</SwiperSlide>
					))}
				</Swiper>
			</div> 
			*/}

			{/* ======= FINAL =======  */}
		</div>
	);
}

export default JobCards;
