import React from "react";

interface SplitLayoutProps {
  mapPanel: React.ReactNode;
  listPanel: React.ReactNode;
}

export function SplitLayout({ mapPanel, listPanel }: SplitLayoutProps) {
  return (
    <div className="h-screen w-full flex flex-col lg:flex-row">
      <div className="w-full lg:w-[55%] h-[55vh] lg:h-full relative flex-shrink-0">
        {mapPanel}
      </div>
      <div className="w-full lg:w-[45%] h-[45vh] lg:h-full flex flex-col overflow-hidden border-t lg:border-t-0 lg:border-l border-gray-200">
        {listPanel}
      </div>
    </div>
  );
}
