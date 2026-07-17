import { PropertyListing } from "../types/api";
import { fetchApi } from "./client";

export interface PropertyQuery {
  area_id?: number;
  min_price?: number;
  max_price?: number;
  sort_by?: "price_asc" | "price_desc" | "recent";
  limit?: number;
  offset?: number;
}

export async function getProperties(query: PropertyQuery): Promise<PropertyListing[]> {
  const params = new URLSearchParams();
  if (query.area_id) params.set("area_id", String(query.area_id));
  if (query.min_price) params.set("min_price", String(query.min_price));
  if (query.max_price) params.set("max_price", String(query.max_price));
  if (query.sort_by) params.set("sort_by", query.sort_by);
  if (query.limit) params.set("limit", String(query.limit));
  if (query.offset) params.set("offset", String(query.offset));

  const qs = params.toString();
  return fetchApi<PropertyListing[]>(`/properties${qs ? `?${qs}` : ""}`);
}
