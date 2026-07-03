import React from "react";

interface ListingsCountProps {
  total: number;
  showing: number;
}

export function ListingsCount({ total, showing }: ListingsCountProps) {
  return (
    <div className="px-4 py-2 text-sm text-gray-500 bg-gray-50 border-b border-gray-100">
      Showing {showing} of {total.toLocaleString()} properties
    </div>
  );
}
