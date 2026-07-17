import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = "Something went wrong", onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-rose-500/10 rounded-lg border border-rose-500/30">
      <AlertCircle className="w-10 h-10 text-rose-500 mb-3" />
      <h3 className="text-rose-300 font-medium mb-1">Error Loading Data</h3>
      <p className="text-rose-200/80 text-sm mb-4">{message}</p>

      {onRetry && (
        <button
          onClick={onRetry}
          aria-label="Retry loading data"
          className="flex items-center px-4 py-2 bg-slate-800 text-rose-300 border border-rose-500/30 rounded-md hover:bg-slate-700 transition-colors shadow-sm text-sm font-medium"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Try Again
        </button>
      )}
    </div>
  );
}
