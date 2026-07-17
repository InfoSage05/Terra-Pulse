import { useState, useMemo, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { useProperties } from "./useProperties";
import { PropertyListing } from "../types/api";

const PAGE_SIZE = 50;

export interface FilterState {
  minPrice: number | null;
  maxPrice: number | null;
}

export type SortOption = "price_asc" | "price_desc" | "recent";

export interface SearchState {
  properties: PropertyListing[];
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
  return {
    minPrice: minPrice ? Number(minPrice) : null,
    maxPrice: maxPrice ? Number(maxPrice) : null,
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
      min_price: filters.minPrice ?? undefined,
      max_price: filters.maxPrice ?? undefined,
      sort_by: sortBy === "price_asc" ? "price_asc" as const
        : sortBy === "price_desc" ? "price_desc" as const
        : "recent" as const,
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
    }),
    [filters.minPrice, filters.maxPrice, sortBy, page]
  );

  const { data: properties = [], isLoading } = useProperties(query);

  const totalPages = Math.max(1, Math.ceil(properties.length / PAGE_SIZE) + (properties.length === PAGE_SIZE ? 1 : 0));

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
    filteredCount: properties.length,
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
