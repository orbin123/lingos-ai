import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { FormField } from "@/components/auth/FormField";
import { renderWithProviders } from "../../utils/render";

describe("FormField", () => {
  it("links the label to the input and derives an id from the label", () => {
    renderWithProviders(<FormField label="Email address" />);
    const input = screen.getByLabelText("Email address");
    expect(input).toHaveAttribute("id", "field-email-address");
  });

  it("renders the hint when there is no error", () => {
    renderWithProviders(<FormField label="Password" hint="8+ characters" />);
    expect(screen.getByText("8+ characters")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toHaveAttribute(
      "aria-invalid",
      "false",
    );
  });

  it("renders the error and marks the input invalid, hiding the hint", () => {
    renderWithProviders(
      <FormField label="Email" hint="we never share it" error="Required" />,
    );
    const input = screen.getByLabelText("Email");
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByText("Required")).toBeInTheDocument();
    // Error takes precedence — the hint is not shown.
    expect(screen.queryByText("we never share it")).not.toBeInTheDocument();
  });

  it("toggles password visibility via the show/hide control", async () => {
    const user = userEvent.setup();
    renderWithProviders(<FormField label="Password" type="password" />);

    const input = screen.getByLabelText("Password");
    expect(input).toHaveAttribute("type", "password");

    await user.click(screen.getByRole("button", { name: /show password/i }));
    expect(input).toHaveAttribute("type", "text");

    await user.click(screen.getByRole("button", { name: /hide password/i }));
    expect(input).toHaveAttribute("type", "password");
  });
});
