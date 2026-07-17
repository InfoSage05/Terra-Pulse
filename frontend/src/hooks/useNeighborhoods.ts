import { useQuery } from "@tanstack/react-query";
import { getFeaturedNeighborhoods, getNeighborhoods, NeighborhoodQuery } from "../api/neighborhoods";

export function useNeighborhoods(query: NeighborhoodQuery = {}) {
  return useQuery({
    queryKey: ["neighborhoods", query],
    queryFn: () => getNeighborhoods(query),
    staleTime: 300_000,
  });
}

export function useFeaturedNeighborhoods(limit: number = 8) {
  return useQuery({
    queryKey: ["featuredNeighborhoods", limit],
    queryFn: () => getFeaturedNeighborhoods(limit),
    staleTime: 300_000,
  });
}
