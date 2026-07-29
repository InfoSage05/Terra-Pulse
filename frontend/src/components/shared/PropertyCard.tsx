import React from "react";
import { AlertTriangle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { PropertyListing } from "../../types/api";
import { propertyPhotoUrl } from "../../lib/images";
import { recordViewedProperty } from "../../hooks/useRecentlyViewed";
import { isRecentSale } from "../../lib/recency";

interface PropertyCardProps {
  property: PropertyListing;
  isNew?: boolean;
  /** Sourced from the REAL `needs_human_review` flag on the property's area score
   *  (`GET /v1/areas/{id}/score`) — never a placeholder. Omit when unknown. */
  needsReview?: boolean;
  /** Compact variant used by RecentlyViewed — no score pills, thumbnail + price + area. */
  variant?: "full" | "compact";
  onClick?: () => void;
}

export function PropertyCard({ property, isNew, needsReview, variant = "full", onClick }: PropertyCardProps) {
  const navigate = useNavigate();
  const recent = isRecentSale(property.sale_date);
  const handleClick = () => {
    recordViewedProperty(property);
    if (onClick) onClick();
    else navigate(`/search?location=${encodeURIComponent(property.area_name || "")}`);
  };

  if (variant === "compact") {
    return (
      <button
        onClick={handleClick}
        className="flex items-center gap-3 bg-slate-900 border border-slate-700 rounded-xl p-2 text-left hover:border-violet-500 transition-colors w-full"
      >
        <img
          src={propertyPhotoUrl(property.id, 200)}
          alt=""
          className="w-14 h-14 rounded-lg object-cover flex-shrink-0"
          loading="lazy"
        />
        <div className="min-w-0">
          <p className="font-mono font-bold text-sm text-slate-100 truncate">
            €{property.price_eur.toLocaleString("en-IE")}
          </p>
          <p className="text-xs text-slate-400 truncate">
            {property.area_name || `Area #${property.area_id}`}
          </p>
        </div>
      </button>
    );
  }

  return (
    <button
      onClick={handleClick}
      className="group relative flex flex-col text-left bg-slate-900 border border-slate-700 rounded-xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-violet-500/10 hover:border-violet-500"
    >
      <div className="relative w-full aspect-video overflow-hidden rounded-t-xl">
        <img
          src={propertyPhotoUrl(property.id)}
          alt={property.address_raw}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />
        {isNew && (
          <span className="absolute top-0 left-0 bg-violet-500 text-white text-xs font-mono font-semibold px-2 py-0.5 rounded-br-lg">
            NEW
          </span>
        )}
        {needsReview && (
          <span
            className="absolute top-0 right-0 flex items-center gap-1 bg-rose-500/90 text-white text-xs font-mono font-semibold px-2 py-0.5 rounded-bl-lg"
            aria-label="Area flagged for human review"
          >
            <AlertTriangle className="w-3 h-3" aria-hidden="true" />
            Review
          </span>
        )}
      </div>

      <div className="p-4">
        <p className="font-mono font-bold text-lg text-slate-50">
          €{property.price_eur.toLocaleString("en-IE")}
        </p>
        <p className="text-sm text-slate-300 mt-1 truncate">{property.address_raw}</p>
        <p className="text-xs text-slate-500 mt-1 flex items-center gap-1.5">
          <span>
            {property.area_name || `Area #${property.area_id}`} · Sold{" "}
            {property.sale_date
              ? new Date(property.sale_date).toLocaleDateString("en-IE", { month: "short", year: "numeric" })
              : "recently"}
          </span>
          {/* Every row here is already a completed PPR sale - there's no live
              "for sale" feed to color red/green against, so this reflects
              recency (a real signal) instead of a fabricated status. */}
          <span
            className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${recent ? "bg-emerald-400" : "bg-rose-400/70"}`}
            title={recent ? "Sold within the last 90 days" : "Sold more than 90 days ago"}
          />
        </p>
      </div>
    </button>
  );
}
