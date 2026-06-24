import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ReconnectNotice } from "@/components/chat/ReconnectNotice";
import { renderWithProviders } from "../../utils/render";

describe("ReconnectNotice", () => {
  it("shows a working 'Reload session' CTA once the reconnect budget is spent", async () => {
    const onReload = vi.fn();
    renderWithProviders(
      <ReconnectNotice
        connectionState="closed"
        accessBlocked={false}
        isReconnecting={false}
        exhausted
        onReload={onReload}
      />,
    );

    const button = screen.getByRole("button", { name: "Reload session" });
    expect(button).toBeInTheDocument();
    expect(screen.getByText(/couldn.t reconnect/i)).toBeInTheDocument();

    await userEvent.click(button);
    expect(onReload).toHaveBeenCalledTimes(1);
  });

  it("shows a calm 'Reconnecting…' (no CTA) while actively recovering", () => {
    renderWithProviders(
      <ReconnectNotice
        connectionState="connecting"
        accessBlocked={false}
        isReconnecting
        exhausted={false}
        onReload={vi.fn()}
      />,
    );

    expect(screen.getByText("Reconnecting…")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Reload session" }),
    ).not.toBeInTheDocument();
  });

  it("treats a freshly closed socket as recovering, not dead", () => {
    renderWithProviders(
      <ReconnectNotice
        connectionState="closed"
        accessBlocked={false}
        isReconnecting={false}
        exhausted={false}
        onReload={vi.fn()}
      />,
    );

    expect(screen.getByText("Reconnecting…")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Reload session" }),
    ).not.toBeInTheDocument();
  });

  it("offers an upgrade (not a reload) when access was revoked", () => {
    renderWithProviders(
      <ReconnectNotice
        connectionState="error"
        accessBlocked
        isReconnecting={false}
        exhausted={false}
        onReload={vi.fn()}
      />,
    );

    expect(screen.getByRole("link", { name: /upgrade now/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Reload session" }),
    ).not.toBeInTheDocument();
  });
});
