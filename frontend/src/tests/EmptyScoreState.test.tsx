import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { EmptyScoreState } from "../components/shared/EmptyScoreState";
import React from "react";

describe("EmptyScoreState", () => {
  it("renders distinct message for missing score data", () => {
    render(<EmptyScoreState scoreName="Affordability" />);
    
    const element = screen.getByTestId("empty-score-state");
    expect(element).toBeInTheDocument();
    expect(element).toHaveTextContent(/Affordability not yet available/i);
  });
});
