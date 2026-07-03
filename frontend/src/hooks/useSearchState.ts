import { useState, useMemo, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import {
  MOCK_PROPERTIES,
  AREA_SCORES_MOCK,
  FilterState,
  SortOption,
  PropertyType,
} from "../data/mockData";

const PAGE_SIZE = 12;

export interface SearchState {
  properties: typeof MOCK_PROPERTIES;
  filteredCount: number;
  page: number;
  totalPages: number;
  pagedProperties: typeof MOCK_PROPERTIES;
  filters: FilterState;
  sortBy: SortOption;
  selectedPropertyId: number | null;
  areaScores: typeof AREA_SCORES_MOCK;
  setFilters: (f: Partial<FilterState>) => void;
  setSortBy: (s: SortOption) => void;
  setPage: (p: number) => void;
  setSelectedPropertyId: (id: number | null) => void;
  clearFilters: () => void;
}

function filtersFromParams(sp: URLSearchParams): FilterState {
  const minPrice = sp.get("minPrice");
  const maxPrice = sp.get("maxPrice");
  const propertyType = sp.get("propertyType");
  return {
    minPrice: minPrice ? Number(minPrice) : null,
    maxPrice: maxPrice ? Number(maxPrice) : null,
    propertyType: (propertyType as PropertyType) || null,
  };
}

function paramsFromFilters(f: FilterState, sort: SortOption, page: number): Record<string, string> {
  const p: Record<string, string> = {};
  if (f.minPrice) p.minPrice = String(f.minPrice);
  if (f.maxPrice) p.maxPrice = String(f.maxPrice);
  if (f.propertyType) p.propertyType = f.propertyType;
  if (sort !== "price_asc") p.sort = sort;
  if (page > 0) p.page = String(page);
  return p;
}

export function useSearchState(): SearchState {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo(() => filtersFromParams(searchParams), [searchParams]);
  const sortBy: SortOption = (searchParams.get("sort") as SortOption) || "price_asc";
  const page = Number(searchParams.get("page") || "0");

  const [selectedPropertyId, setSelectedPropertyId] = useState<number | null>(null);

  const filtered = useMemo(() => {
    let result = [...MOCK_PROPERTIES];

    if (filters.minPrice) {
      result = result.filter(p => p.price_eur >= filters.minPrice!);
    }
    if (filters.maxPrice) {
      result = result.filter(p => p.price_eur <= filters.maxPrice!);
    }
    if (filters.propertyType) {
      result = result.filter(p => p.property_type === filters.propertyType);
    }

    result.sort((a, b) => {
      switch (sortBy) {
        case "price_asc": return a.price_eur - b.price_eur;
        case "price_desc": return b.price_eur - a.price_eur;
        case "recent": return new Date(b.sale_date).getTime() - new Date(a.sale_date).getTime();
        case "score": {
          const sa = AREA_SCORES_MOCK[a.area_id]?.livability ?? 0;
          const sb = AREA_SCORES_MOCK[b.area_id]?.livability ?? 0;
          return sb - sa;
        }
        default: return 0;
      }
    });

    return result;
  }, [filters, sortBy]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const clampedPage = Math.min(page, totalPages - 1);
  const pagedProperties = filtered.slice(clampedPage * PAGE_SIZE, (clampedPage + 1) * PAGE_SIZE);

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
    properties: filtered,
    filteredCount: filtered.length,
    page: clampedPage,
    totalPages,
    pagedProperties,
    filters,
    sortBy,
    selectedPropertyId,
    areaScores: AREA_SCORES_MOCK,
    setFilters,
    setSortBy: setSortByFn,
    setPage: setPageFn,
    setSelectedPropertyId,
    clearFilters,
  };
}
