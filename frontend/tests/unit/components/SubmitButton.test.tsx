import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { SubmitButton } from "@/components/auth/SubmitButton";
import { renderWithProviders } from "../../utils/render";

describe("SubmitButton", () => {
  it("shows its children and is enabled when idle", () => {
    renderWithProviders(<SubmitButton>Sign in</SubmitButton>);
    const btn = screen.getByRole("button", { name: "Sign in" });
    expect(btn).toBeEnabled();
    expect(btn).toHaveAttribute("type", "submit");
  });

  it("shows the loading text and disables itself while loading", () => {
    renderWithProviders(
      <SubmitButton loading loadingText="Signing in…">
        Sign in
      </SubmitButton>,
    );
    const btn = screen.getByRole("button");
    expect(btn).toBeDisabled();
    expect(btn).toHaveTextContent("Signing in…");
    expect(btn).not.toHaveTextContent("Sign in");
  });

  it("falls back to a default loading label", () => {
    renderWithProviders(<SubmitButton loading>Go</SubmitButton>);
    expect(screen.getByRole("button")).toHaveTextContent("Loading...");
  });

  it("respects an explicit disabled prop even when not loading", () => {
    renderWithProviders(<SubmitButton disabled>Go</SubmitButton>);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
