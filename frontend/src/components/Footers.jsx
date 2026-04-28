import { FaInstagram, FaLinkedin, FaWhatsapp, FaYoutube } from "react-icons/fa";

function Footers() {
	return (
		<div className="text-black bg-[#D9D9D9] h-auto py-10  flex flex-col items-center">
			<div className="w-3/4 flex justify-between">
				<div className="min-w-90">
					<div className=" flex justify-between m-1">
						<div className="font-bold text-5xl">LARAS</div>
						<div>
							Lintasan Arah dan
							<br />
							Rencana Aktualisasi Studi
						</div>
					</div>
					<div className="bg-black h-1 my-2"></div>
					<div className="text-[13px]">
						Gedung Andi Hakim Nasoetion Kampus IPB Dramaga - Bogor
						<br />
						Jawa Barat, Kabupaten Bogor
						<br />
						Indonesia 16680
					</div>
				</div>

				<div>
					<div className="font-bold">Cutomer Service</div>
                    <div>Phone : 082135244191</div>
                    <div>laras@apps.ipb.ac.id</div>
                    <div>larasipb@apps.ipb.ac.id</div>
                    <div className="flex gap-3.5 mt-2">
						<FaInstagram size={30} />
						<FaLinkedin size={30} />
						<FaWhatsapp size={30} />
						<FaYoutube size={30} />
                    </div>
				</div>
			</div>
		</div>
	);
}

export default Footers;
