import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { PricePredictorWidget } from "../components/prediction/PricePredictorWidget";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import * as predictApi from "../api/predict";

vi.mock("../api/predict");

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe("PricePredictorWidget", () => {
  it("renders prediction with confidence interval and model version", async () => {
    const mockArea = { id: 1, name: "Dublin 1", area_type: "city", county: "Dublin" };
    
    vi.mocked(predictApi.predictPrice).mockResolvedValueOnce({
      area_id: 1,
      predicted_price_eur: 450000,
      confidence_interval_low: 420000,
      confidence_interval_high: 480000,
      model_version: "lightgbm_v2"
    });

    render(
      <QueryClientProvider client={queryClient}>
        <PricePredictorWidget area={mockArea as any} />
      </QueryClientProvider>
    );
    
    fireEvent.click(screen.getByText("Predict Price"));
    
    await waitFor(() => {
      expect(screen.getByText("€450,000")).toBeInTheDocument();
    });
    
    expect(screen.getByText(/€420,000 - €480,000/)).toBeInTheDocument();
    expect(screen.getByTestId("model-version")).toHaveTextContent("lightgbm_v2");
  });
});
