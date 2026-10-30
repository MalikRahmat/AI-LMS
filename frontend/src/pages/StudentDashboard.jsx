import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { errMsg } from "../api";
import { useAuth } from "../auth.jsx";

const level = (w) => (w > 0.55 ? "weak" : w > 0.4 ? "mid" : "strong");

export default function StudentDashboard() {
  const { setUser } = useAuth();
  const [d, setD] = useState(null);
  const [err, setErr] = useState("");

  const load = () => api.get("/student/dashboard").then((r) => setD(r.data)).catch((e) => setErr(errMsg(e)));
  useEffect(() => { load(); }, []);

  const setStyle = async (learning_style) => {
    const r = await api.patch("/student/profile", { learning_style });
    setUser(r.data.user);
    load();
  };

  if (err) return <p className="err">{err}</p>;
  if (!d) return <p className="center">Loading your dashboard…</p>;
  const { stats } = d;

  return (
    <>
      <h2>Hello, {d.user.name}</h2>
      <div className="grid">
        <div className="card stat"><b>{stats.answered}</b><span>questions answered</span></div>
        <div className="card stat"><b>{stats.accuracy == null ? "–" : Math.round(stats.accuracy * 100) + "%"}</b><span>overall accuracy</span></div>
        <div className="card">
          <label htmlFor="style">Learning style</label>
          <select id="style" value={d.user.learning_style} onChange={(e) => setStyle(e.target.value)}>
            <option value="visual">Visual</option><option value="auditory">Auditory</option>
            <option value="reading">Reading</option><option value="kinesthetic">Kinesthetic</option>
          </select>
        </div>
      </div>

      <div className="card">
        <h3>Where to focus</h3>
        <p className="muted">Predicted weakness per topic (higher bar = needs more practice).</p>
        {d.topics.map((t) => (
          <div className="row" key={t.topic_id}>
            <span className="name">{t.topic} <span className="muted">· {t.subject}</span></span>
            <div className={`bar ${level(t.weakness)}`}><i style={{ width: `${Math.round(t.weakness * 100)}%` }} /></div>
            <span className="muted" style={{ width: 44, textAlign: "right" }}>{Math.round(t.weakness * 100)}%</span>
          </div>
        ))}
        <p><Link className="btn" to="/quiz">Take a quiz on my weak topics</Link></p>
      </div>

      <div className="card">
        <h3>Recommended for you</h3>
        {d.recommendations.map((r) => (
          <div key={r.topic} style={{ marginBottom: ".8rem" }}>
            <strong>{r.topic}</strong>
            {r.resources.length === 0 && <p className="muted">No resources for this topic yet.</p>}
            {r.resources.map((x) => (
              <div key={x.id} className="row"><span>{x.title}</span><span className="tag">{x.type}</span></div>
            ))}
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Your 7-day study plan</h3>
        <table><tbody>
          {d.study_plan.map((p) => (
            <tr key={p.day}><th>Day {p.day}</th><td><strong>{p.focus}</strong><br />{p.tasks.join(" • ")}</td></tr>
          ))}
        </tbody></table>
      </div>

      <div className="card">
        <h3>Recent quizzes</h3>
        {d.history.length === 0 ? <p className="muted">No quizzes yet. Take your first one to unlock predictions.</p> :
          d.history.map((h) => (
            <div className="row" key={h.id}>
              <span>{new Date(h.date).toLocaleDateString()}</span>
              <div className="bar strong"><i style={{ width: `${(h.score / h.total) * 100}%` }} /></div>
              <span>{h.score}/{h.total}</span>
            </div>
          ))}
      </div>
    </>
  );
}
