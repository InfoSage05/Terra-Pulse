import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";
import { api } from "../lib/api";

export default function AuthPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleGoogleSuccess(credentialResponse: CredentialResponse) {
    setError(null);
    if (!credentialResponse.credential) {
      setError("Google sign-in failed. Please try again.");
      return;
    }
    try {
      await api.googleAuth(credentialResponse.credential);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed.");
    }
  }

  async function handleEmailContinue(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!showPassword) {
      // First step: just validate email format, then reveal password field
      if (!email.includes("@")) {
        setError("Please enter a valid email.");
        return;
      }
      setShowPassword(true);
      return;
    }

    setLoading(true);
    try {
      if (mode === "signup") {
        await api.register(email, password);
      } else {
        await api.login(email, password);
      }
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-black px-4">
      <div className="w-full max-w-sm border border-white/10 rounded-2xl p-8">
        <h1 className="text-xl font-semibold text-white text-center mb-6">
          {mode === "login" ? "Sign in to TerraPulse" : "Create your account"}
        </h1>

        <div className="mb-4 flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError("Google sign-in failed. Please try again.")}
            theme="filled_black"
            shape="pill"
            width="320"
          />
        </div>

        <div className="flex items-center gap-3 my-4 text-xs text-white/40">
          <div className="h-px flex-1 bg-white/10" />
          OR
          <div className="h-px flex-1 bg-white/10" />
        </div>

        <form onSubmit={handleEmailContinue} className="space-y-3">
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={showPassword}
            required
            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/40 outline-none"
          />

          {showPassword && (
            <input
              type="password"
              placeholder={mode === "signup" ? "Create a password" : "Password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoFocus
              required
              minLength={8}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white placeholder-white/40 outline-none"
            />
          )}

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-white text-black rounded-lg py-2.5 font-medium disabled:opacity-50"
          >
            {loading
              ? "Please wait..."
              : showPassword
              ? mode === "signup"
                ? "Create account"
                : "Sign in"
              : "Continue with email"}
          </button>
        </form>

        <p className="text-center text-sm text-white/50 mt-5">
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            type="button"
            onClick={() => {
              setMode(mode === "login" ? "signup" : "login");
              setError(null);
              setShowPassword(false);
              setPassword("");
            }}
            className="text-blue-400 hover:underline"
          >
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}