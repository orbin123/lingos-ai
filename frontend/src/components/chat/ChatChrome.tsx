"use client";

import type React from "react";
import { useState } from "react";
import { Check, ChevronLeft, Copy, RotateCcw } from "lucide-react";
import type { CSSProperties } from "react";

export type ChatSectionTone = "intro" | "task" | "score" | "feedback";

export interface LessonMetaCardProps {
  eyebrow: string;
  title: string;
  focus?: string;
}

export function ChatGlobalStyles() {
  return (
    <>
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <style>{`
        *, *::before, *::after { box-sizing: border-box; }
        body { overflow-x: hidden; }
        @keyframes chatFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes testChatFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes streamPulse {
          0%, 100% { opacity: 0.25; transform: scaleY(0.75); }
          50% { opacity: 1; transform: scaleY(1); }
        }
        strong { font-weight: 700; }
        em { font-style: italic; }
        @media (max-width: 720px) {
          .chat-topbar-inner {
            flex-wrap: wrap;
          }
          .chat-topbar-actions {
            margin-left: auto;
          }
        }
        @media (max-width: 560px) {
          .chat-lesson-card {
            border-radius: 18px;
            padding: 16px 17px;
          }
          .chat-bubble-content {
            max-width: 82% !important;
          }
        }
      `}</style>
    </>
  );
}

export function ChatPageShell({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "oklch(91% 0.04 245)",
        color: "oklch(18% 0.06 240)",
        position: "relative",
      }}
    >
      <div
        aria-hidden
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />
      {children}
    </div>
  );
}

export function ChatMain({
  children,
  bottomPadding = 120,
}: {
  children: React.ReactNode;
  bottomPadding?: number;
}) {
  return (
    <main
      style={{
        position: "relative",
        zIndex: 1,
        maxWidth: 720,
        margin: "0 auto",
        padding: `28px 20px ${bottomPadding}px`,
      }}
    >
      {children}
    </main>
  );
}

export function ChatTopbar({
  subtitle,
  onBack,
  actions,
}: {
  subtitle: string;
  onBack?: () => void;
  actions?: React.ReactNode;
}) {
  return (
    <div
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        background: "rgba(232,240,252,0.55)",
        borderBottom: "1px solid rgba(140,170,220,0.14)",
      }}
    >
      <div
        className="chat-topbar-inner"
        style={{
          maxWidth: 920,
          margin: "0 auto",
          padding: "14px 20px",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <button
          type="button"
          className="chat-round-icon-btn"
          aria-label="Back"
          title="Back"
          onClick={onBack}
          style={{
            cursor: onBack ? "pointer" : "default",
          }}
        >
          <ChevronLeft size={18} strokeWidth={2.4} />
        </button>

        <LingosBrand subtitle={subtitle} />

        <div style={{ flex: 1 }} />

        {actions && (
          <div className="chat-topbar-actions" style={{ display: "flex", alignItems: "center" }}>
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}

export function LingosBrand({ subtitle }: { subtitle: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <LingosLogo />
      <div>
        <div style={{ fontSize: 16, fontWeight: 800, color: "oklch(20% 0.09 245)" }}>
          LingosAI
        </div>
        <div style={{ fontSize: 11.5, color: "oklch(42% 0.07 240)", fontWeight: 700 }}>
          {subtitle}
        </div>
      </div>
    </div>
  );
}

export function LingosLogo() {
  return (
    <div
      aria-hidden
      style={{
        width: 34,
        height: 34,
        borderRadius: 9,
        background: "oklch(52% 0.18 240)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        fontSize: 15,
        fontWeight: 900,
        boxShadow: "0 4px 12px rgba(60,100,200,0.35)",
      }}
    >
      L
    </div>
  );
}

export function LessonMetaCard({ eyebrow, title, focus }: LessonMetaCardProps) {
  return (
    <section
      className="chat-lesson-card"
      style={{
        borderRadius: 22,
        padding: "18px 20px",
        marginBottom: 18,
        background: "linear-gradient(135deg, rgba(255,255,255,0.96), rgba(238,245,255,0.96))",
        border: "1.5px solid rgba(255,255,255,0.9)",
        boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
      }}
    >
      <div style={{ fontSize: 12, fontWeight: 800, color: "#0070C4", textTransform: "uppercase" }}>
        {eyebrow}
      </div>
      <h1
        style={{
          margin: "5px 0 7px",
          fontSize: 22,
          lineHeight: 1.2,
          fontWeight: 800,
          color: "oklch(20% 0.09 245)",
        }}
      >
        {title}
      </h1>
      {focus && (
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.55, color: "oklch(42% 0.07 240)" }}>
          {focus}
        </p>
      )}
    </section>
  );
}

export function SectionMarker({
  tone,
  icon,
  children,
}: {
  tone: ChatSectionTone;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  const colors: Record<ChatSectionTone, string> = {
    intro: "oklch(62% 0.16 240)",
    task: "oklch(70% 0.16 290)",
    score: "oklch(70% 0.16 155)",
    feedback: "oklch(76% 0.15 60)",
  };

  return (
    <div style={{ display: "flex", justifyContent: "center", margin: "10px 0 14px" }}>
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 7,
          padding: "6px 13px",
          borderRadius: 999,
          background: "rgba(255,255,255,0.96)",
          border: "1px solid oklch(85% 0.025 240)",
          fontSize: 12.5,
          fontWeight: 800,
          color: colors[tone],
          boxShadow: "0 2px 8px rgba(80,110,180,0.06)",
          animation: "chatFadeIn 0.35s ease both",
        }}
      >
        {icon}
        <span>{children}</span>
      </div>
    </div>
  );
}

const bubbleActionButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 6,
  borderRadius: 999,
  border: "1px solid oklch(88% 0.02 245)",
  background: "white",
  fontFamily: "inherit",
  cursor: "pointer",
};

function CopyMessageButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable — silently ignore */
    }
  };

  return (
    <button
      type="button"
      onClick={copy}
      aria-label={copied ? "Copied" : "Copy message"}
      title={copied ? "Copied" : "Copy message"}
      className="chat-bubble-copy"
      style={{
        ...bubbleActionButtonStyle,
        color: copied ? "oklch(48% 0.16 155)" : "oklch(45% 0.07 240)",
      }}
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
}

function RetryActivityButton({
  onClick,
  disabled,
  loading,
}: {
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={loading ? "Resetting activity" : "Retry this activity"}
      title={loading ? "Resetting…" : "Retry this activity"}
      className="chat-bubble-retry"
      style={{
        ...bubbleActionButtonStyle,
        color: "oklch(45% 0.07 240)",
        opacity: disabled ? 0.55 : 1,
        cursor: disabled ? "default" : "pointer",
      }}
    >
      <RotateCcw size={13} />
    </button>
  );
}

export function ChatBubble({
  role,
  name,
  children,
  actions,
  streaming,
  onAction,
  copyText,
  onRetry,
  retrying,
}: {
  role: "ai" | "you";
  name?: string;
  children: React.ReactNode;
  actions?: string[];
  streaming?: boolean;
  onAction?: (label: string) => void;
  copyText?: string;
  onRetry?: () => void;
  retrying?: boolean;
}) {
  const isAi = role === "ai";
  const showCopy = isAi && !streaming && Boolean(copyText && copyText.trim());
  const showRetry = isAi && !streaming && Boolean(onRetry);
  const showBubbleActions = showCopy || showRetry;

  return (
    <div
      style={{
        display: "flex",
        flexDirection: isAi ? "row" : "row-reverse",
        alignItems: "flex-end",
        gap: 10,
        marginBottom: 12,
        animation: "chatFadeIn 0.35s ease both",
      }}
    >
      <div
        aria-hidden
        style={{
          width: 30,
          height: 30,
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          marginBottom: 2,
          background: isAi ? "oklch(52% 0.18 240)" : "oklch(28% 0.06 260)",
          color: "white",
          fontSize: 12,
          fontWeight: 800,
          boxShadow: "0 2px 12px rgba(60,100,200,0.26)",
        }}
      >
        {isAi ? "L" : "U"}
      </div>

      <div
        className="chat-bubble-content"
        style={{
          maxWidth: "78%",
          display: "flex",
          flexDirection: "column",
          gap: 3,
          alignItems: isAi ? "flex-start" : "flex-end",
        }}
      >
        {name && (
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              color: "oklch(45% 0.07 240)",
              padding: "0 4px",
            }}
          >
            {name}
          </div>
        )}
        <div
          style={{
            padding: "13px 16px",
            borderRadius: 18,
            borderBottomLeftRadius: isAi ? 6 : 18,
            borderBottomRightRadius: isAi ? 18 : 6,
            fontSize: 14.5,
            lineHeight: 1.55,
            wordBreak: "break-word",
            background: isAi ? "white" : "oklch(52% 0.18 240)",
            border: isAi ? "1px solid oklch(86% 0.025 240)" : "1px solid transparent",
            color: isAi ? "oklch(18% 0.06 240)" : "white",
            boxShadow: isAi
              ? "0 2px 10px rgba(80,110,180,0.06)"
              : "0 8px 26px rgba(55,100,220,0.28)",
          }}
        >
          {children}
          {isAi && streaming && (
            <span
              aria-hidden
              style={{
                display: "inline-block",
                width: 7,
                height: 16,
                marginLeft: 3,
                borderRadius: 999,
                background: "oklch(52% 0.18 240)",
                verticalAlign: "-3px",
                animation: "streamPulse 0.9s ease-in-out infinite",
              }}
            />
          )}
          {isAi && actions && actions.length > 0 && (
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
              {actions.map((label) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => onAction?.(label)}
                  style={{
                    padding: "7px 13px",
                    borderRadius: 999,
                    background: "white",
                    border: "1px solid oklch(85% 0.025 240)",
                    fontSize: 12.5,
                    fontWeight: 700,
                    color: "oklch(20% 0.09 245)",
                    cursor: onAction ? "pointer" : "default",
                    fontFamily: "inherit",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
        {showBubbleActions && (
          <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
            {showCopy && <CopyMessageButton text={copyText as string} />}
            {showRetry && (
              <RetryActivityButton
                onClick={onRetry as () => void}
                disabled={retrying}
                loading={retrying}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export const roundIconButton: React.CSSProperties = {
  width: 36,
  height: 36,
  borderRadius: "50%",
  background: "white",
  border: "1px solid oklch(85% 0.025 240)",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  color: "oklch(28% 0.08 245)",
  flexShrink: 0,
};
