import { useQuery } from "@tanstack/react-query";
import { getAreaScore } from "../api/areas";

export function useAreaScore(id: number | null) {
  return useQuery({
    queryKey: ["areaScore", id],
    queryFn: () => getAreaScore(id!),
    enabled: id !== null,
  });
}
