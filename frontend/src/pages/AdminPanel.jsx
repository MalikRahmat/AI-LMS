import { useEffect, useState } from "react";
import api, { errMsg } from "../api";

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [f, setF] = useState({ name: "", email: "", password: "", role: "teacher" });
  const [msg, setMsg] = useState({ ok: "", err: "" });

  const load = () => {
    api.get("/admin/users").then((r) => setUsers(r.data.users));
    api.get("/admin/stats").then((r) => setStats(r.data));
  };
  useEffect(load, []);

  const create = async (e) => {
    e.preventDefault();
    try { await api.post("/admin/users", f); setMsg({ ok: "User created", err: "" }); setF({ ...f, name: "", email: "", password: "" }); load(); }
    catch (x) { setMsg({ ok: "", err: errMsg(x) }); }
  };
  const patch = async (id, body) => {
    try { await api.patch(`/admin/users/${id}`, body); load(); } catch (x) { setMsg({ ok: "", err: errMsg(x) }); }
  };
  const train = async () => {
    try { const r = await api.post("/admin/train-model"); setMsg({ ok: r.data.trained ? `Model trained on ${r.data.samples} answers (accuracy ${r.data.sklearn_accuracy})` : r.data.reason, err: "" }); }
    catch (x) { setMsg({ ok: "", err: errMsg(x) }); }
  };

  return (
    <>
      <h2>Administration</h2>
      {stats && (
        <div className="grid">
          {Object.entries(stats).map(([k, v]) => <div className="card stat" key={k}><b>{v}</b><span>{k}</span></div>)}
        </div>
      )}
      {msg.err && <p className="err">{msg.err}</p>}{msg.ok && <p className="ok">{msg.ok}</p>}

      <div className="card">
        <h3>AI model</h3>
        <p className="muted">Retrain the weakness predictor with the latest student answers.</p>
        <button onClick={train}>Retrain model</button>
      </div>

      <div className="card">
        <h3>Users</h3>
        <table>
          <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td><td>{u.email}</td>
                <td><select value={u.role} onChange={(e) => patch(u.id, { role: e.target.value })}><option>student</option><option>teacher</option><option>admin</option></select></td>
                <td>{u.active ? "Active" : "Disabled"}</td>
                <td><button className="ghost" onClick={() => patch(u.id, { active: !u.active })}>{u.active ? "Disable" : "Enable"}</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Create a teacher or admin</h3>
        <form onSubmit={create}>
          <label>Name</label><input value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} required />
          <label>Email</label><input type="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} required />
          <label>Temporary password (8+ characters)</label><input type="password" minLength={8} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} required />
          <label>Role</label>
          <select value={f.role} onChange={(e) => setF({ ...f, role: e.target.value })}><option>teacher</option><option>admin</option><option>student</option></select>
          <p><button>Create user</button></p>
        </form>
      </div>
    </>
  );
}
