"use client";

import { FileText, Sparkles } from "lucide-react";
import type { SessionPreviewState } from "../../teaching/source";
import type { LiveTaskController, WriteEmailTask } from "../source";
import {
  LiveTextItems,
  ResultBanner,
  RuleCallout,
  StatusDot,
  TaskWidgetFrame,
} from "./TaskWidgetFrame";

export function WriteEmailTaskWidget({
  task,
  previewState,
  live,
}: {
  task: WriteEmailTask;
  previewState: SessionPreviewState;
  live?: LiveTaskController;
}) {
  if (live) {
    return (
      <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
        <RuleCallout label="Email focus">{task.grammarRule}</RuleCallout>
        <LiveTextItems
          items={[
            {
              itemId: task.itemId ?? "item_1",
              prompt: task.prompt,
              sampleAnswer: task.sampleAnswer,
              minHeight: 140,
              placeholder: "Write your email here. You can include To: and Subject: lines.",
              hints: task.answerHints,
            },
          ]}
          live={live}
          numbered={false}
          yourLabel="Your email"
          sampleLabel="Sample answer"
        />
      </TaskWidgetFrame>
    );
  }
  const isDefault = previewState === "default";
  const answers = isDefault ? [] : task.answers[previewState];
  const correctCount = isDefault ? 0 : answers.filter((answer) => answer.isCorrect).length;
  const answer = answers[0];

  // Helper to count words
  const getWordCount = (text?: string) => {
    if (!text) return 0;
    // Strip To/Subject line prefixes from word count to count only email body
    const bodyOnly = text.replace(/^To:.*\n/, "").replace(/^Subject:.*\n/, "");
    return bodyOnly.trim().split(/\s+/).filter(Boolean).length;
  };

  const currentText = isDefault ? "" : answer?.text || "";
  const wordCount = getWordCount(currentText);

  // Parse To, Subject, and Body for rendering
  const parseEmail = (text: string) => {
    const lines = text.split("\n");
    let to = "friend@example.com";
    let subject = "Meet my family";
    const bodyLines: string[] = [];

    lines.forEach((line) => {
      if (line.startsWith("To:")) {
        to = line.replace("To:", "").trim();
      } else if (line.startsWith("Subject:")) {
        subject = line.replace("Subject:", "").trim();
      } else {
        bodyLines.push(line);
      }
    });

    return { to, subject, body: bodyLines.join("\n").trim() };
  };

  const parsedSample = parseEmail(task.sampleAnswer);
  const parsedCurrent = isDefault ? parsedSample : parseEmail(currentText);

  return (
    <TaskWidgetFrame task={task} icon={<FileText size={18} strokeWidth={2.5} />}>
      <RuleCallout label="Email focus">{task.grammarRule}</RuleCallout>

      {!isDefault && (
        <ResultBanner
          total={1}
          correct={correctCount}
          label={correctCount > 0 ? "Email draft accepted" : "Email has grammatical errors"}
        />
      )}

      {/* Email Composer Box */}
      <div 
        style={{
          border: "1.5px solid oklch(90% 0.02 240)",
          borderRadius: 20,
          background: "oklch(99% 0.005 240)",
          padding: 18,
          marginBottom: 16,
          boxShadow: "0 4px 18px rgba(80,110,180,0.04)"
        }}
      >
        <div 
          style={{ 
            fontSize: 11, 
            fontWeight: 800, 
            color: "#0070C4", 
            textTransform: "uppercase", 
            letterSpacing: "0.05em",
            borderBottom: "1.5px solid oklch(92% 0.02 240)",
            paddingBottom: 8,
            marginBottom: 12,
            display: "flex",
            alignItems: "center",
            gap: 6
          }}
        >
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#0070C4" }} />
              <span>New Message</span>
        </div>

        {/* Email Header */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", fontSize: 13.5, borderBottom: "1px solid oklch(94% 0.01 240)", paddingBottom: 6 }}>
            <span style={{ width: 70, fontWeight: 700, color: "oklch(45% 0.07 240)" }}>To:</span>
            <span style={{ color: "oklch(20% 0.09 245)", fontWeight: 500 }}>{parsedCurrent.to}</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", fontSize: 13.5, borderBottom: "1px solid oklch(94% 0.01 240)", paddingBottom: 6 }}>
            <span style={{ width: 70, fontWeight: 700, color: "oklch(45% 0.07 240)" }}>Subject:</span>
            <span style={{ color: "oklch(20% 0.09 245)", fontWeight: 500 }}>{parsedCurrent.subject}</span>
          </div>
        </div>

        {isDefault ? (
          <>
            <div
              style={{
                color: "oklch(55% 0.07 240)",
                minHeight: 120,
                fontSize: 14,
                lineHeight: 1.6,
                padding: "8px 0"
              }}
            >
              {task.prompt}
            </div>
            <div 
              style={{ 
                display: "flex", 
                justifyContent: "space-between", 
                marginTop: 12, 
                fontSize: 12, 
                color: "oklch(45% 0.07 240)",
                borderTop: "1px dashed oklch(90% 0.02 240)",
                paddingTop: 10
              }}
            >
                <span>Minimum {task.minimumWords} words required.</span>
              <span style={{ fontWeight: 700, color: "oklch(40% 0.16 25)" }}>
                0 words
              </span>
            </div>
          </>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ background: "white", border: "1px solid oklch(92% 0.02 240)", borderRadius: 12, padding: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, fontWeight: 800, color: "oklch(45% 0.07 240)", marginBottom: 8 }}>
                <StatusDot ok={Boolean(answer?.isCorrect)} />
                <span>Your Email Body</span>
              </div>
              <div 
                style={{ 
                  fontSize: 14, 
                  lineHeight: 1.6, 
                  color: "oklch(20% 0.09 245)",
                  whiteSpace: "pre-wrap"
                }}
              >
                {parsedCurrent.body}
              </div>
              <div 
                style={{ 
                  marginTop: 10, 
                  fontSize: 11.5, 
                  color: "oklch(45% 0.07 240)", 
                  fontWeight: 700,
                  borderTop: "1px dashed oklch(94% 0.01 240)",
                  paddingTop: 8
                }}
              >
                {wordCount} words - {wordCount >= task.minimumWords ? "meets requirements" : "short of limit"}
              </div>
            </div>

            <div style={{ background: "oklch(98% 0.02 155)", border: "1.5px dashed oklch(85% 0.05 155)", borderRadius: 12, padding: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, fontWeight: 800, color: "oklch(35% 0.18 155)", marginBottom: 8 }}>
                <Sparkles size={13} style={{ color: "oklch(40% 0.18 155)" }} />
                <span>Sample answer</span>
              </div>
              <div 
                style={{ 
                  fontSize: 14, 
                  lineHeight: 1.6, 
                  color: "oklch(20% 0.09 245)",
                  whiteSpace: "pre-wrap"
                }}
              >
                {parsedSample.body}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="tw-hints-block">
        <div className="tw-hints-label">Hints Checklist</div>
        <div className="tw-hints-list">
          {task.answerHints.map((hint) => (
            <div className="tw-hint-item" key={hint}>
              <span className="tw-hint-dot" />
              {hint}
            </div>
          ))}
        </div>
      </div>
    </TaskWidgetFrame>
  );
}
