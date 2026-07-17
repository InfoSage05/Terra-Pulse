import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { HomePage } from "./pages/HomePage";
import { SearchPage } from "./pages/SearchPage";
import { AreasPage } from "./pages/AreasPage";
import { MapPage } from "./pages/MapPage";
import { InsightsPage } from "./pages/InsightsPage";
import { ChatWidgetButton } from "./components/ai-assistant/ChatWidgetButton";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/areas" element={<AreasPage />} />
          <Route path="/insights" element={<InsightsPage />} />
        </Routes>
        <ChatWidgetButton />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
