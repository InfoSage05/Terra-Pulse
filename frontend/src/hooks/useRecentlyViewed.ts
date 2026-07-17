import { useCallback, useEffect, useState } from "react";
import { PropertyListing } from "../types/api";

const STORAGE_KEY = "terrapulse_viewed";
const MAX_ITEMS = 8;
const CHANGE_EVENT = "terrapulse-viewed-changed";

function read(): PropertyListing[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/** Call whenever the user views a property (e.g. clicks a PropertyCard). */
export function recordViewedProperty(property: PropertyListing): void {
  try {
    const existing = read().filter((p) => p.id !== property.id);
    const next = [property, ...existing].slice(0, MAX_ITEMS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    window.dispatchEvent(new CustomEvent(CHANGE_EVENT));
  } catch {
    // localStorage unavailable (private browsing, quota, etc.) — no-op
  }
}

export function useRecentlyViewed() {
  const [items, setItems] = useState<PropertyListing[]>(() => read());

  useEffect(() => {
    const refresh = () => setItems(read());
    window.addEventListener(CHANGE_EVENT, refresh);
    window.addEventListener("storage", refresh);
    return () => {
      window.removeEventListener(CHANGE_EVENT, refresh);
      window.removeEventListener("storage", refresh);
    };
  }, []);

  const clear = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
    setItems([]);
  }, []);

  return { items, clear };
}
