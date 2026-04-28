import axios from "axios";
import { useEffect, useState } from "react";

import { Swiper, SwiperSlide } from "swiper/react";

import { Pagination, Navigation } from "swiper/modules";

// Import Swiper styles
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";

function CompanyCards() {
	const [companies, setCompanies] = useState([]);

	useEffect(() => {
		getAllData();
	});

	async function getAllData() {
		const response = await axios.get(API_URL);
		setCompanies(response.data);
	}

	const API_URL = "http://localhost:3000/company";

	return (
		<div className="text-black bg-[#F2F2F2] h-auto p-10  flex flex-col items-center">
			<div className="items-center text-2xl font-bold text-center my-10">
				Bergabung Bersama Perusahaan
				<br />
				Terbaik di Indonesia
			</div>

	

			<div className="w-3/4">
				<Swiper
					modules={[Pagination, Navigation]}
					spaceBetween={20}
					slidesPerView={3}
					navigation
					loop={true}
				>
					{companies.slice(0,6).map((company) => (
						<SwiperSlide>
							<div className="flex justify-center">
								<div className="bg-[#D9D9D9] w-60 h-80 rounded-xl p-4 flex flex-col items-center">
									<div className="bg-[#F2F2F2] w-full h-30 rounded-xl"></div>
									<div className="font-medium text-center">
										{company.name}
									</div>
									<div className="text-center h-25 flex items-center">
										{company.motto}
									</div>
									<button className="bg-[#F2F2F2] px-4 py-2 rounded-full w-1/2">
										Detail
									</button>
								</div>
							</div>
						</SwiperSlide>
					))}
				</Swiper>
			</div>
		</div>
	);
}

export default CompanyCards;
