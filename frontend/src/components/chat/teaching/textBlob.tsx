import { Sparkles } from "lucide-react";
import type { TeachingMessage } from "./source";

interface TextBlobProps {
  message: TeachingMessage;
}

export function TextBlob({ message }: TextBlobProps) {
  const isAi = message.role === "ai";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: isAi ? "row" : "row-reverse",
        alignItems: "flex-end",
        gap: 10,
        marginBottom: 12,
        animation: "testChatFadeIn 0.35s ease both",
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
          boxShadow: "0 2px 12px rgba(60,100,200,0.26)",
        }}
      >
        {isAi ? <Sparkles size={14} strokeWidth={2.6} /> : "U"}
      </div>

      <div
        style={{
          maxWidth: "78%",
          display: "flex",
          flexDirection: "column",
          gap: 3,
          alignItems: isAi ? "flex-start" : "flex-end",
        }}
      >
        {message.name && (
          <div
            style={{
              fontSize: 11,
              fontWeight: 800,
              color: "oklch(45% 0.07 240)",
              padding: "0 4px",
            }}
          >
            {message.name}
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
          {message.content}
          {isAi && message.actions && message.actions.length > 0 && (
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
              {message.actions.map((label) => (
                <button
                  key={label}
                  type="button"
                  style={{
                    padding: "7px 13px",
                    borderRadius: 999,
                    background: "white",
                    border: "1px solid oklch(85% 0.025 240)",
                    fontSize: 12.5,
                    fontWeight: 700,
                    color: "oklch(20% 0.09 245)",
                    cursor: "default",
                    fontFamily: "inherit",
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
