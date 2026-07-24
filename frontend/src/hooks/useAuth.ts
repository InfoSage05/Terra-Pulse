// frontend/src/hooks/useAuth.ts
import { useEffect, useState } from "react";
import { api } from "../lib/api";

export interface AuthUser {
  id: number;
  email: string;
  name?: string;
  picture?: string;
  auth_provider: string;
}

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return { user, loading };
}