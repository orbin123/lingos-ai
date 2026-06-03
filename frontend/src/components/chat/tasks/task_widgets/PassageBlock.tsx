"use client";

import ReactMarkdown from "react-markdown";

export function PassageBlock({ title, children }: { title?: string; children: string }) {
  return (
    <div className="tw-passage tw-passage-md">
      {title && <div className="tw-passage-label">{title}</div>}
      <ReactMarkdown>{children}</ReactMarkdown>
    </div>
  );
}
