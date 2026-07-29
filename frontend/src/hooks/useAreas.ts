import { useQuery } from "@tanstack/react-query";
import { getAreas, getAreaDetail, getAreaSummaries } from "../api/areas";

export function useAreas() {
  return useQuery({
    queryKey: ["areas"],
    queryFn: getAreas,
    retry: false,
    staleTime: 60_000,
  });
}

export function useAreaDetail(id: number | null) {
  return useQuery({
    queryKey: ["areas", id],
    queryFn: () => getAreaDetail(id!),
    enabled: id !== null,
  });
}

export function useAreaSummaries() {
  return useQuery({
    queryKey: ["areaSummaries"],
    queryFn: getAreaSummaries,
    staleTime: 300_000,
  });
}
