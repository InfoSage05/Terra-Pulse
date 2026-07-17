export type ModelType = 
  | "price_prediction"
  | "affordability_score"
  | "safety_score"
  | "livability_score";

export interface ModelMetadata {
  model_type: ModelType;
  version: string;
  trained_at: string;
  training_row_count: number;
  feature_names: string[];
  metric_name: string;
  metric_value: number;
  is_active: boolean;
}

export interface PricePredictionInput {
  area_id: number;
}

export interface PricePredictionOutput {
  area_id: number;
  predicted_price_eur: number;
  confidence_interval_low: number;
  confidence_interval_high: number;
  model_version: string;
}

export interface AreaScoreOutput {
  area_id: number;
  affordability_score: number | null;
  safety_score: number | null;
  livability_score: number | null;
  livability_confidence: number | null;
  needs_human_review: boolean;
  agent_summary: string | null;
  model_versions_used: Record<string, string>;
  last_updated: string;
}

export interface AreaMetrics {
  avg_price: number;
  sales_count: number;
  amenity_count: number;
  total_crime: number;
  population: number;
  deprivation_index: number;
}

export interface AreaDetail {
  id: number;
  name: string;
  area_type: string;
  county: string;
  geometry?: any;
  metrics?: AreaMetrics;
}

export interface AreaSummary {
  id: number;
  name: string;
  area_type: string;
  county: string;
  avg_price: number;
  property_count: number;
}

export interface PropertyListing {
  id: number;
  area_id: number;
  area_name: string | null;
  address_raw: string;
  price_eur: number;
  sale_date: string;
  property_type: string | null;
  lat: number | null;
  lon: number | null;
}

export interface Neighborhood {
  locality: string;
  eircode_district: string | null;
  median_sold_price: number | null;
  average_sold_price: number | null;
  avg_asking_price: number | null;
  data_source: string | null;
}
