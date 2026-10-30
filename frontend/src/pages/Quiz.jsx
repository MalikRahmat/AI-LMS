import { useEffect, useState } from "react";
import api, { errMsg } from "../api";

export default function Quiz() {
  const [topics, setTopics] = useState([]);
  const [topicId, setTopicId] = useState("");
  const [questions, setQuestions] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.get("/content/topics").then((r) => setTopics(r.data.topics)); }, []);

  const start = async () => {
    setErr(""); setResult(null); setAnswers({}); setBusy(true);
    try {
      const r = await api.post("/quiz/generate", { num: 10, topic_id: topicId ? Number(topicId) : undefined });
      setQuestions(r.data.questions);
    } catch (e) { setErr(errMsg(e)); }
    setBusy(false);
  };

  const submit = async () => {
    setBusy(true);
    try {
      const payload = questions.map((q) => ({ question_id: q.id, selected: answers[q.id] ?? null }));
      setResult((await api.post("/quiz/submit", { answers: payload })).data);
      setQuestions(null);
    } catch (e) { setErr(errMsg(e)); }
    setBusy(false);
  };

  const aiMore = async () => {
    if (!topicId) return setErr("Pick a topic first to generate AI questions for it.");
    setErr(""); setBusy(true);
    try { const r = await api.post("/quiz/ai-generate", { topic_id: Number(topicId), num: 5 }); setErr(""); alert(`${r.data.created} new AI questions added to the bank.`); }
    catch (e) { setErr(errMsg(e)); }
    setBusy(false);
  };

  return (
    <>
      <h2>Adaptive quiz</h2>
      {!questions && (
        <div className="card">
          <p className="muted">Questions are picked from your weakest topics and matched to your current level.</p>
          <label htmlFor="t">Topic</label>
          <select id="t" value={topicId} onChange={(e) => setTopicId(e.target.value)}>
            <option value="">Automatic (my weak topics)</option>
            {topics.map((t) => <option key={t.id} value={t.id}>{t.subject} – {t.name}</option>)}
          </select>
          <p className="inline"><button disabled={busy} onClick={start}>Start quiz</button>
            <button className="ghost" disabled={busy} onClick={aiMore}>Add AI-written questions</button></p>
          {err && <p className="err">{err}</p>}
        </div>
      )}

      {questions && (
        <>
          {questions.map((q, i) => (
            <div className="card" key={q.id}>
              <span className="tag">{q.topic}</span>
              <h3 style={{ marginTop: ".5rem" }}>{i + 1}. {q.text}</h3>
              {q.options.map((o, k) => (
                <button key={k} className={`opt ${answers[q.id] === k ? "sel" : ""}`} onClick={() => setAnswers({ ...answers, [q.id]: k })}>{o}</button>
              ))}
            </div>
          ))}
          {err && <p className="err">{err}</p>}
          <button disabled={busy} onClick={submit}>Submit answers ({Object.keys(answers).length}/{questions.length})</button>
        </>
      )}

      {result && (
        <>
          <div className="card stat"><b>{result.score}/{result.total}</b><span>Your weakest topics now: {result.weakest.map((w) => w.topic).join(", ")}</span></div>
          {result.results.map((r) => (
            <div className="card" key={r.question_id}>
              <span className="tag">{r.topic}</span>
              <h3 style={{ marginTop: ".5rem" }}>{r.text}</h3>
              {r.options.map((o, k) => (
                <div key={k} className={`opt ${k === r.correct_index ? "right" : k === r.selected ? "wrong" : ""}`} style={{ padding: ".55rem 1rem", borderRadius: 8 }}>{o}</div>
              ))}
              {r.explanation && <p className="muted">{r.explanation}</p>}
            </div>
          ))}
          <button onClick={start}>Take another quiz</button>
        </>
      )}
    </>
  );
}
