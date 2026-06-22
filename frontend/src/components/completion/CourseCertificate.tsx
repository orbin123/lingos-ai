"use client";

import type { CourseLengthLiteral } from "@/lib/preferences-api";

interface CourseCertificateProps {
  /** Learner's display name (falls back to a neutral label upstream). */
  name: string;
  courseLength: CourseLengthLiteral;
  /** ISO timestamp of completion. */
  completedAt: string;
}

function courseTitle(courseLength: CourseLengthLiteral): string {
  return courseLength === "48w"
    ? "48-Week English Course"
    : "24-Week English Course";
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Print-friendly completion certificate. The parent page drives "Download"
 * via `window.print()`; the page's `@media print` rules hide everything else
 * so only this card lands on the page/PDF.
 */
export function CourseCertificate({
  name,
  courseLength,
  completedAt,
}: CourseCertificateProps) {
  return (
    <div
      className="course-certificate"
      style={{
        position: "relative",
        width: "100%",
        maxWidth: 720,
        margin: "0 auto",
        background: "#fffdf8",
        border: "2px solid oklch(78% 0.09 85)",
        borderRadius: 18,
        padding: "44px 48px",
        boxShadow: "0 10px 40px rgba(60,50,20,0.12)",
        textAlign: "center",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        color: "oklch(28% 0.05 250)",
      }}
    >
      {/* Inner hairline frame */}
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 10,
          border: "1px solid oklch(85% 0.06 85)",
          borderRadius: 12,
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          fontSize: 12,
          fontWeight: 800,
          letterSpacing: "0.22em",
          textTransform: "uppercase",
          color: "oklch(55% 0.13 85)",
        }}
      >
        Certificate of Completion
      </div>

      <div
        style={{
          marginTop: 6,
          fontSize: 13,
          fontWeight: 700,
          color: "oklch(45% 0.07 240)",
        }}
      >
        LingosAI
      </div>

      <div
        style={{
          margin: "26px 0 8px",
          fontSize: 13.5,
          color: "oklch(45% 0.05 250)",
        }}
      >
        This certifies that
      </div>

      <div
        style={{
          fontSize: 34,
          fontWeight: 800,
          lineHeight: 1.15,
          color: "oklch(22% 0.09 250)",
          padding: "0 8px",
          wordBreak: "break-word",
        }}
      >
        {name}
      </div>

      <div
        style={{
          width: 220,
          height: 1,
          background: "oklch(82% 0.06 85)",
          margin: "14px auto 18px",
        }}
      />

      <div
        style={{
          fontSize: 14.5,
          lineHeight: 1.7,
          color: "oklch(40% 0.05 250)",
          maxWidth: 520,
          marginInline: "auto",
        }}
      >
        has successfully completed every lesson of the{" "}
        <strong style={{ color: "oklch(28% 0.09 250)" }}>
          {courseTitle(courseLength)}
        </strong>{" "}
        and demonstrated sustained progress across reading, writing, listening,
        and speaking.
      </div>

      <div
        style={{
          marginTop: 30,
          fontSize: 13,
          fontWeight: 700,
          color: "oklch(45% 0.07 240)",
        }}
      >
        Completed on {formatDate(completedAt)}
      </div>
    </div>
  );
}
