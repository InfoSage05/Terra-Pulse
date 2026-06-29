import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ReviewFlagBanner } from "../components/area-detail/ReviewFlagBanner";
import React from "react";

describe("ReviewFlagBanner", () => {
  it("renders the banner prominently when needs_human_review is true", () => {
    render(<ReviewFlagBanner needsReview={true} />);
    
    const banner = screen.getByTestId("review-flag-banner");
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent(/Qualitative Disagreement Flag/i);
    expect(banner).toHaveTextContent(/contradicts the hard data/i);
  });

  it("does not render when needs_human_review is false", () => {
    render(<ReviewFlagBanner needsReview={false} />);
    
    const banner = screen.queryByTestId("review-flag-banner");
    expect(banner).not.toBeInTheDocument();
  });
});
