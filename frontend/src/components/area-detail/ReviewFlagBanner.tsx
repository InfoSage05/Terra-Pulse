import React from "react";
import { AlertTriangle } from "lucide-react";

export function ReviewFlagBanner({ needsReview }: { needsReview: boolean }) {
  if (!needsReview) return null;

  return (
    <div 
      className="bg-amber-50 border-l-4 border-amber-500 p-4 my-4 shadow-sm"
      data-testid="review-flag-banner"
    >
      <div className="flex">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-amber-500" aria-hidden="true" />
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-bold text-amber-800">
            Qualitative Disagreement Flag
          </h3>
          <div className="mt-2 text-sm text-amber-700">
            <p>
              The qualitative livability read for this area contradicts the hard data, or the model's confidence is low. This area has been flagged for human review. Proceed with caution.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
