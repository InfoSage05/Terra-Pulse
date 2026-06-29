import { useMutation } from "@tanstack/react-query";
import { predictPrice } from "../api/predict";

export function usePricePrediction() {
  return useMutation({
    mutationFn: predictPrice,
  });
}
