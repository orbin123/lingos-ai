import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { CourseCertificate } from "@/components/completion/CourseCertificate";

describe("CourseCertificate", () => {
  it("renders the learner name, title, 24-week course label and formatted date", () => {
    render(
      <CourseCertificate
        name="Orbin Sunny"
        courseLength="24w"
        completedAt="2026-06-22T10:00:00Z"
      />,
    );

    expect(screen.getByText("Certificate of Completion")).toBeInTheDocument();
    // Name appears in the certificate body.
    expect(screen.getByText("Orbin Sunny")).toBeInTheDocument();
    expect(screen.getByText("24-Week English Course")).toBeInTheDocument();
    // Locale-formatted long date (month spelled out, year present).
    expect(screen.getByText(/2026/)).toBeInTheDocument();
    expect(screen.getByText(/Completed on/)).toBeInTheDocument();
  });

  it("uses the 48-week label for the long course", () => {
    render(
      <CourseCertificate
        name="Jane Doe"
        courseLength="48w"
        completedAt="2026-12-01T10:00:00Z"
      />,
    );

    expect(screen.getByText("48-Week English Course")).toBeInTheDocument();
    expect(screen.queryByText("24-Week English Course")).not.toBeInTheDocument();
  });

  it("degrades gracefully on an unparseable completion date", () => {
    render(
      <CourseCertificate name="Sam" courseLength="24w" completedAt="not-a-date" />,
    );

    // Still renders the rest of the certificate; the date just collapses to "".
    expect(screen.getByText("Sam")).toBeInTheDocument();
    expect(screen.getByText(/Completed on/)).toBeInTheDocument();
  });
});
