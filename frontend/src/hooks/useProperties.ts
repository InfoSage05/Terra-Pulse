import { useQuery } from "@tanstack/react-query";
import { getProperties, PropertyQuery } from "../api/properties";

export function useProperties(query: PropertyQuery) {
  return useQuery({
    queryKey: ["properties", query],
    queryFn: () => getProperties(query),
    staleTime: 300_000,
  });
}
