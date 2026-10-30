import { useState } from "react";
import api, { errMsg } from "../api";

function List({ courses }) {
  return courses.map((c) => (
    <div className="row" key={c.id}>
      <span><strong>{c.title}</strong><br /><span className="muted">{c.summary.replace(/<[^>]+>/g, "").slice(0, 140)}</span></span>
      <a className="btn" href={c.url} target="_blank" rel="noopener noreferrer">Open</a>
    </div>
  ));
}

export default function Integrations() {
  const [q, setQ] = useState("");
  const [coursera, setCoursera] = useState([]);
  const [moodle, setMoodle] = useState([]);
  const [err, setErr] = useState("");

  const search = async (e) => {
    e.preventDefault(); setErr("");
    try { setCoursera((await api.get("/integrations/coursera/search", { params: { q } })).data.courses); } catch (x) { setErr(errMsg(x)); }
  };
  const loadMoodle = async () => {
    setErr("");
    try { setMoodle((await api.get("/integrations/moodle/courses")).data.courses); } catch (x) { setErr(errMsg(x)); }
  };

  return (
    <>
      <h2>Online courses</h2>
      {err && <p className="err">{err}</p>}
      <div className="card">
        <h3>Coursera</h3>
        <form className="inline" onSubmit={search}><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search courses, e.g. machine learning" required /><button>Search</button></form>
        <List courses={coursera} />
      </div>
      <div className="card">
        <h3>Moodle</h3>
        <button onClick={loadMoodle}>Load my Moodle courses</button>
        <List courses={moodle} />
      </div>
    </>
  );
}
