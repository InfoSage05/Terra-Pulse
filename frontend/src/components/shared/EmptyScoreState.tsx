import React from "react";
import { Info } from "lucide-react";

export function EmptyScoreState({ scoreName }: { scoreName: string }) {
  return (
    <div className="flex items-center text-gray-500 text-sm italic" data-testid="empty-score-state">
      <Info className="w-4 h-4 mr-1.5 text-gray-400" />
      {scoreName} not yet available
    </div>
  );
}
