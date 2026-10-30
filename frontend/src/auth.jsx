import { createContext, useContext, useEffect, useState } from "react";
import api from "./api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem("token"));

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    api.get("/auth/me").then((r) => setUser(r.data.user)).catch(() => localStorage.removeItem("token")).finally(() => setLoading(false));
  }, []);

  const finish = (data) => {
    localStorage.setItem("token", data.token);
    setUser(data.user);
    return data.user;
  };
  const login = async (email, password) => finish((await api.post("/auth/login", { email, password })).data);
  const register = async (form) => finish((await api.post("/auth/register", form)).data);
  const logout = () => { localStorage.removeItem("token"); setUser(null); };

  return <Ctx.Provider value={{ user, setUser, loading, login, register, logout }}>{children}</Ctx.Provider>;
}
