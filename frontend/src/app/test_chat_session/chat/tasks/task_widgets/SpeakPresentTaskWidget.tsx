"use client";

import { Mic2, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { SpeakPresentTask } from "../source";
import { ResultBanner, RuleCallout, StatusDot, TaskWidgetFrame } from "./TaskWidgetFrame";

export function SpeakPresentTaskWidget({
  task,
  previewState,
}: {
  task: SpeakPresentTask;
  previewState: SessionPreviewState;
}) {
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];
  const showRoomPrompt = task.visualPromptDescription.toLowerCase().includes("cozy room");
  const modelPresentation =
    task.modelPresentation ??
    "There is a coffee table in the room. A coffee mug is sitting on the table. A green plant is standing next to the sofa. A lovely picture hangs between the two windows.";

  return (
    <TaskWidgetFrame task={task} icon={<Mic2 size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Speaking focus">{task.grammarRule}</RuleCallout>

      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 800, color: "oklch(45% 0.07 240)", marginBottom: 6, textTransform: "uppercase" }}>
          Target speaking cues
        </div>
        <div className="tw-target-chip-row">
          {task.targetWords.map((word) => (
            <span className="tw-target-chip used" key={word}>
              {word}
            </span>
          ))}
        </div>
      </div>

      <div
        style={{
          width: "100%",
          padding: "20px 10px",
          background: "linear-gradient(135deg, #FDFDFD 0%, #F5F7FA 100%)",
          border: "1.5px solid oklch(90% 0.02 240)",
          borderRadius: 18,
          marginBottom: 16,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          boxShadow: "0 4px 14px rgba(80,110,180,0.04)"
        }}
      >
        <div style={{ fontSize: 12, fontWeight: 800, color: "#0070C4", textTransform: "uppercase", marginBottom: 12 }}>
          Speaking prompt
        </div>
        {showRoomPrompt ? (
          <svg
            viewBox="0 0 500 240"
            width="100%"
            height="180"
            style={{ maxWidth: 440 }}
          >
            <rect x="10" y="10" width="480" height="220" rx="14" fill="#EDF3F9" stroke="#DFE7EF" strokeWidth="2" />
            <path d="M 10 180 L 490 180 L 490 230 L 10 230 Z" fill="#E8DFD7" stroke="#D3C7BD" strokeWidth="1.5" />
            <rect x="50" y="30" width="50" height="80" rx="25" fill="#FFFFFF" stroke="#BACCDD" strokeWidth="3" />
            <line x1="50" y1="70" x2="100" y2="70" stroke="#BACCDD" strokeWidth="2" />
            <line x1="75" y1="30" x2="75" y2="110" stroke="#BACCDD" strokeWidth="2" />
            <rect x="400" y="30" width="50" height="80" rx="25" fill="#FFFFFF" stroke="#BACCDD" strokeWidth="3" />
            <line x1="400" y1="70" x2="450" y2="70" stroke="#BACCDD" strokeWidth="2" />
            <line x1="425" y1="30" x2="425" y2="110" stroke="#BACCDD" strokeWidth="2" />
            <rect x="210" y="40" width="80" height="50" rx="4" fill="#FFFFFF" stroke="#3A4D62" strokeWidth="3.5" />
            <circle cx="235" cy="65" r="8" fill="#FBD38D" />
            <path d="M 215 80 L 235 68 L 255 80 Z" fill="#48BB78" />
            <path d="M 240 80 L 260 72 L 285 80 Z" fill="#38B2AC" />
            <text x="250" y="105" fontSize="8" fontWeight="800" fill="#3A4D62" textAnchor="middle">
              [ between ]
            </text>
            <rect x="150" y="110" width="200" height="60" rx="10" fill="#3B82F6" stroke="#1D4ED8" strokeWidth="2.5" />
            <rect x="160" y="125" width="180" height="40" rx="6" fill="#60A5FA" />
            <rect x="175" y="115" width="40" height="30" rx="4" fill="#93C5FD" />
            <rect x="285" y="115" width="40" height="30" rx="4" fill="#93C5FD" />
            <rect x="80" y="120" width="30" height="35" rx="3" fill="#D57C59" stroke="#A75A3E" strokeWidth="2" />
            <path d="M 95 120 Q 80 100 70 105 Q 80 120 95 120 Z" fill="#2F855A" />
            <path d="M 95 120 Q 110 100 120 105 Q 110 120 95 120 Z" fill="#276749" />
            <path d="M 95 105 Q 95 85 85 88 Q 90 105 95 105 Z" fill="#38A169" />
            <text x="95" y="170" fontSize="8" fontWeight="800" fill="#276749" textAnchor="middle">
              [ next to ]
            </text>
            <ellipse cx="250" cy="185" rx="80" ry="18" fill="#EDF2F7" stroke="#A0AEC0" strokeWidth="2.5" />
            <line x1="200" y1="185" x2="195" y2="210" stroke="#718096" strokeWidth="4" strokeLinecap="round" />
            <line x1="300" y1="185" x2="305" y2="210" stroke="#718096" strokeWidth="4" strokeLinecap="round" />
            <line x1="250" y1="185" x2="250" y2="212" stroke="#718096" strokeWidth="4" strokeLinecap="round" />
            <rect x="240" y="171" width="12" height="12" rx="2" fill="#E53E3E" stroke="#9B2C2C" strokeWidth="1.5" />
            <path d="M 252 173 Q 256 177 252 181" stroke="#9B2C2C" strokeWidth="1.5" fill="none" />
            <text x="250" y="163" fontSize="8" fontWeight="800" fill="#E53E3E" textAnchor="middle">
              [ on ]
            </text>
          </svg>
        ) : (
          <div
            style={{
              width: "100%",
              maxWidth: 520,
              borderRadius: 16,
              background: "white",
              border: "1px solid oklch(90% 0.02 240)",
              padding: "16px 18px",
              color: "oklch(22% 0.08 245)",
              fontSize: 15,
              lineHeight: 1.6,
              fontWeight: 700,
              textAlign: "center",
            }}
          >
            {task.visualPromptDescription}
          </div>
        )}
      </div>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={answer?.isCorrect ? "Presentation clear and complete" : "Presentation needs one correction"}
        />
      )}

      {isDefault ? (
        <div className="tw-mic-stage" style={{ marginBottom: 0 }}>
          <div className="tw-mic-prompt">Ready to present</div>
          <div className="tw-mic-button-wrap">
            <button
              type="button"
              disabled
              aria-label="Preview recording button"
              title="Preview recording button"
              className="tw-mic-button"
              style={{ cursor: "default" }}
            >
              <Mic2 size={28} strokeWidth={2.5} />
            </button>
            <span className="tw-mic-ring" />
          </div>
          <div className="tw-mic-instruction">{task.instructions}</div>
          <div className="tw-mic-sub">Record up to {task.speakingDurationSeconds} seconds.</div>
        </div>
      ) : (
        <div className="tw-compare-grid">
          <div className="tw-compare-card">
            <div className="tw-compare-label">
              <StatusDot ok={Boolean(answer?.isCorrect)} />
              Your Spoken Presentation
            </div>
            <div className="tw-compare-body" style={{ fontStyle: "italic" }}>
              &ldquo;{answer?.transcript}&rdquo;
            </div>
            <div style={{ marginTop: 8, fontSize: 12, color: "var(--tw-ink-muted)", fontWeight: 700 }}>
              {answer?.durationSeconds}s recording
            </div>
          </div>
          <div className="tw-compare-card sample">
            <div className="tw-compare-label">
              <Sparkles size={12} />
              Model Presentation
            </div>
            <div className="tw-compare-body">
              {modelPresentation}
            </div>
          </div>
        </div>
      )}
    </TaskWidgetFrame>
  );
}
