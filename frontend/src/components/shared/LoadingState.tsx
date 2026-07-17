import React from "react";

export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex justify-center items-center p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-500"></div>
      <span className="ml-3 text-slate-400">{message}</span>
    </div>
  );
}
