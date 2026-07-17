import { useQuery } from "@tanstack/react-query";
import { getNeighborhoods, NeighborhoodQuery } from "../api/neighborhoods";

export function useNeighborhoods(query: NeighborhoodQuery = {}) {
  return useQuery({
    queryKey: ["neighborhoods", query],
    queryFn: () => getNeighborhoods(query),
    staleTime: 300_000,
  });
}
