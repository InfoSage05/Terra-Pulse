import { useQuery } from "@tanstack/react-query";
import { getAreas, getAreaDetail } from "../api/areas";

export function useAreas() {
  return useQuery({
    queryKey: ["areas"],
    queryFn: getAreas,
  });
}

export function useAreaDetail(id: number | null) {
  return useQuery({
    queryKey: ["areas", id],
    queryFn: () => getAreaDetail(id!),
    enabled: id !== null,
  });
}
