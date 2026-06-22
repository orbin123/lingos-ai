import { describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError } from "axios";

import { ActiveSessionBlock } from "@/components/dashboard/DailyTaskPanel";
import { renderWithProviders } from "../../utils/render";

/** Build the AxiosError the backend now returns when task generation fails
 * (a transient 503 with a machine-readable code). */
function taskGenFailedError(): AxiosError {
  return new AxiosError(
    "Service Unavailable",
    "ERR_BAD_RESPONSE",
    undefined,
    undefined,
    {
      status: 503,
      statusText: "Service Unavailable",
      data: {
        detail: {
          code: "task_generation_failed",
          message: "We couldn't prepare today's lesson. Please try again.",
        },
      },
      headers: {},
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      config: {} as any,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } as any,
  );
}

const baseProps = {
  activities: [],
  topic: "Past tense errors",
  isPreview: false,
  isDepthDay: false,
  explanationBrief: null,
  sessionStatus: null,
  isStarting: false,
};

describe("ActiveSessionBlock — task-generation retry", () => {
  it("flips to a Retry session button on a 503 task_generation_failed error and re-runs onStart", async () => {
    const onStart = vi.fn();
    renderWithProviders(
      <ActiveSessionBlock
        {...baseProps}
        startError={taskGenFailedError()}
        onStart={onStart}
      />,
    );

    const button = screen.getByRole("button", { name: /retry session/i });
    expect(button).toBeInTheDocument();
    expect(
      screen.getByText(/couldn't prepare today's lesson/i),
    ).toBeInTheDocument();

    await userEvent.click(button);
    expect(onStart).toHaveBeenCalledTimes(1);
  });

  it("shows the normal Start session button when there is no error", () => {
    renderWithProviders(
      <ActiveSessionBlock {...baseProps} startError={null} onStart={vi.fn()} />,
    );

    expect(
      screen.getByRole("button", { name: /start session/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /retry session/i }),
    ).not.toBeInTheDocument();
  });
});
