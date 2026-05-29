"use client";

import { Check, Sparkles, X } from "lucide-react";
import type { CSSProperties, ReactNode } from "react";
import type { SessionTask } from "../source";

export function TaskWidgetFrame({
  task,
  icon,
  children,
}: {
  task: SessionTask;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <section
      className="tw-root"
      style={{
        background: "rgba(255,255,255,0.96)",
        border: "1.5px solid rgba(255,255,255,0.9)",
        borderRadius: 22,
        padding: 22,
        boxShadow: "0 8px 32px rgba(80,110,180,0.14)",
        marginBottom: 16,
        animation: "testChatFadeIn 0.35s ease both",
      }}
    >
      <div className="tw-task-header">
        <div className="tw-task-topic">{task.topic}</div>
        <div style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
          <div
            style={{
              width: 38,
              height: 38,
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "#0070C4",
              color: "white",
              flexShrink: 0,
              boxShadow: "0 5px 14px rgba(0,112,196,0.28)",
            }}
          >
            {icon}
          </div>
          <div style={{ minWidth: 0 }}>
            <div className="tw-task-title">{task.taskIntro}</div>
            <div className="tw-task-intro">{task.instructions}</div>
          </div>
        </div>
        <div className="tw-task-pill-row">
          <span className="tw-task-pill">
            <span className="tw-dot" />
            {task.subSkill}
          </span>
          <span className="tw-task-pill activity">
            <span className="tw-dot" />
            {task.activity}
          </span>
          <span className="tw-task-pill time">
            <span className="tw-dot" />
            {task.estimatedMinutes} min
          </span>
        </div>
      </div>
      {children}
    </section>
  );
}

export function RuleCallout({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="tw-rule-callout">
      <div className="tw-rule-icon">
        <Sparkles size={16} />
      </div>
      <div className="tw-rule-body">
        <div className="tw-rule-label">{label}</div>
        <div className="tw-rule-text">{children}</div>
      </div>
    </div>
  );
}

export function ResultBanner({
  total,
  correct,
  label,
}: {
  total: number;
  correct: number;
  label: string;
}) {
  const score = total > 0 ? Math.round((correct / total) * 100) : 0;
  const tone = score === 100 ? "good" : score >= 70 ? "mid" : "bad";

  return (
    <div className={`tw-result-banner ${tone}`}>
      <div className="tw-result-icon">
        <Sparkles size={18} />
      </div>
      <div className="tw-result-text">
        <div className="tw-result-headline">{label}</div>
        <div className="tw-result-sub">Completed and submitted preview state.</div>
      </div>
      <div>
        <div className="tw-result-score">
          {score}
          <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>%</span>
        </div>
        <div className="tw-result-score-sub">Score</div>
      </div>
    </div>
  );
}

export function FeedbackRow({
  ok,
  title,
  body,
}: {
  ok: boolean;
  title: string;
  body: string;
}) {
  return (
    <div className={`tw-fb-row ${ok ? "good" : "bad"}`}>
      <div className={`tw-fb-marker ${ok ? "ok" : "no"}`}>
        {ok ? <Check size={13} strokeWidth={3} /> : <X size={13} strokeWidth={3} />}
      </div>
      <div>
        <div className="tw-fb-q">{title}</div>
        <div className="tw-fb-explain">{body}</div>
      </div>
    </div>
  );
}

export function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      aria-label={ok ? "Correct" : "Needs correction"}
      style={{
        width: 20,
        height: 20,
        borderRadius: "50%",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        background: ok ? "var(--tw-green)" : "var(--tw-red)",
        color: "white",
        flexShrink: 0,
      }}
    >
      {ok ? <Check size={12} strokeWidth={3} /> : <X size={12} strokeWidth={3} />}
    </span>
  );
}

export function normalizeAnswer(value: string | undefined): string {
  return (value ?? "").trim().toLowerCase();
}

export const roundIconButton: CSSProperties = {
  width: 42,
  height: 42,
  borderRadius: "50%",
  border: "none",
  background: "#0070C4",
  color: "white",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
  flexShrink: 0,
  boxShadow: "0 6px 16px rgba(0,112,196,0.28)",
};
