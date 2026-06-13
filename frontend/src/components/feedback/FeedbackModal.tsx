"use client";

import { useEffect, useState, type CSSProperties } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Star, X } from "lucide-react";

import { feedbackApi, type FeedbackSubmit } from "@/lib/feedback-api";
import { useFeedbackStore } from "@/store/feedbackStore";

const APP_VERSION = process.env.NEXT_PUBLIC_APP_VERSION ?? "web";

const STAR_ON = "oklch(75% 0.15 80)";
const STAR_ON_BORDER = "oklch(70% 0.15 80)";
const STAR_OFF = "oklch(82% 0.02 245)";

/**
 * In-app product feedback prompt. Open/close is driven by the global
 * feedback store; the surrounding pages mount this via <FeedbackPrompt />.
 */
export function FeedbackModal() {
  const isOpen = useFeedbackStore((s) => s.isOpen);
  const close = useFeedbackStore((s) => s.close);
  const queryClient = useQueryClient();

  const [rating, setRating] = useState(0);
  const [hovered, setHovered] = useState(0);
  const [positive, setPositive] = useState("");
  const [improvement, setImprovement] = useState("");
  const [bug, setBug] = useState("");

  const resetFields = () => {
    setRating(0);
    setHovered(0);
    setPositive("");
    setImprovement("");
    setBug("");
  };

  const submitMutation = useMutation({
    mutationFn: (data: FeedbackSubmit) => feedbackApi.submit(data),
    onSuccess: () => {
      // Refresh the admin list if it's mounted somewhere.
      void queryClient.invalidateQueries({ queryKey: ["admin", "app-reviews"] });
      resetFields();
      close();
    },
  });

  const dismissMutation = useMutation({
    mutationFn: () => feedbackApi.dismiss(),
    onSettled: () => {
      resetFields();
      close();
    },
  });

  const isBusy = submitMutation.isPending || dismissMutation.isPending;

  const handleDismiss = () => {
    if (isBusy) return;
    dismissMutation.mutate();
  };

  const handleSubmit = () => {
    if (isBusy || rating < 1) return;
    submitMutation.mutate({
      rating,
      positive_feedback: positive.trim() || null,
      improvement_feedback: improvement.trim() || null,
      bug_report: bug.trim() || null,
      app_version: APP_VERSION,
    });
  };

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleDismiss();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, isBusy]);

  if (!isOpen) return null;

  const activeStars = hovered || rating;

  return (
    <div
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) handleDismiss();
      }}
      style={overlayStyle}
    >
      <div
        aria-describedby="feedback-modal-desc"
        aria-labelledby="feedback-modal-title"
        aria-modal="true"
        role="dialog"
        style={dialogStyle}
      >
        <div style={headerStyle}>
          <h2 id="feedback-modal-title" style={titleStyle}>
            How is Lingos AI helping you?
          </h2>
          <button
            aria-label="Maybe later"
            disabled={isBusy}
            onClick={handleDismiss}
            style={{ ...iconButtonStyle, opacity: isBusy ? 0.45 : 1 }}
            type="button"
          >
            <X size={17} strokeWidth={2.4} />
          </button>
        </div>

        <p id="feedback-modal-desc" style={descriptionStyle}>
          Your feedback helps us improve the learning experience.
        </p>

        {/* Rating */}
        <div style={{ marginTop: 18 }}>
          <div style={labelStyle}>Your rating</div>
          <div
            style={{ display: "flex", gap: 6, marginTop: 8 }}
            onMouseLeave={() => setHovered(0)}
          >
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                aria-label={`${n} star${n > 1 ? "s" : ""}`}
                key={n}
                onClick={() => setRating(n)}
                onMouseEnter={() => setHovered(n)}
                style={starButtonStyle}
                type="button"
              >
                <Star
                  size={30}
                  fill={n <= activeStars ? STAR_ON : "none"}
                  color={n <= activeStars ? STAR_ON_BORDER : STAR_OFF}
                />
              </button>
            ))}
          </div>
        </div>

        <Field
          label="What do you like most?"
          placeholder="The part of Lingos AI that's working for you…"
          value={positive}
          onChange={setPositive}
        />
        <Field
          label="What could be improved?"
          placeholder="Anything that would make this better…"
          value={improvement}
          onChange={setImprovement}
        />
        <Field
          label="Did you encounter any bugs or issues?"
          placeholder="Steps, screens, or errors you hit…"
          value={bug}
          onChange={setBug}
        />

        <div style={actionsStyle}>
          <button
            disabled={isBusy}
            onClick={handleDismiss}
            style={{
              ...buttonStyle,
              background: "white",
              borderColor: "oklch(84% 0.025 240)",
              color: "oklch(28% 0.08 245)",
              cursor: isBusy ? "not-allowed" : "pointer",
              opacity: isBusy ? 0.55 : 1,
            }}
            type="button"
          >
            Maybe Later
          </button>
          <button
            disabled={isBusy || rating < 1}
            onClick={handleSubmit}
            style={{
              ...buttonStyle,
              background: "oklch(52% 0.18 240)",
              borderColor: "oklch(52% 0.18 240)",
              color: "white",
              cursor: rating < 1 ? "not-allowed" : isBusy ? "wait" : "pointer",
              opacity: rating < 1 ? 0.5 : isBusy ? 0.72 : 1,
              boxShadow: "0 10px 24px oklch(52% 0.18 240 / 0.24)",
            }}
            type="button"
          >
            {submitMutation.isPending ? "Submitting…" : "Submit Feedback"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  placeholder,
  value,
  onChange,
}: {
  label: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div style={{ marginTop: 16 }}>
      <div style={labelStyle}>{label}</div>
      <textarea
        maxLength={4000}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={2}
        style={textareaStyle}
        value={value}
      />
    </div>
  );
}

const overlayStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  zIndex: 130,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 20,
  background: "rgba(12,22,42,0.46)",
  backdropFilter: "blur(10px)",
  WebkitBackdropFilter: "blur(10px)",
};

const dialogStyle: CSSProperties = {
  width: "min(100%, 480px)",
  maxHeight: "calc(100vh - 40px)",
  overflowY: "auto",
  borderRadius: 10,
  border: "1px solid rgba(255,255,255,0.92)",
  background: "rgba(255,255,255,0.97)",
  boxShadow: "0 30px 90px rgba(18,34,70,0.28), 0 2px 10px rgba(70,110,180,0.08)",
  color: "oklch(18% 0.06 240)",
  fontFamily: "'Plus Jakarta Sans', sans-serif",
  padding: 24,
};

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: 16,
};

const iconButtonStyle: CSSProperties = {
  width: 34,
  height: 34,
  flexShrink: 0,
  borderRadius: "50%",
  border: "1px solid oklch(86% 0.025 240)",
  background: "white",
  color: "oklch(42% 0.06 240)",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
};

const titleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(15% 0.09 245)",
  fontSize: 20,
  fontWeight: 800,
  lineHeight: 1.25,
};

const descriptionStyle: CSSProperties = {
  marginTop: 8,
  marginBottom: 0,
  color: "oklch(42% 0.06 240)",
  fontSize: 14,
  fontWeight: 600,
  lineHeight: 1.55,
};

const labelStyle: CSSProperties = {
  color: "oklch(30% 0.06 245)",
  fontSize: 13,
  fontWeight: 750,
};

const textareaStyle: CSSProperties = {
  width: "100%",
  marginTop: 6,
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid oklch(88% 0.02 245)",
  background: "white",
  color: "oklch(20% 0.05 245)",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 500,
  lineHeight: 1.5,
  resize: "vertical",
  boxSizing: "border-box",
};

const starButtonStyle: CSSProperties = {
  background: "none",
  border: "none",
  padding: 0,
  cursor: "pointer",
  lineHeight: 0,
};

const actionsStyle: CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  gap: 10,
  marginTop: 24,
};

const buttonStyle: CSSProperties = {
  minWidth: 124,
  minHeight: 42,
  borderRadius: 8,
  border: "1px solid transparent",
  padding: "0 16px",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 800,
};
