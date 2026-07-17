import React from "react";

interface SplitLayoutProps {
  mapPanel: React.ReactNode;
  listPanel: React.ReactNode;
}

export function SplitLayout({ mapPanel, listPanel }: SplitLayoutProps) {
  return (
    <div className="flex-1 w-full flex flex-col lg:flex-row min-h-0">
      <div className="w-full lg:w-[55%] h-[50vh] lg:h-full relative flex-shrink-0 p-2 bg-slate-950">
        <div className="w-full h-full rounded-lg overflow-hidden border border-slate-800 shadow-sm">
          {mapPanel}
        </div>
      </div>
      <div className="w-full lg:w-[45%] h-[50vh] lg:h-full flex flex-col overflow-hidden bg-slate-950">
        {listPanel}
      </div>
    </div>
  );
}
