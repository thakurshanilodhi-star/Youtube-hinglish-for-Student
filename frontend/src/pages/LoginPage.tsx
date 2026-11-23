import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Film, Eye, EyeOff } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import api from "@/services/api";

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setToken, setUser } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isRegister) {
        await api.post("/auth/register", null, { params: { email, password, full_name: fullName } });
        const loginRes = await api.post("/auth/login", null, { params: { username: email, password } });
        setToken(loginRes.data.access_token);
      } else {
        const response = await api.post("/auth/login", null, { params: { username: email, password } });
        setToken(response.data.access_token);
      }
      const userRes = await api.get("/auth/me");
      setUser(userRes.data);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Authentication failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 px-4">
      <div className="w-full max-w-md bg-card border border-border rounded-2xl p-8 shadow-lg">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4"><Film className="w-8 h-8 text-primary" /></div>
          <h1 className="text-2xl font-bold">HinglishDub</h1>
          <p className="text-muted-foreground text-sm mt-1">{isRegister ? "Create your account" : "Sign in to your account"}</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div><label className="block text-sm font-medium mb-1.5">Full Name</label><input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" placeholder="John Doe" /></div>
          )}
          <div><label className="block text-sm font-medium mb-1.5">Email</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" placeholder="you@example.com" /></div>
          <div><label className="block text-sm font-medium mb-1.5">Password</label><div className="relative"><input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full px-4 py-2.5 pr-10 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary" placeholder="••••••••" /><button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">{showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button></div></div>
          {error && <p className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">{error}</p>}
          <button type="submit" disabled={loading} className="w-full py-2.5 bg-primary text-primary-foreground rounded-lg font-medium text-sm hover:bg-primary/90 disabled:opacity-50">{loading ? "Please wait..." : isRegister ? "Create Account" : "Sign In"}</button>
        </form>
        <p className="text-center text-sm text-muted-foreground mt-6">{isRegister ? "Already have an account?" : "Don't have an account?"} <button onClick={() => setIsRegister(!isRegister)} className="text-primary font-medium hover:underline">{isRegister ? "Sign in" : "Create one"}</button></p>
      </div>
    </div>
  );
}
