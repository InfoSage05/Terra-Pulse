import { useEffect, useRef, useState } from "react";
import { getAreaScore } from "../api/areas";
import { AreaScoreOutput } from "../types/api";

/**
 * Fetches GET /v1/areas/{id}/score for a set of area ids in parallel and
 * returns an id -> AreaScoreOutput cache. Used wherever we need the REAL
 * needs_human_review flag / score pills for several areas at once (area
 * browser grid, map choropleth) without a dedicated bulk-scores endpoint.
 */
export function useAreaScoresMap(areaIds: number[] | undefined): Record<number, AreaScoreOutput> {
  const [cache, setCache] = useState<Record<number, AreaScoreOutput>>({});
  const cacheRef = useRef(cache);

  useEffect(() => {
    cacheRef.current = cache;
  }, [cache]);

  const key = areaIds?.join(",") ?? "";

  useEffect(() => {
    if (!areaIds || areaIds.length === 0) return;
    const toFetch = areaIds.filter((id) => !cacheRef.current[id]);
    if (toFetch.length === 0) return;

    let cancelled = false;
    (async () => {
      const next = { ...cacheRef.current };
      await Promise.all(
        toFetch.map(async (id) => {
          try {
            next[id] = await getAreaScore(id);
          } catch {
            // score unavailable — leave unset, callers treat as "loading/unknown"
          }
        })
      );
      if (!cancelled) setCache(next);
    })();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return cache;
}
