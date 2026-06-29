import { AreaDetail, AreaScoreOutput } from "../types/api";
import { fetchApi } from "./client";

export async function getAreas(): Promise<AreaDetail[]> {
  return fetchApi<AreaDetail[]>("/areas");
}

export async function getAreaDetail(id: number): Promise<AreaDetail> {
  return fetchApi<AreaDetail>(`/areas/${id}`);
}

export async function getAreaScore(id: number): Promise<AreaScoreOutput> {
  return fetchApi<AreaScoreOutput>(`/areas/${id}/score`);
}
