import { useEffect, useRef, useState } from "react";
import api, { errMsg } from "../api";

export default function Chat() {
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const end = useRef(null);

  useEffect(() => { api.get("/chat").then((r) => setMsgs(r.data.messages)); }, []);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  const send = async (e) => {
    e.preventDefault();
    const q = text.trim();
    if (!q) return;
    setText(""); setErr(""); setBusy(true);
    setMsgs((m) => [...m, { role: "user", content: q }]);
    try {
      const r = await api.post("/chat", { message: q });
      setMsgs((m) => [...m, { role: "assistant", content: r.data.reply }]);
    } catch (x) { setErr(errMsg(x)); }
    setBusy(false);
  };

  return (
    <>
      <h2>AI tutor</h2>
      <div className="card">
        <div className="chat">
          {msgs.length === 0 && <p className="muted">Ask about any topic, for example: “Explain list vs tuple”.</p>}
          {msgs.map((m, i) => <div key={i} className={`msg ${m.role}`}>{m.content}</div>)}
          {busy && <div className="msg assistant">Thinking…</div>}
          <div ref={end} />
        </div>
        {err && <p className="err">{err}</p>}
        <form className="inline" onSubmit={send} style={{ marginTop: ".8rem" }}>
          <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Ask your tutor a question" maxLength={2000} />
          <button disabled={busy}>Send</button>
        </form>
      </div>
    </>
  );
}
