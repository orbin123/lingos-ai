"use client";

import type { SpeakWithTenseTaskContent } from "@/lib/tasks-api";
import { SpeakAndRecord } from "./SpeakAndRecord";
import type { SpeakAndRecordResult } from "./SpeakAndRecord";

interface Props {
  content: SpeakWithTenseTaskContent;
  onSubmit: (answers: Record<string, unknown>) => void;
  isPending: boolean;
}

/**
 * Speak-with-tense task: shows the speaking prompt + target tense,
 * delegates audio recording and transcription to SpeakAndRecord,
 * then submits the transcript via the standard onSubmit callback.
 */
export function GeneratedSpeakWithTense({ content, onSubmit, isPending }: Props) {
  function handleRecordingResult(result: SpeakAndRecordResult) {
    onSubmit({
      transcript: result.transcript,
      duration_seconds: result.duration_seconds,
      audio_url: result.audio_url,
    });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Task intro */}
      <p
        style={{
          fontSize: 14,
          color: "oklch(40% 0.07 240)",
          lineHeight: 1.6,
          margin: 0,
        }}
      >
        {content.task_intro}
      </p>

      {/* Instructions */}
      <p
        style={{
          fontSize: 13,
          color: "oklch(45% 0.07 240)",
          margin: 0,
          fontStyle: "italic",
        }}
      >
        {content.instructions}
      </p>

      {/* Target tense + duration badges */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        <span
          style={{
            fontSize: 12,
            fontWeight: 700,
            background: "oklch(92% 0.06 245)",
            color: "oklch(38% 0.14 245)",
            padding: "4px 12px",
            borderRadius: 20,
          }}
        >
          Tense: {content.target_tense.replace(/_/g, " ")}
        </span>
        <span
          style={{
            fontSize: 12,
            fontWeight: 600,
            background: "oklch(95% 0.03 240)",
            color: "oklch(45% 0.07 240)",
            padding: "4px 12px",
            borderRadius: 20,
          }}
        >
          Min. {content.minimum_sentences} sentences
        </span>
        <span
          style={{
            fontSize: 12,
            fontWeight: 600,
            background: "oklch(95% 0.03 240)",
            color: "oklch(45% 0.07 240)",
            padding: "4px 12px",
            borderRadius: 20,
          }}
        >
          Up to {content.minimum_duration_seconds}s
        </span>
      </div>

      {/* Speaking prompt */}
      <div
        style={{
          background: "rgba(255,255,255,0.85)",
          backdropFilter: "blur(16px)",
          WebkitBackdropFilter: "blur(16px)",
          borderRadius: 14,
          border: "1px solid rgba(80,120,200,0.12)",
          padding: "18px 20px",
        }}
      >
        <p
          style={{
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            color: "oklch(50% 0.14 245)",
            margin: "0 0 8px",
          }}
        >
          Speaking prompt
        </p>
        <p
          style={{
            fontSize: 15,
            fontWeight: 600,
            color: "oklch(22% 0.08 240)",
            lineHeight: 1.55,
            margin: 0,
          }}
        >
          {content.speaking_prompt}
        </p>
      </div>

      {/* Grading criteria */}
      {content.grading_criteria.length > 0 && (
        <div>
          <p
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.06em",
              color: "oklch(50% 0.07 240)",
              margin: "0 0 6px",
            }}
          >
            Grading criteria
          </p>
          <ul
            style={{
              margin: 0,
              paddingLeft: 20,
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}
          >
            {content.grading_criteria.map((c, i) => (
              <li
                key={i}
                style={{ fontSize: 13, color: "oklch(38% 0.07 240)", lineHeight: 1.5 }}
              >
                {c}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sample response (collapsible hint) */}
      <details
        style={{
          background: "oklch(97% 0.015 155)",
          border: "1px solid oklch(88% 0.05 155)",
          borderRadius: 10,
          padding: "10px 14px",
        }}
      >
        <summary
          style={{
            fontSize: 12,
            fontWeight: 700,
            color: "oklch(42% 0.12 155)",
            cursor: "pointer",
            userSelect: "none",
          }}
        >
          Show sample response (hint)
        </summary>
        <p
          style={{
            fontSize: 13,
            color: "oklch(30% 0.07 240)",
            lineHeight: 1.65,
            margin: "10px 0 0",
          }}
        >
          {content.sample_response}
        </p>
      </details>

      {/* Recording component */}
      <SpeakAndRecord
        maxDurationSeconds={content.minimum_duration_seconds}
        minimumSentences={content.minimum_sentences}
        onSubmit={handleRecordingResult}
        isPending={isPending}
      />
    </div>
  );
}
