import { useEffect, useState } from "react";
import api, { errMsg } from "../api";
import { useAuth } from "../auth.jsx";

export default function Resources() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [topics, setTopics] = useState([]);
  const [filter, setFilter] = useState("");
  const [err, setErr] = useState("");
  const canEdit = user.role !== "student";

  const load = () => api.get("/resources", { params: filter ? { topic_id: filter } : {} }).then((r) => setItems(r.data.resources));
  useEffect(() => { api.get("/content/topics").then((r) => setTopics(r.data.topics)); }, []);
  useEffect(() => { load(); }, [filter]);

  const open = async (r) => {
    if (!r.has_file) return window.open(r.url, "_blank", "noopener");
    try {
      const res = await api.get(`/resources/${r.id}/download`, { responseType: "blob" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(res.data);
      a.download = r.title;
      a.click();
    } catch (e) { setErr(errMsg(e)); }
  };

  const remove = async (id) => { await api.delete(`/resources/${id}`); load(); };

  return (
    <>
      <h2>Learning resources</h2>
      <div className="card">
        <label htmlFor="f">Filter by topic</label>
        <select id="f" value={filter} onChange={(e) => setFilter(e.target.value)}>
          <option value="">All topics</option>
          {topics.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
        </select>
        {err && <p className="err">{err}</p>}
        <table><tbody>
          {items.map((r) => (
            <tr key={r.id}>
              <td><strong>{r.title}</strong><br /><span className="muted">{r.topic || "General"}</span></td>
              <td><span className="tag">{r.type}</span></td>
              <td style={{ textAlign: "right" }}>
                <button className="ghost" onClick={() => open(r)}>{r.has_file ? "Download" : "Open"}</button>{" "}
                {canEdit && <button className="ghost" onClick={() => remove(r.id)}>Delete</button>}
              </td>
            </tr>
          ))}
          {items.length === 0 && <tr><td className="muted">No resources yet.</td></tr>}
        </tbody></table>
      </div>
      {canEdit && <Upload topics={topics} onDone={load} />}
    </>
  );
}

function Upload({ topics, onDone }) {
  const [msg, setMsg] = useState({ ok: "", err: "" });
  const submit = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    try {
      await api.post("/resources", form);
      setMsg({ ok: "Resource added", err: "" });
      e.target.reset();
      onDone();
    } catch (x) { setMsg({ ok: "", err: errMsg(x) }); }
  };
  return (
    <div className="card">
      <h3>Add a resource</h3>
      <form onSubmit={submit}>
        <label>Title</label><input name="title" required />
        <label>Topic</label>
        <select name="topic_id"><option value="">General</option>{topics.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}</select>
        <label>Type</label>
        <select name="type"><option>article</option><option>video</option><option>audio</option><option>pdf</option><option>exercise</option></select>
        <label>Link (or upload a file below)</label><input name="url" placeholder="https://" />
        <label>File (stored securely)</label><input type="file" name="file" />
        {msg.err && <p className="err">{msg.err}</p>}{msg.ok && <p className="ok">{msg.ok}</p>}
        <p><button>Save resource</button></p>
      </form>
    </div>
  );
}
