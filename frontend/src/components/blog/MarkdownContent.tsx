"use client";

import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";

const HEADING = "oklch(15% 0.09 245)";
const BODY = "oklch(32% 0.05 240)";
const ACCENT = "oklch(40% 0.14 240)";

// Article-grade Markdown: block elements styled to match the marketing
// typography (Plus Jakarta Sans, blue-grey palette). Links open safely.
const components: Components = {
  h1: ({ children }) => (
    <h2 style={{ fontSize: 30, fontWeight: 800, color: HEADING, margin: "40px 0 16px", lineHeight: 1.2 }}>
      {children}
    </h2>
  ),
  h2: ({ children }) => (
    <h2 style={{ fontSize: 26, fontWeight: 800, color: HEADING, margin: "36px 0 14px", lineHeight: 1.25 }}>
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 style={{ fontSize: 21, fontWeight: 700, color: HEADING, margin: "28px 0 12px", lineHeight: 1.3 }}>
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p style={{ fontSize: 17, lineHeight: 1.75, color: BODY, margin: "0 0 20px" }}>{children}</p>
  ),
  ul: ({ children }) => (
    <ul style={{ margin: "0 0 20px", paddingLeft: 24, display: "grid", gap: 8 }}>{children}</ul>
  ),
  ol: ({ children }) => (
    <ol style={{ margin: "0 0 20px", paddingLeft: 24, display: "grid", gap: 8 }}>{children}</ol>
  ),
  li: ({ children }) => (
    <li style={{ fontSize: 17, lineHeight: 1.7, color: BODY }}>{children}</li>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{ color: ACCENT, fontWeight: 600, textDecoration: "underline" }}
    >
      {children}
    </a>
  ),
  strong: ({ children }) => (
    <strong style={{ color: HEADING, fontWeight: 700 }}>{children}</strong>
  ),
  em: ({ children }) => <em style={{ fontStyle: "italic" }}>{children}</em>,
  blockquote: ({ children }) => (
    <blockquote
      style={{
        margin: "0 0 22px",
        padding: "8px 22px",
        borderLeft: "4px solid oklch(80% 0.1 240)",
        color: "oklch(40% 0.05 240)",
        fontStyle: "italic",
      }}
    >
      {children}
    </blockquote>
  ),
  code: ({ children }) => (
    <code
      style={{
        background: "oklch(94% 0.02 240)",
        borderRadius: 6,
        padding: "2px 6px",
        fontSize: 15,
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
        color: "oklch(30% 0.08 260)",
      }}
    >
      {children}
    </code>
  ),
  hr: () => (
    <hr style={{ border: "none", borderTop: "1px solid oklch(90% 0.02 240)", margin: "32px 0" }} />
  ),
};

export function MarkdownContent({ children }: { children: string }) {
  return <ReactMarkdown components={components}>{children}</ReactMarkdown>;
}
