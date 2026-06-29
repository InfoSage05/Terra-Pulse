import { PricePredictionInput, PricePredictionOutput } from "../types/api";
import { fetchApi } from "./client";

export async function predictPrice(input: PricePredictionInput): Promise<PricePredictionOutput> {
  return fetchApi<PricePredictionOutput>("/predict/price", {
    method: "POST",
    body: JSON.stringify(input),
  });
}
