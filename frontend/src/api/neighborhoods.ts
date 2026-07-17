import { Neighborhood, FeaturedNeighborhoodsResponse } from "../types/api";
import { fetchApi } from "./client";

export interface NeighborhoodQuery {
  sort_by?: "median_sold_price" | "average_sold_price" | "avg_asking_price" | "locality";
  limit?: number;
}

export async function getNeighborhoods(query: NeighborhoodQuery = {}): Promise<Neighborhood[]> {
  const params = new URLSearchParams();
  if (query.sort_by) params.set("sort_by", query.sort_by);
  if (query.limit) params.set("limit", String(query.limit));
  const qs = params.toString();
  return fetchApi<Neighborhood[]>(`/neighborhoods${qs ? `?${qs}` : ""}`);
}

export async function getFeaturedNeighborhoods(limit: number = 8): Promise<FeaturedNeighborhoodsResponse> {
  return fetchApi<FeaturedNeighborhoodsResponse>(`/neighborhoods/featured?limit=${limit}`);
}
