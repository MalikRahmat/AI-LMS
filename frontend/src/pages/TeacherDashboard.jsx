import { useEffect, useState } from "react";
import api, { errMsg } from "../api";

const pct = (x) => (x == null ? "–" : Math.round(x * 100) + "%");

export default function TeacherDashboard() {
  const [d, setD] = useState(null);
  const [detail, setDetail] = useState(null);
  const [topics, setTopics] = useState([]);
  const [err, setErr] = useState("");

  const load = () => api.get("/teacher/overview").then((r) => setD(r.data)).catch((e) => setErr(errMsg(e)));
  useEffect(() => { load(); api.get("/content/topics").then((r) => setTopics(r.data.topics)); }, []);

  const view = async (id) => setDetail((await api.get(`/teacher/student/${id}`)).data);

  if (err) return <p className="err">{err}</p>;
  if (!d) return <p className="center">Loading…</p>;

  return (
    <>
      <h2>Class overview</h2>
      <div className="grid">
        <div className="card stat"><b>{d.students.length}</b><span>active students</span></div>
        <div className="card stat"><b>{pct(d.class_accuracy)}</b><span>class average accuracy</span></div>
      </div>

      <div className="card">
        <h3>Topics where the class struggles</h3>
        {d.topics.map((t) => (
          <div className="row" key={t.topic}>
            <span className="name">{t.topic}</span>
            <div className={`bar ${t.accuracy < 0.5 ? "weak" : t.accuracy < 0.7 ? "mid" : "strong"}`}><i style={{ width: pct(t.accuracy) }} /></div>
            <span className="muted" style={{ width: 44, textAlign: "right" }}>{pct(t.accuracy)}</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>Students</h3>
        <table>
          <thead><tr><th>Name</th><th>Answered</th><th>Accuracy</th><th>Weakest topic</th><th>Last active</th><th></th></tr></thead>
          <tbody>
            {d.students.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td><td>{s.answered}</td><td>{pct(s.accuracy)}</td><td>{s.weakest_topic || "–"}</td>
                <td>{s.last_active ? new Date(s.last_active).toLocaleDateString() : "–"}</td>
                <td><button className="ghost" onClick={() => view(s.id)}>Details</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {detail && (
        <div className="card">
          <h3>{detail.user.name} · {detail.user.learning_style} learner</h3>
          {detail.topics.map((t) => (
            <div className="row" key={t.topic_id}>
              <span className="name">{t.topic}</span>
              <div className="bar weak"><i style={{ width: pct(t.weakness) }} /></div>
              <span className="muted" style={{ width: 44, textAlign: "right" }}>{pct(t.weakness)}</span>
            </div>
          ))}
          <p className="muted">Quiz scores: {detail.history.map((h) => `${h.score}/${h.total}`).join(", ") || "none yet"}</p>
          <button className="ghost" onClick={() => setDetail(null)}>Close</button>
        </div>
      )}

      <AddQuestion topics={topics} />
    </>
  );
}

function AddQuestion({ topics }) {
  const empty = { topic_id: "", text: "", options: ["", "", "", ""], answer_index: 0, difficulty: 2, explanation: "" };
  const [f, setF] = useState(empty);
  const [msg, setMsg] = useState({ ok: "", err: "" });
  const setOpt = (i, v) => setF({ ...f, options: f.options.map((o, k) => (k === i ? v : o)) });

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/content/questions", { ...f, topic_id: Number(f.topic_id), answer_index: Number(f.answer_index), difficulty: Number(f.difficulty) });
      setMsg({ ok: "Question added", err: "" }); setF(empty);
    } catch (x) { setMsg({ ok: "", err: errMsg(x) }); }
  };

  return (
    <div className="card">
      <h3>Add a quiz question</h3>
      <form onSubmit={submit}>
        <label>Topic</label>
        <select value={f.topic_id} onChange={(e) => setF({ ...f, topic_id: e.target.value })} required>
          <option value="">Choose a topic</option>{topics.map((t) => <option key={t.id} value={t.id}>{t.subject} – {t.name}</option>)}
        </select>
        <label>Question</label><textarea value={f.text} onChange={(e) => setF({ ...f, text: e.target.value })} required />
        {f.options.map((o, i) => (<div key={i}><label>Option {i + 1}</label><input value={o} onChange={(e) => setOpt(i, e.target.value)} required /></div>))}
        <label>Correct option</label>
        <select value={f.answer_index} onChange={(e) => setF({ ...f, answer_index: e.target.value })}>{[0, 1, 2, 3].map((i) => <option key={i} value={i}>Option {i + 1}</option>)}</select>
        <label>Difficulty</label>
        <select value={f.difficulty} onChange={(e) => setF({ ...f, difficulty: e.target.value })}><option value={1}>Easy</option><option value={2}>Medium</option><option value={3}>Hard</option></select>
        <label>Explanation shown after answering</label><input value={f.explanation} onChange={(e) => setF({ ...f, explanation: e.target.value })} />
        {msg.err && <p className="err">{msg.err}</p>}{msg.ok && <p className="ok">{msg.ok}</p>}
        <p><button>Save question</button></p>
      </form>
    </div>
  );
}
