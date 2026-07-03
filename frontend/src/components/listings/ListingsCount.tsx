import React from "react";

interface ListingsCountProps {
  total: number;
  showing: number;
}

export function ListingsCount({ total, showing }: ListingsCountProps) {
  return (
    <div className="px-5 py-2 text-xs text-gray-400 bg-gray-50 border-b border-gray-100">
      Showing {showing} of {total.toLocaleString()} properties
    </div>
  );
}
