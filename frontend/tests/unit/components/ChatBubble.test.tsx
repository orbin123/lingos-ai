import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ChatBubble } from "@/components/chat/ChatChrome";
import { renderWithProviders } from "../../utils/render";

describe("ChatBubble retry affordance", () => {
  it("renders a retry icon next to copy when onRetry is provided", async () => {
    const onRetry = vi.fn();
    renderWithProviders(
      <ChatBubble role="ai" copyText="⚠️ We couldn't prepare this activity." onRetry={onRetry}>
        ⚠️ We couldn&apos;t prepare this activity.
      </ChatBubble>,
    );

    const copy = screen.getByRole("button", { name: "Copy message" });
    const retry = screen.getByRole("button", { name: "Retry this activity" });
    expect(copy).toBeInTheDocument();
    expect(retry).toBeInTheDocument();

    await userEvent.click(retry);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("omits the retry icon when no onRetry handler is given", () => {
    renderWithProviders(
      <ChatBubble role="ai" copyText="Just an FYI.">
        Just an FYI.
      </ChatBubble>,
    );

    expect(
      screen.queryByRole("button", { name: "Retry this activity" }),
    ).not.toBeInTheDocument();
    // Copy still shows for AI bubbles with copyText.
    expect(screen.getByRole("button", { name: "Copy message" })).toBeInTheDocument();
  });

  it("disables the retry icon while a regeneration is in flight", () => {
    renderWithProviders(
      <ChatBubble role="ai" copyText="⚠️ error" onRetry={vi.fn()} retrying>
        ⚠️ error
      </ChatBubble>,
    );

    const retry = screen.getByRole("button", { name: "Resetting activity" });
    expect(retry).toBeDisabled();
  });
});
