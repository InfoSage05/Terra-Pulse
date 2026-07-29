import { useState, useMemo, useCallback, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { useProperties } from "./useProperties";
import { PropertyListing } from "../types/api";

const PAGE_SIZE = 50;

export interface FilterState {
  minPrice: number | null;
  maxPrice: number | null;
  areaId: number | null;
  soldAfter: string | null;
  soldBefore: string | null;
}

export type SortOption = "price_asc" | "price_desc" | "recent";

export interface SearchState {
  properties: PropertyListing[];
  /** Real count matching the current filters, from the backend's
   *  X-Total-Count header - NOT properties.length (which is only the
   *  current page's size). */
  filteredCount: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  filters: FilterState;
  sortBy: SortOption;
  selectedPropertyId: number | null;
  setFilters: (f: Partial<FilterState>) => void;
  setSortBy: (s: SortOption) => void;
  setPage: (p: number) => void;
  setSelectedPropertyId: (id: number | null) => void;
  clearFilters: () => void;
}

function filtersFromParams(sp: URLSearchParams): FilterState {
  const minPrice = sp.get("minPrice");
  const maxPrice = sp.get("maxPrice");
  const areaId = sp.get("areaId");
  return {
    minPrice: minPrice ? Number(minPrice) : null,
    maxPrice: maxPrice ? Number(maxPrice) : null,
    areaId: areaId ? Number(areaId) : null,
    soldAfter: sp.get("soldAfter"),
    soldBefore: sp.get("soldBefore"),
  };
}

function paramsFromFilters(
  f: FilterState,
  sort: SortOption,
  page: number
): Record<string, string> {
  const p: Record<string, string> = {};
  if (f.minPrice) p.minPrice = String(f.minPrice);
  if (f.maxPrice) p.maxPrice = String(f.maxPrice);
  if (f.areaId) p.areaId = String(f.areaId);
  if (f.soldAfter) p.soldAfter = f.soldAfter;
  if (f.soldBefore) p.soldBefore = f.soldBefore;
  if (sort !== "price_asc") p.sort = sort;
  if (page > 0) p.page = String(page);
  return p;
}

export function useSearchState(): SearchState {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | null>(null);

  const filters = useMemo(() => filtersFromParams(searchParams), [searchParams]);
  const sortBy: SortOption =
    (searchParams.get("sort") as SortOption) || "price_asc";
  const page = Number(searchParams.get("page") || "0");

  const query = useMemo(
    () => ({
      area_id: filters.areaId ?? undefined,
      min_price: filters.minPrice ?? undefined,
      max_price: filters.maxPrice ?? undefined,
      sold_after: filters.soldAfter ?? undefined,
      sold_before: filters.soldBefore ?? undefined,
      sort_by: sortBy === "price_asc" ? "price_asc" as const
        : sortBy === "price_desc" ? "price_desc" as const
        : "recent" as const,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }),
    [filters.minPrice, filters.maxPrice, filters.areaId, filters.soldAfter, filters.soldBefore, sortBy, page]
  );

  const { data, isLoading } = useProperties(query);
  const filteredCount = data?.total ?? 0;

  // "Load more" is meant to accumulate results (there can be thousands of
  // real matches - see filteredCount), not replace the visible list with
  // just the next page's 50. Accumulate across pages here, resetting
  // whenever the filters/sort (anything but page) change.
  const [accumulated, setAccumulated] = useState<PropertyListing[]>([]);
  const filterKey = JSON.stringify({
    areaId: filters.areaId,
    minPrice: filters.minPrice,
    maxPrice: filters.maxPrice,
    soldAfter: filters.soldAfter,
    soldBefore: filters.soldBefore,
    sortBy,
  });
  const prevFilterKeyRef = useRef(filterKey);

  useEffect(() => {
    if (prevFilterKeyRef.current !== filterKey) {
      prevFilterKeyRef.current = filterKey;
      setAccumulated([]);
    }
  }, [filterKey]);

  useEffect(() => {
    if (!data) return;
    setAccumulated((prev) => (page === 0 ? data.items : [...prev, ...data.items]));
  }, [data, page]);

  const properties = accumulated;
  const totalPages = Math.max(1, Math.ceil(filteredCount / PAGE_SIZE));

  const updateParams = useCallback(
    (f: Partial<FilterState>, sort?: SortOption, p?: number) => {
      const newFilters = { ...filters, ...f };
      const newSort = sort ?? sortBy;
      const newPage = p ?? 0;
      setSearchParams(paramsFromFilters(newFilters, newSort, newPage));
    },
    [filters, sortBy, setSearchParams]
  );

  const setFilters = useCallback(
    (f: Partial<FilterState>) => updateParams(f),
    [updateParams]
  );

  const setSortByFn = useCallback(
    (s: SortOption) => updateParams({}, s),
    [updateParams]
  );

  const setPageFn = useCallback(
    (p: number) => updateParams({}, undefined, p),
    [updateParams]
  );

  const clearFilters = useCallback(() => {
    setSearchParams({});
  }, [setSearchParams]);

  return {
    properties,
    filteredCount,
    page,
    totalPages,
    isLoading,
    filters,
    sortBy,
    selectedPropertyId,
    setFilters,
    setSortBy: setSortByFn,
    setPage: setPageFn,
    setSelectedPropertyId,
    clearFilters,
  };
}
