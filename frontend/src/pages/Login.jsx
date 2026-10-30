import { useState } from "react";
import { useAuth } from "../auth.jsx";
import { errMsg } from "../api";

export default function Login() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ name: "", email: "", password: "", learning_style: "reading" });
  const [err, setErr] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      mode === "login" ? await login(f.email, f.password) : await register(f);
    } catch (x) { setErr(errMsg(x)); }
  };

  return (
    <div className="card login">
      <h2>{mode === "login" ? "Sign in to AdaptLearn" : "Create a student account"}</h2>
      <form onSubmit={submit}>
        {mode === "register" && (<><label>Full name</label><input value={f.name} onChange={set("name")} required /></>)}
        <label>Email</label><input type="email" value={f.email} onChange={set("email")} required />
        <label>Password</label><input type="password" minLength={mode === "register" ? 8 : 1} value={f.password} onChange={set("password")} required />
        {mode === "register" && (
          <><label>How do you learn best?</label>
            <select value={f.learning_style} onChange={set("learning_style")}>
              <option value="visual">Watching videos and diagrams</option>
              <option value="auditory">Listening and discussing</option>
              <option value="reading">Reading and notes</option>
              <option value="kinesthetic">Practising with exercises</option>
            </select></>
        )}
        {err && <p className="err">{err}</p>}
        <p><button type="submit">{mode === "login" ? "Sign in" : "Create account"}</button></p>
      </form>
      <button className="ghost" onClick={() => { setMode(mode === "login" ? "register" : "login"); setErr(""); }}>
        {mode === "login" ? "New student? Create an account" : "Have an account? Sign in"}
      </button>
      {mode === "login" && <p className="muted">Demo: student@demo.com, teacher@demo.com, admin@demo.com — password Password123</p>}
    </div>
  );
}
