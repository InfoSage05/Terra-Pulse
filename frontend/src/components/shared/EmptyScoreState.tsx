import React from "react";
import { Info } from "lucide-react";

export function EmptyScoreState({ scoreName }: { scoreName: string }) {
  return (
    <div className="flex items-center text-slate-400 text-sm italic font-sans" data-testid="empty-score-state">
      <Info className="w-4 h-4 mr-1.5 text-slate-500" />
      {scoreName} not yet available
    </div>
  );
}
