import React from "react";
import { SiteHeader } from "../components/layout/SiteHeader";
import { HeroSection } from "../components/home/HeroSection";
import { FeaturedListings } from "../components/home/FeaturedListings";
import { MapPreviewStrip } from "../components/home/MapPreviewStrip";
import { AreaBrowser } from "../components/home/AreaBrowser";
import { InsightsBanner } from "../components/home/InsightsBanner";
import { RecentlyViewed } from "../components/home/RecentlyViewed";

export function HomePage() {
  return (
    <div className="min-h-screen bg-slate-950">
      <SiteHeader />
      <HeroSection />
      <FeaturedListings />
      <MapPreviewStrip />
      <AreaBrowser />
      <InsightsBanner />
      <RecentlyViewed />
    </div>
  );
}
