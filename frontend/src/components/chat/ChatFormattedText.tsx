"use client";

import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";

/** Inline-only markdown for teacher chat bubbles (bold grammar, italic L1 gloss). */
const chatMarkdownComponents: Components = {
  p: ({ children }) => <span className="chat-md-block">{children}</span>,
  h1: ({ children }) => <span className="chat-md-block">{children}</span>,
  h2: ({ children }) => <span className="chat-md-block">{children}</span>,
  h3: ({ children }) => <span className="chat-md-block">{children}</span>,
  h4: ({ children }) => <span className="chat-md-block">{children}</span>,
  h5: ({ children }) => <span className="chat-md-block">{children}</span>,
  h6: ({ children }) => <span className="chat-md-block">{children}</span>,
  ul: ({ children }) => <span className="chat-md-block">{children}</span>,
  ol: ({ children }) => <span className="chat-md-block">{children}</span>,
  li: ({ children }) => <span>{children} </span>,
  a: ({ children }) => <span>{children}</span>,
  img: () => null,
  pre: ({ children }) => <span className="chat-md-block">{children}</span>,
  code: ({ children }) => <span>{children}</span>,
  blockquote: ({ children }) => <span className="chat-md-block">{children}</span>,
  strong: ({ children }) => <strong className="chat-md-strong">{children}</strong>,
  em: ({ children }) => <em className="chat-md-em">{children}</em>,
};

export function ChatFormattedText({ children }: { children: string }) {
  return (
    <span className="chat-md">
      <ReactMarkdown components={chatMarkdownComponents}>{children}</ReactMarkdown>
    </span>
  );
}
