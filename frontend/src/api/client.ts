const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/v1";
const API_KEY = import.meta.env.VITE_API_KEY || "dev_secret_key";

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...options?.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Not found");
    }
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
