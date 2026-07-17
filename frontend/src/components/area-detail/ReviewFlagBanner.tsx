import React from "react";
import { AlertTriangle } from "lucide-react";

// CRITICAL (per general-architecture + frontend skills): needs_human_review
// originates in the Agents Layer and must never be dropped or silenced on
// its way to the UI. Any area where needs_human_review === true MUST render
// this banner — unmissable, both here (side panel / area detail) and via the
// pulsing marker on the map (see AreaMarker.tsx).
export function ReviewFlagBanner({ needsReview }: { needsReview: boolean }) {
  if (!needsReview) return null;

  return (
    <div
      className="bg-rose-500/10 border border-rose-500/40 rounded-lg p-4 my-4"
      data-testid="review-flag-banner"
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0">
          <AlertTriangle className="h-5 w-5 text-rose-500" aria-hidden="true" />
        </div>
        <div>
          <h3 className="text-sm font-sans font-bold text-rose-400">
            Qualitative Disagreement Flag
          </h3>
          <div className="mt-1.5 text-sm font-sans text-rose-200/90 leading-relaxed">
            <p>
              The qualitative livability read for this area contradicts the hard data, or the
              model's confidence is low. This area has been flagged for human review. Proceed
              with caution.
            </p>
            <p className="mt-2">
              AI signals conflict with reported data for this area. Qualitative sources disagree
              with hard metrics — verify independently before transacting.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
