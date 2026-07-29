import React from "react";

interface ListingsCountProps {
  total: number;
  showing: number;
}

export function ListingsCount({ total, showing }: ListingsCountProps) {
  return (
    <div className="px-5 py-2 text-xs text-slate-500 bg-slate-900/60 border-b border-slate-800 font-mono">
      Showing {showing} of {total.toLocaleString()} properties
    </div>
  );
}
