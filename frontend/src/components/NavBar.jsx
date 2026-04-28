function NavBar() {
	return (
		<div>
			<nav class="text-black bg-[#D9D9D9] fixed w-full z-20 top-0 inset-s-0 flex justify-center shadow-sm">
				<div className="w-9/12 h-18 flex justify-between items-center">
					<div className="font-bold text-4xl">LARAS</div>
					<div className="flex gap-10 text-xl">
						<p>Home</p>
						<p>Karier</p>
						<p>Logbook</p>
						<div className="flex gap-3">
							<div>O</div>
							<button className="bg-[#F2F2F2] px-4 rounded-full">
								Profile
							</button>
						</div>
					</div>
				</div>
			</nav>
			<div className="bg-[#D9D9D9] h-18"></div>
		</div>
	);
}

export default NavBar;
