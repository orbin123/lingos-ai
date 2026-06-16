import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { ServerErrorBanner } from "@/components/auth/ServerErrorBanner";
import { renderWithProviders } from "../../utils/render";

describe("ServerErrorBanner", () => {
  it("renders nothing when there is no message", () => {
    const { container } = renderWithProviders(<ServerErrorBanner />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing for an empty-string message", () => {
    const { container } = renderWithProviders(<ServerErrorBanner message="" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("renders an alert with the message when present", () => {
    renderWithProviders(<ServerErrorBanner message="Invalid credentials" />);
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Invalid credentials");
  });
});
