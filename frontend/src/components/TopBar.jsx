import { useState } from "react";
import { PiBell, PiUserCircle, PiTrash } from "react-icons/pi";
import { useNotifications } from "../hooks/useNotifications";
import { useAuth } from "../hooks/useAuth";
import { NavLink } from "react-router-dom";
import { resolveBackendAssetUrl } from "../utils/assetUrl";

const TopBar = () => {
	const { unreadCount, notifications, markAsRead, deleteNotification } = useNotifications();
	const { user } = useAuth();
	const [showNotifications, setShowNotifications] = useState(false);

	const handleMarkAllRead = (e) => {
		e.stopPropagation();
		notifications
			.filter((n) => n.status !== "READ")
			.forEach((n) => markAsRead(n.id));
	};

	const formatNotifTime = (dateString) => {
		if (!dateString) return "";
		const date = new Date(dateString);
		return date.toLocaleDateString("id-ID", {
			day: "numeric",
			month: "short",
			year: "numeric",
			hour: "2-digit",
			minute: "2-digit"
		});
	};

	return (
		<nav className="flex items-center justify-between w-full h-14 px-4 sm:h-16 sm:px-6 bg-white border-b border-gray-100 font-jakarta relative">
			<div className="flex items-center gap-2 lg:hidden">
				<img src="/logo/laras.png" alt="LARAS" className="w-8 h-8 object-contain" />
				<span className="text-base font-[900] tracking-tight text-sky-950">LARAS</span>
			</div>
			<div className="flex items-center gap-3 sm:gap-5 ml-auto">
				{/* Notifikasi */}
				<div className="relative">
					<button 
						onClick={() => setShowNotifications(!showNotifications)}
						className="relative flex items-center justify-center p-1.5 text-zinc-500 hover:text-sky-700 hover:bg-slate-50 rounded-xl transition-all"
					>
						<PiBell size={24} />
						{unreadCount > 0 && (
							<span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full"></span>
						)}
					</button>

					{/* Dropdown Notifikasi */}
					{showNotifications && (
						<>
							{/* Overlay to close on click outside */}
							<div className="fixed inset-0 z-10" onClick={() => setShowNotifications(false)}></div>
							
							<div className="fixed left-4 right-4 top-16 bg-white rounded-2xl shadow-[0px_8px_24px_0px_rgba(0,41,87,0.12)] border border-slate-100 overflow-hidden z-20 sm:absolute sm:left-auto sm:right-0 sm:top-auto sm:mt-3 sm:w-80">
								<div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
									<div className="flex items-center gap-2">
										<span className="font-bold text-sky-950 text-sm">Notifikasi</span>
										{unreadCount > 0 && (
											<span className="bg-sky-100 text-sky-800 text-[10px] font-bold px-1.5 py-0.5 rounded-full">
												{unreadCount} Baru
											</span>
										)}
									</div>
									{unreadCount > 0 && (
										<button 
											onClick={handleMarkAllRead}
											className="text-[10px] text-sky-700 font-bold hover:underline"
										>
											Tandai semua dibaca
										</button>
									)}
								</div>
								
								<div className="max-h-96 overflow-y-auto divide-y divide-slate-50">
									{notifications.length > 0 ? (
										notifications.map((notif) => {
											const isUnread = notif.status !== "READ";
											return (
												<div 
													key={notif.id} 
													onClick={() => {
														if (isUnread) markAsRead(notif.id);
													}}
													className={`p-4 hover:bg-slate-50 transition-colors cursor-pointer flex gap-3 relative group ${isUnread ? "bg-sky-50/40" : "bg-white"}`}
												>
													{/* Dot indicator */}
													{isUnread && (
														<span className="absolute top-5 left-2 w-1.5 h-1.5 bg-sky-600 rounded-full shrink-0"></span>
													)}
													
													<div className={`flex-1 ${isUnread ? "pl-2" : ""}`}>
														<div className="flex justify-between items-start gap-2">
															<p className={`text-xs text-zinc-800 leading-snug line-clamp-2 ${isUnread ? "font-[800]" : "font-medium"}`}>
																{notif.title}
															</p>
															{/* Delete Button */}
															<button
																onClick={(e) => {
																	e.stopPropagation();
																	deleteNotification(notif.id);
																}}
																className="text-zinc-400 hover:text-red-600 p-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
																title="Hapus"
															>
																<PiTrash size={14} />
															</button>
														</div>
														<p className="text-[11px] text-zinc-500 mt-1 leading-normal font-medium line-clamp-2">
															{notif.message}
														</p>
														<span className="text-[9px] text-zinc-400 mt-1.5 block">
															{formatNotifTime(notif.sent_at || notif.scheduled_at)}
														</span>
													</div>
												</div>
											);
										})
									) : (
										<div className="p-10 text-center text-zinc-400">
											<PiBell className="mx-auto text-zinc-300 mb-2" size={32} />
											<p className="text-xs">Tidak ada notifikasi baru</p>
										</div>
									)}
								</div>
							</div>
						</>
					)}
				</div>

				{/* Profil */}
				<NavLink to="/app/profil" className="cursor-pointer">
					<div className="w-10 h-10 overflow-hidden rounded-full border-2 border-transparent hover:border-sky-700 transition-all bg-slate-100 flex items-center justify-center shadow-sm">
						{user?.avatar_url ? (
							<img 
								src={resolveBackendAssetUrl(user.avatar_url)} 
								alt="Profile" 
								className="w-full h-full object-cover"
								referrerPolicy="no-referrer"
							/>
						) : (
							<PiUserCircle size={32} className="text-zinc-600" />
						)}
					</div>
				</NavLink>
			</div>
		</nav>
	);
};

export default TopBar;
