"use client";

/**
 * Generic free-text widget — Phase 6 default.
 *
 * Used as the fallback when (a) task_content is the Phase 3 stub or (b)
 * the registry doesn't recognise the archetype's ui_widget. Renders the
 * task instructions and a single textarea. Phase 4 replaces real
 * archetypes with their bespoke widgets; this one stays around for
 * stub content during development.
 */

import { useState } from "react";

import { getStr, isStubContent, type SessionWidgetProps } from "./types";


export function GenericResponseWidget({
  taskContent,
  disabled,
  onSubmit,
}: SessionWidgetProps) {
  const [text, setText] = useState("");

  const topic = getStr(taskContent, "topic");
  const instructions = getStr(taskContent, "instructions");
  const brief = getStr(taskContent, "explanation_brief");
  const archetypeName = getStr(taskContent, "archetype_name");

  const stub = isStubContent(taskContent);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {topic && (
        <header>
          <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>{topic}</h3>
          {brief && (
            <p style={{ fontSize: 14, color: "oklch(40% 0.07 240)", marginTop: 4 }}>
              {brief}
            </p>
          )}
        </header>
      )}

      {instructions && (
        <p style={{ fontSize: 15, lineHeight: 1.5 }}>{instructions}</p>
      )}

      {stub && (
        <div
          style={{
            background: "oklch(96% 0.04 80)",
            border: "1px dashed oklch(70% 0.12 80)",
            color: "oklch(35% 0.1 80)",
            padding: 12,
            borderRadius: 8,
            fontSize: 13,
          }}
        >
          <strong>Stub task content.</strong> The Task Generator agent
          (Phase 4) will replace this with real archetype-specific content
          for <code>{archetypeName || "this activity"}</code>.
        </div>
      )}

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        rows={6}
        placeholder="Write your response here…"
        style={{
          width: "100%",
          borderRadius: 8,
          border: "1px solid oklch(85% 0.04 245)",
          padding: 12,
          fontSize: 14,
          resize: "vertical",
          fontFamily: "inherit",
        }}
      />

      <button
        type="button"
        onClick={() => onSubmit({ text: text.trim() })}
        disabled={disabled || text.trim().length === 0}
        style={{
          alignSelf: "flex-start",
          background: "oklch(52% 0.18 240)",
          color: "white",
          fontWeight: 600,
          padding: "10px 18px",
          borderRadius: 8,
          border: "none",
          cursor: disabled ? "default" : "pointer",
          opacity: disabled || text.trim().length === 0 ? 0.6 : 1,
        }}
      >
        Submit
      </button>
    </div>
  );
}
