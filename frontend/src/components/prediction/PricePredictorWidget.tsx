import React from "react";
import { usePricePrediction } from "../../hooks/usePricePrediction";
import { AreaDetail } from "../../types/api";

export function PricePredictorWidget({ area }: { area: AreaDetail }) {
  const { mutate: predict, data: prediction, isPending, error } = usePricePrediction();

  const handlePredict = () => {
    predict({ area_id: area.id });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 mt-4 border border-gray-200" data-testid="price-predictor">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">Price Predictor</h3>
      <p className="text-sm text-gray-600 mb-4">
        Get an AI-powered estimated price for {area.name}.
      </p>
      
      <button
        onClick={handlePredict}
        disabled={isPending}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded transition-colors disabled:opacity-50"
      >
        {isPending ? "Calculating..." : "Predict Price"}
      </button>

      {error && (
        <div className="mt-3 text-red-600 text-sm">
          Failed to generate prediction. Please try again.
        </div>
      )}

      {prediction && (
        <div className="mt-4 p-3 bg-indigo-50 border border-indigo-100 rounded">
          <div className="text-2xl font-bold text-indigo-900">
            €{prediction.predicted_price_eur.toLocaleString("en-IE", { maximumFractionDigits: 0 })}
          </div>
          <div className="text-sm text-indigo-700 mt-1">
            Confidence Interval: 
            <span className="font-medium ml-1">
              €{prediction.confidence_interval_low.toLocaleString("en-IE", { maximumFractionDigits: 0 })} - 
              €{prediction.confidence_interval_high.toLocaleString("en-IE", { maximumFractionDigits: 0 })}
            </span>
          </div>
          <div className="text-xs text-indigo-400 mt-2 font-mono" data-testid="model-version">
            Model Version: {prediction.model_version}
          </div>
        </div>
      )}
    </div>
  );
}
