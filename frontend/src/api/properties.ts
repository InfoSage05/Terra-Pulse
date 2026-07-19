import { PropertyListing } from "../types/api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/v1";
const API_KEY = import.meta.env.VITE_API_KEY || "dev_secret_key";

export interface PropertyQuery {
  area_id?: number;
  min_price?: number;
  max_price?: number;
  sold_after?: string;
  sold_before?: string;
  sort_by?: "price_asc" | "price_desc" | "recent";
  limit?: number;
  offset?: number;
}

export interface PropertiesResult {
  items: PropertyListing[];
  total: number;
}

export async function getProperties(query: PropertyQuery): Promise<PropertiesResult> {
  const params = new URLSearchParams();
  if (query.area_id) params.set("area_id", String(query.area_id));
  if (query.min_price) params.set("min_price", String(query.min_price));
  if (query.max_price) params.set("max_price", String(query.max_price));
  if (query.sold_after) params.set("sold_after", query.sold_after);
  if (query.sold_before) params.set("sold_before", query.sold_before);
  if (query.sort_by) params.set("sort_by", query.sort_by);
  if (query.limit) params.set("limit", String(query.limit));
  if (query.offset) params.set("offset", String(query.offset));

  const qs = params.toString();
  const response = await fetch(`${BASE_URL}/properties/${qs ? `?${qs}` : ""}`, {
    headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  const items: PropertyListing[] = await response.json();
  // X-Total-Count is the real total matching the current filters (see
  // backend/app/api/v1/properties.py) - items.length is only this page's
  // size, never the true total, so callers must use this for display counts.
  const totalHeader = response.headers.get("X-Total-Count");
  const total = totalHeader ? Number(totalHeader) : items.length;
  return { items, total };
}
