function HeroSec() {
	return(
	<div className="text-black bg-[#F2F2F2] h-screen flex items-center justify-center">
		<div className="w-6/10  flex flex-col items-center">
			<h1 className="text-5xl font-bold">LARAS</h1>
			<p className="text-3xl font-bold">
				Temukan Kesempatan Berkarir Anda
			</p>
			<input
				type="text"
				placeholder="Search"
				className="w-full bg-[#D9D9D9] h-20 rounded-full my-10 px-15 text-xl"
			/>
			<div className="flex gap-7">
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					Tech
				</div>
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					Accounting
				</div>
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					Creative
				</div>
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					HR
				</div>
			</div>
			<div className="flex gap-7 mt-7">
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					Operation
				</div>
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					Sales
				</div>
				<div className="bg-[#D9D9D9] text-xl p-5 rounded-xl w-50 flex justify-center">
					Engineer
				</div>
			</div>
		</div>
	</div>
	)
}

export default HeroSec;
