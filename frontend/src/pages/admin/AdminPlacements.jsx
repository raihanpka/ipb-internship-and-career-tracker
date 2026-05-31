import { useState } from 'react';
import { format } from 'date-fns';
import { id } from 'date-fns/locale';
import { useAdminPlacements } from '../../hooks/useAdminPlacements';
import { 
  PiMagnifyingGlass,
  PiBuildings,
  PiCalendarBlank,
  PiUserList,
  PiSpinnerGap,
  PiWarning 
} from 'react-icons/pi';

function AdminPlacements() {
  const [searchTerm, setSearchTerm] = useState("");

  const {
    placements,
    isLoadingPlacements: isLoading,
    isErrorPlacements: isError
  } = useAdminPlacements();

  const filteredPlacements = placements.filter(placement => {
    const term = searchTerm.toLowerCase();
    const companyMatch = placement.company_name?.toLowerCase().includes(term);
    const statusMatch = placement.status?.toLowerCase().includes(term);
    const nameMatch = placement.student_name?.toLowerCase().includes(term);
    const nimMatch = placement.student_nim?.toLowerCase().includes(term);
    return companyMatch || statusMatch || nameMatch || nimMatch;
  });

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center font-jakarta">
        <PiSpinnerGap size={40} className="animate-spin text-sky-950" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="h-full flex items-center justify-center font-jakarta">
        <div className="flex flex-col items-center gap-2 text-rose-600">
          <PiWarning size={48} />
          <p className="font-bold">Gagal memuat data penempatan.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="font-jakarta pb-20">
      <div className="mb-8 bg-sky-950 p-8 rounded-[2rem] text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10">
          <h1 className="text-3xl sm:text-4xl font-extrabold">Data Penempatan (Placement)</h1>
          <p className="text-sky-100/80 mt-3 max-w-2xl leading-relaxed">
            Daftar seluruh mahasiswa yang sedang atau telah menjalankan program magang. 
            <strong>Catatan:</strong> Data di sini otomatis ditambahkan ketika Anda memverifikasi lamaran mahasiswa (mengubah status menjadi ACCEPTED) pada menu <strong>Verifikasi</strong>.
          </p>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-sky-400/20 rounded-full blur-3xl -mr-20 -mt-20"></div>
      </div>

      {/* Header Actions */}
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 mb-6 bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
        <div className="relative w-full md:w-96">
          <PiMagnifyingGlass className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" size={20} />
          <input
            type="text"
            placeholder="Cari nama, NIM, perusahaan, atau status..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-sky-500 outline-none transition-all font-medium"
          />
        </div>
        <div className="w-full md:w-auto flex items-center justify-center gap-2 text-sm font-bold text-sky-950 bg-sky-50 px-5 py-3 rounded-xl border border-sky-100">
          <PiUserList size={20} />
          Total Penempatan: {filteredPlacements.length}
        </div>
      </div>

      {/* Content */}
      {filteredPlacements.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-2xl shadow-sm border border-slate-100">
          <PiBuildings size={64} className="mx-auto text-zinc-300 mb-4" />
          <h2 className="text-xl font-bold text-slate-700">Tidak Ada Data</h2>
          <p className="text-slate-500 mt-2">Belum ada penempatan yang sesuai dengan pencarian Anda.</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="bg-sky-50/50 text-slate-600 border-b border-slate-100">
                <tr>
                  <th className="p-5 font-bold uppercase tracking-wider text-xs">Mahasiswa</th>
                  <th className="p-5 font-bold uppercase tracking-wider text-xs">Perusahaan</th>
                  <th className="p-5 font-bold uppercase tracking-wider text-xs">Periode Magang</th>
                  <th className="p-5 font-bold uppercase tracking-wider text-xs">Pembimbing Lapangan</th>
                  <th className="p-5 font-bold uppercase tracking-wider text-xs">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredPlacements.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                    <td className="p-5">
                      <div className="flex flex-col">
                        <span className="font-bold text-sky-950 text-base">{p.student_name || "Nama Tidak Diketahui"}</span>
                        <span className="text-xs text-slate-500 font-medium">{p.student_nim || p.student_id.substring(0, 8).toUpperCase()}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <PiBuildings size={18} className="text-zinc-400" />
                        <span className="font-bold text-slate-700">{p.company_name || "Perusahaan"}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2 text-slate-600">
                        <PiCalendarBlank size={16} />
                        <span>
                          {format(new Date(p.start_date), "dd MMM yyyy", { locale: id })} - {format(new Date(p.end_date), "dd MMM yyyy", { locale: id })}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 text-slate-600">
                      {p.external_supervisor_name || "-"}
                    </td>
                    <td className="p-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded text-xs font-bold uppercase ${
                        p.status === "ACTIVE" 
                          ? "bg-emerald-100 text-emerald-800" 
                          : "bg-slate-100 text-slate-800"
                      }`}>
                        {p.status === "ACTIVE" ? "Aktif" : p.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPlacements;
