"use client";

import { useEffect, type CSSProperties, type ReactNode } from "react";
import { AlertTriangle, Info, X } from "lucide-react";

type DialogTone = "default" | "danger" | "warning";

interface AppConfirmDialogProps {
  open: boolean;
  title: string;
  description: ReactNode;
  confirmLabel: string;
  cancelLabel?: string;
  loadingLabel?: string;
  isLoading?: boolean;
  tone?: DialogTone;
  onCancel: () => void;
  onConfirm: () => void;
}

const toneColor: Record<DialogTone, string> = {
  default: "oklch(52% 0.18 240)",
  danger: "oklch(54% 0.2 28)",
  warning: "oklch(62% 0.16 65)",
};

const toneBackground: Record<DialogTone, string> = {
  default: "oklch(94% 0.045 240)",
  danger: "oklch(94% 0.055 28)",
  warning: "oklch(95% 0.07 65)",
};

export function AppConfirmDialog({
  open,
  title,
  description,
  confirmLabel,
  cancelLabel = "Cancel",
  loadingLabel,
  isLoading = false,
  tone = "default",
  onCancel,
  onConfirm,
}: AppConfirmDialogProps) {
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !isLoading) {
        onCancel();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isLoading, onCancel, open]);

  if (!open) return null;

  const Icon = tone === "default" ? Info : AlertTriangle;

  return (
    <div
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isLoading) {
          onCancel();
        }
      }}
      style={overlayStyle}
    >
      <div
        aria-describedby="app-confirm-dialog-description"
        aria-labelledby="app-confirm-dialog-title"
        aria-modal="true"
        role="dialog"
        style={dialogStyle}
      >
        <div style={headerStyle}>
          <div
            aria-hidden
            style={{
              ...iconWrapStyle,
              background: toneBackground[tone],
              color: toneColor[tone],
            }}
          >
            <Icon size={19} strokeWidth={2.4} />
          </div>
          <button
            aria-label="Close dialog"
            disabled={isLoading}
            onClick={onCancel}
            style={{
              ...iconButtonStyle,
              cursor: isLoading ? "not-allowed" : "pointer",
              opacity: isLoading ? 0.45 : 1,
            }}
            type="button"
          >
            <X size={17} strokeWidth={2.4} />
          </button>
        </div>

        <h2 id="app-confirm-dialog-title" style={titleStyle}>
          {title}
        </h2>
        <div id="app-confirm-dialog-description" style={descriptionStyle}>
          {description}
        </div>

        <div style={actionsStyle}>
          <button
            disabled={isLoading}
            onClick={onCancel}
            style={{
              ...buttonStyle,
              background: "white",
              borderColor: "oklch(84% 0.025 240)",
              color: "oklch(28% 0.08 245)",
              cursor: isLoading ? "not-allowed" : "pointer",
              opacity: isLoading ? 0.55 : 1,
            }}
            type="button"
          >
            {cancelLabel}
          </button>
          <button
            disabled={isLoading}
            onClick={onConfirm}
            style={{
              ...buttonStyle,
              background: toneColor[tone],
              borderColor: toneColor[tone],
              color: "white",
              cursor: isLoading ? "wait" : "pointer",
              opacity: isLoading ? 0.72 : 1,
              boxShadow: `0 10px 24px ${toneColor[tone]}3D`,
            }}
            type="button"
          >
            {isLoading ? loadingLabel || confirmLabel : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

const overlayStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  zIndex: 120,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 20,
  background: "rgba(12,22,42,0.46)",
  backdropFilter: "blur(10px)",
  WebkitBackdropFilter: "blur(10px)",
};

const dialogStyle: CSSProperties = {
  width: "min(100%, 440px)",
  borderRadius: 8,
  border: "1px solid rgba(255,255,255,0.92)",
  background: "rgba(255,255,255,0.96)",
  boxShadow: "0 30px 90px rgba(18,34,70,0.28), 0 2px 10px rgba(70,110,180,0.08)",
  color: "oklch(18% 0.06 240)",
  fontFamily: "'Plus Jakarta Sans', sans-serif",
  padding: 24,
};

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 16,
  marginBottom: 16,
};

const iconWrapStyle: CSSProperties = {
  width: 38,
  height: 38,
  borderRadius: 8,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
};

const iconButtonStyle: CSSProperties = {
  width: 34,
  height: 34,
  borderRadius: "50%",
  border: "1px solid oklch(86% 0.025 240)",
  background: "white",
  color: "oklch(42% 0.06 240)",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
};

const titleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(15% 0.09 245)",
  fontSize: 21,
  fontWeight: 800,
  lineHeight: 1.22,
};

const descriptionStyle: CSSProperties = {
  marginTop: 9,
  color: "oklch(42% 0.06 240)",
  fontSize: 14,
  fontWeight: 600,
  lineHeight: 1.58,
};

const actionsStyle: CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  gap: 10,
  marginTop: 24,
};

const buttonStyle: CSSProperties = {
  minWidth: 112,
  minHeight: 42,
  borderRadius: 8,
  border: "1px solid transparent",
  padding: "0 16px",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 800,
};
