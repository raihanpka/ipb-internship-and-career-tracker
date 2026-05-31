import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
// Layout component replaced by AppShell for protected routes
import Landing from "./pages/public/Landing";
import AppShell from "./layouts/AppShell";
import Wishlist from "./pages/portal/Wishlist";
import Login from "./pages/auth/Login";
import Registration from "./pages/auth/Registrasi";
import ForgotPassword from "./pages/auth/ForgotPassword";
import ResetPassword from "./pages/auth/ResetPassword";
import VerifyEmail from "./pages/auth/VerifyEmail";
import Dashboard from "./pages/portal/Dashboard";
import Lowongan from "./pages/portal/Lowongan";
import Lamaran from "./pages/portal/Lamaran";
import Jurnal from "./pages/portal/Jurnal";
import Laporan from "./pages/portal/Laporan";
import Profil from "./pages/portal/Profil";
import DetailLowongan from "./pages/portal/DetailLowongan";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminVerification from "./pages/admin/AdminVerification";
import AdminVacancies from "./pages/admin/AdminVacancies";
import AdminCompanies from "./pages/admin/AdminCompanies";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminMasterData from "./pages/admin/AdminMasterData";
import AdminPlacements from "./pages/admin/AdminPlacements";
import PublicLowongan from "./pages/public/PublicLowongan";

import { useAuth } from "./hooks/useAuth";
import { PiSpinnerGap } from "react-icons/pi";

// Component to protect routes that require specific roles
const RoleGuard = ({ children, allowedRoles }) => {
  const { user, isLoading, isError } = useAuth();
  const token = localStorage.getItem('token');

  if (!token) return <Navigate to="/login" replace />;
  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#F8F9FF]">
      <PiSpinnerGap size={48} className="animate-spin text-sky-950" />
    </div>
  );

  if (isError || !user) {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('refresh_token');
    return <Navigate to="/login" replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    // Redirect based on role if they try to access unauthorized area
    return user?.role === 'ADMIN' 
      ? <Navigate to="/app/admin/dashboard" replace /> 
      : <Navigate to="/app/home" replace />;
  }

  return children;
};

// Component to protect routes that require authentication
const ProtectedRoute = ({ children }) => {
  const { isLoading, isError } = useAuth();
  const token = localStorage.getItem('token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8F9FF]">
        <div className="flex flex-col items-center gap-4">
          <PiSpinnerGap size={48} className="animate-spin text-sky-950" />
          <p className="text-sm font-bold text-sky-950/50 uppercase tracking-widest">Memuat Aplikasi...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    // Jika ada token tapi API return error (misal expired), bersihkan token & login ulang
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('refresh_token');
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Component to redirect authenticated users away from public auth pages
const PublicRoute = ({ children }) => {
  const { user } = useAuth();
  const token = localStorage.getItem('token');
  if (token) {
    if (user?.role === 'ADMIN') {
      return <Navigate to="/app/admin/dashboard" replace />;
    }
    return <Navigate to="/app/home" replace />;
  }
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Guest / Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/lowongan" element={<PublicLowongan />} />
        <Route path="/detail/:vacancyId" element={<DetailLowongan />} />
        
        {/* Authentication Routes */}
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/registration" element={<PublicRoute><Registration /></PublicRoute>} />
        <Route path="/forgot-password" element={<PublicRoute><ForgotPassword /></PublicRoute>} />
        <Route path="/reset-password" element={<PublicRoute><ResetPassword /></PublicRoute>} />
        <Route path="/verify-email" element={<VerifyEmail />} />

        {/* App (protected) with nested routes */}
        <Route path="/app" element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
          {/* Default redirect based on role */}
          <Route index element={<Navigate to="/app/home" replace />} />
          
          {/* Admin Routes (Strictly guarded) */}
          <Route path="admin/dashboard" element={<RoleGuard allowedRoles={['ADMIN']}><AdminDashboard /></RoleGuard>} />
          <Route path="admin/verifikasi" element={<RoleGuard allowedRoles={['ADMIN']}><AdminVerification /></RoleGuard>} />
          <Route path="admin/lowongan" element={<RoleGuard allowedRoles={['ADMIN']}><AdminVacancies /></RoleGuard>} />
          <Route path="admin/perusahaan" element={<RoleGuard allowedRoles={['ADMIN']}><AdminCompanies /></RoleGuard>} />
          <Route path="admin/mahasiswa" element={<RoleGuard allowedRoles={['ADMIN']}><AdminUsers /></RoleGuard>} />
          <Route path="admin/master-data" element={<RoleGuard allowedRoles={['ADMIN']}><AdminMasterData /></RoleGuard>} />
          <Route path="admin/penempatan" element={<RoleGuard allowedRoles={['ADMIN']}><AdminPlacements /></RoleGuard>} />
          
          {/* Student Routes (Strictly guarded) */}
          <Route path="home" element={<RoleGuard allowedRoles={['STUDENT']}><Dashboard /></RoleGuard>} />
          <Route path="lowongan" element={<RoleGuard allowedRoles={['STUDENT', 'ADMIN']}><Lowongan /></RoleGuard>} />
          <Route path="wishlist" element={<RoleGuard allowedRoles={['STUDENT']}><Wishlist /></RoleGuard>} />
          <Route path="lamaran" element={<RoleGuard allowedRoles={['STUDENT']}><Lamaran /></RoleGuard>} />
          <Route path="jurnal" element={<RoleGuard allowedRoles={['STUDENT']}><Jurnal /></RoleGuard>} />
          <Route path="laporan" element={<RoleGuard allowedRoles={['STUDENT']}><Laporan /></RoleGuard>} />
          <Route path="profil" element={<RoleGuard allowedRoles={['STUDENT']}><Profil /></RoleGuard>} />
          <Route path="detail/:vacancyId" element={<RoleGuard allowedRoles={['STUDENT', 'ADMIN']}><DetailLowongan /></RoleGuard>} />
        </Route>
        
        {/* Fallback redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
