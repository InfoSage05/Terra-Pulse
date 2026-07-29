import React from "react";
import { usePricePrediction } from "../../hooks/usePricePrediction";
import { AreaDetail } from "../../types/api";

export function PricePredictorWidget({ area }: { area: AreaDetail }) {
  const { mutate: predict, data: prediction, isPending, error } = usePricePrediction();

  const handlePredict = () => {
    predict({ area_id: area.id });
  };

  return (
    <div className="bg-slate-900 rounded-lg shadow p-4 mt-4 border border-slate-700" data-testid="price-predictor">
      <h3 className="text-lg font-display font-semibold text-slate-100 mb-2">Price Predictor</h3>
      <p className="text-sm text-slate-400 mb-4">
        Get an AI-powered estimated price for {area.name}.
      </p>

      <button
        onClick={handlePredict}
        disabled={isPending}
        className="w-full bg-violet-500 hover:bg-violet-600 text-white font-medium py-2 px-4 rounded transition-colors disabled:opacity-50"
      >
        {isPending ? "Calculating..." : "Predict Price"}
      </button>

      {error && (
        <div className="mt-3 text-rose-400 text-sm">
          Failed to generate prediction. Please try again.
        </div>
      )}

      {prediction && (
        <div className="mt-4 p-3 bg-violet-500/10 border border-violet-500/30 rounded">
          <div className="text-2xl font-mono font-bold text-violet-300">
            €{prediction.predicted_price_eur.toLocaleString("en-IE", { maximumFractionDigits: 0 })}
          </div>
          <div className="text-sm text-violet-200/80 mt-1">
            Confidence Interval:
            <span className="font-mono font-medium ml-1">
              €{prediction.confidence_interval_low.toLocaleString("en-IE", { maximumFractionDigits: 0 })} -
              €{prediction.confidence_interval_high.toLocaleString("en-IE", { maximumFractionDigits: 0 })}
            </span>
          </div>
          <div className="text-xs text-violet-400/70 mt-2 font-mono" data-testid="model-version">
            Model Version: {prediction.model_version}
          </div>
        </div>
      )}
    </div>
  );
}
