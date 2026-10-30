import { Routes, Route, Navigate, NavLink } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Login from "./pages/Login.jsx";
import StudentDashboard from "./pages/StudentDashboard.jsx";
import Quiz from "./pages/Quiz.jsx";
import Chat from "./pages/Chat.jsx";
import Resources from "./pages/Resources.jsx";
import Integrations from "./pages/Integrations.jsx";
import TeacherDashboard from "./pages/TeacherDashboard.jsx";
import AdminPanel from "./pages/AdminPanel.jsx";

const NAV = {
  student: [["/", "Dashboard"], ["/quiz", "Adaptive quiz"], ["/chat", "AI tutor"], ["/resources", "Resources"], ["/integrations", "Courses"]],
  teacher: [["/teacher", "Class overview"], ["/resources", "Resources"], ["/chat", "AI tutor"], ["/integrations", "Courses"]],
  admin: [["/admin", "Users"], ["/teacher", "Class overview"], ["/resources", "Resources"], ["/integrations", "Courses"]],
};
const HOME = { student: "/", teacher: "/teacher", admin: "/admin" };

function Shell({ roles, children }) {
  const { user, loading, logout } = useAuth();
  if (loading) return <p className="center">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to={HOME[user.role]} replace />;
  return (
    <div className="app">
      <aside className="side">
        <h1>AdaptLearn</h1>
        <nav>
          {NAV[user.role].map(([to, label]) => (
            <NavLink key={to} to={to} end className={({ isActive }) => (isActive ? "on" : "")}>{label}</NavLink>
          ))}
        </nav>
        <div className="who">
          <strong>{user.name}</strong>
          <span>{user.role}</span>
          <button className="ghost" onClick={logout}>Sign out</button>
        </div>
      </aside>
      <main className="main">{children}</main>
    </div>
  );
}

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={HOME[user.role]} replace /> : <Login />} />
      <Route path="/" element={<Shell roles={["student"]}><StudentDashboard /></Shell>} />
      <Route path="/quiz" element={<Shell roles={["student"]}><Quiz /></Shell>} />
      <Route path="/chat" element={<Shell><Chat /></Shell>} />
      <Route path="/resources" element={<Shell><Resources /></Shell>} />
      <Route path="/integrations" element={<Shell><Integrations /></Shell>} />
      <Route path="/teacher" element={<Shell roles={["teacher", "admin"]}><TeacherDashboard /></Shell>} />
      <Route path="/admin" element={<Shell roles={["admin"]}><AdminPanel /></Shell>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
