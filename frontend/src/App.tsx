import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { APIProvider } from "@vis.gl/react-google-maps";
import { HomePage } from "./pages/HomePage";
import { SearchPage } from "./pages/SearchPage";
import { AreasPage } from "./pages/AreasPage";
import { ChatWidgetButton } from "./components/ai-assistant/ChatWidgetButton";

const queryClient = new QueryClient();
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "";

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/areas" element={<AreasPage />} />
            <Route path="/insights" element={
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Insights</h1>
                  <p className="text-gray-500">Coming soon</p>
                </div>
              </div>
            } />
          </Routes>
          <ChatWidgetButton />
        </BrowserRouter>
      </APIProvider>
    </QueryClientProvider>
  );
}

export default App;
