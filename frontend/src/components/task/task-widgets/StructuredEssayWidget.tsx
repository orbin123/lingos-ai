"use client";

import { useRef, useState } from "react";
import { TaskHeader, I } from "./shared";
import { countWords } from "./types";
import type { EssaySection, StructuredEssayPayload, WidgetProps } from "./types";

type Props = WidgetProps<StructuredEssayPayload>;

interface SectionAnswer {
  section_id: string;
  user_answer: string;
  word_count: number;
}

interface EssayAnswers {
  sections?: SectionAnswer[];
  total_word_count?: number;
  time_spent_seconds?: number;
}

function sectionsFromAnswers(answers: Record<string, unknown>): Record<string, string> {
  const rows = (answers as EssayAnswers).sections ?? [];
  const out: Record<string, string> = {};
  for (const row of rows) {
    if (row?.section_id) out[row.section_id] = row.user_answer ?? "";
  }
  return out;
}

function sectionTitle(s: EssaySection): string {
  const raw = s.section_name || "";
  return raw
    .toString()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ") || "Section";
}

export function StructuredEssayWidget({ payload, answers, setAnswers, state, onSubmit }: Props) {
  const submitted = state === "after";
  const sections = payload.sections ?? [];
  const startedAtRef = useRef(Date.now());
  const initialMap = sectionsFromAnswers(answers);
  const [texts, setTexts] = useState<Record<string, string>>(initialMap);
  const [activeIdx, setActiveIdx] = useState(0);

  const setText = (sectionId: string, next: string) => {
    if (submitted) return;
    const updated = { ...texts, [sectionId]: next };
    setTexts(updated);
    const rows: SectionAnswer[] = sections.map((s) => ({
      section_id: s.section_id,
      user_answer: updated[s.section_id] ?? "",
      word_count: countWords(updated[s.section_id] ?? ""),
    }));
    setAnswers({
      sections: rows,
      total_word_count: rows.reduce((a, r) => a + r.word_count, 0),
      time_spent_seconds: Math.round((Date.now() - startedAtRef.current) / 1000),
    });
  };

  const totalWords = sections.reduce(
    (acc, s) => acc + countWords(texts[s.section_id] ?? ""),
    0,
  );
  const targetTotal = payload.total_target_words || 0;
  const allMinMet = sections.every(
    (s) => countWords(texts[s.section_id] ?? "") >= s.minimum_word_count,
  );
  const canSubmit = !submitted && (allMinMet || (targetTotal > 0 && totalWords >= targetTotal));

  return (
    <div className="tw-root">
      <TaskHeader
        topic="Structured Essay"
        intro={{
          title: payload.task_intro || "Build your essay section by section",
          body: payload.instructions || "Work through each section in order.",
        }}
        sub_skill={payload.sub_skill || "Structured writing"}
        activity={payload.activity || "Structured Essay"}
        time={payload.estimated_time_minutes ?? 0}
      />

      {payload.overall_topic && (
        <div
          className="tw-card"
          style={{
            background: "linear-gradient(135deg, oklch(96% 0.04 290), white)",
            borderColor: "oklch(82% 0.1 290)",
          }}
        >
          <div className="tw-rule-label" style={{ color: "oklch(40% 0.16 290)" }}>
            Topic
          </div>
          <div
            style={{
              fontSize: 17,
              fontWeight: 800,
              color: "var(--tw-navy)",
              lineHeight: 1.4,
              marginTop: 4,
            }}
          >
            {payload.overall_topic}
          </div>
          {payload.structure_pattern && (
            <div style={{ fontSize: 12, color: "var(--tw-ink-muted)", marginTop: 6, fontStyle: "italic" }}>
              Structure: {payload.structure_pattern}
            </div>
          )}
        </div>
      )}

      <div className="tw-progress-strip">
        <div className="tw-progress-row">
          <div>
            <div className="tw-progress-step-label">
              {submitted
                ? "All sections complete"
                : `Section ${Math.min(activeIdx + 1, sections.length)} of ${sections.length}`}
            </div>
            <div className="tw-progress-section-title">
              {submitted
                ? "Ready to submit"
                : sectionTitle(sections[activeIdx] ?? sections[0])}
            </div>
          </div>
          <div className="tw-progress-total">
            <span>Total written</span>{" "}
            <strong style={{ color: "var(--tw-navy)", fontWeight: 800, fontSize: 14 }}>
              {totalWords}
            </strong>{" "}
            {targetTotal > 0 && <>/ {targetTotal}</>} words
          </div>
        </div>
        <div className="tw-dot-track">
          {sections.map((s, i) => {
            let cls = "tw-dot-step";
            const wc = countWords(texts[s.section_id] ?? "");
            if (submitted || wc >= s.minimum_word_count) cls += " done";
            else if (i === activeIdx) cls += " active";
            return <span key={s.section_id} className={cls} />;
          })}
        </div>
      </div>

      <div className="tw-section-tabs">
        {sections.map((s, i) => {
          const wc = countWords(texts[s.section_id] ?? "");
          const done = wc >= s.minimum_word_count;
          let cls = "tw-section-tab";
          if (submitted) cls += " done";
          else if (i === activeIdx) cls += " active";
          else if (done) cls += " done";
          return (
            <button
              key={s.section_id}
              className={cls}
              onClick={() => setActiveIdx(i)}
              disabled={submitted}
            >
              <span className="tw-step-num">{i + 1}</span>
              <span>{sectionTitle(s)}</span>
              {done && <span style={{ marginLeft: 4 }}>{I.check}</span>}
            </button>
          );
        })}
      </div>

      {!submitted ? (
        sections[activeIdx] && (
          <SectionEditor
            section={sections[activeIdx]}
            value={texts[sections[activeIdx].section_id] ?? ""}
            onChange={(v) => setText(sections[activeIdx].section_id, v)}
            activeIdx={activeIdx}
            totalSections={sections.length}
            onPrev={() => setActiveIdx((i) => Math.max(0, i - 1))}
            onNext={() => setActiveIdx((i) => Math.min(sections.length - 1, i + 1))}
          />
        )
      ) : (
        <>
          <div className="tw-result-banner good">
            <div className="tw-result-icon" style={{ color: "var(--tw-green)" }}>
              {I.check}
            </div>
            <div className="tw-result-text">
              <div className="tw-result-headline">
                {sections.length} section{sections.length === 1 ? "" : "s"} complete · {totalWords} words
              </div>
              <div className="tw-result-sub">Compare each section with the sample below.</div>
            </div>
            <div>
              <div className="tw-result-score">
                {totalWords}
                {targetTotal > 0 && (
                  <span style={{ fontSize: 14, color: "var(--tw-ink-muted)" }}>
                    {" "}/ {targetTotal}
                  </span>
                )}
              </div>
              <div className="tw-result-score-sub">Words</div>
            </div>
          </div>
          {sections.map((s) => {
            const userText = texts[s.section_id] ?? "";
            const wc = countWords(userText);
            return (
              <div className="tw-card" key={s.section_id}>
                <div className="tw-q-number-row" style={{ marginBottom: 6 }}>
                  <div
                    className="tw-q-number-badge"
                    style={{
                      background: "var(--tw-green-soft)",
                      color: "oklch(28% 0.14 155)",
                    }}
                  >
                    {I.check}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13.5, fontWeight: 800, color: "var(--tw-navy)" }}>
                      {sectionTitle(s)}
                    </div>
                    <div
                      style={{
                        fontSize: 11.5,
                        color: "var(--tw-ink-muted)",
                        fontWeight: 700,
                      }}
                    >
                      {wc} words · target {s.minimum_word_count}+
                    </div>
                  </div>
                </div>
                <div className="tw-compare-grid">
                  <div className="tw-compare-card">
                    <div className="tw-compare-label">{I.doc} Your section</div>
                    <div className="tw-compare-body">
                      {userText || <em style={{ color: "var(--tw-ink-muted)" }}>No answer</em>}
                    </div>
                  </div>
                  <div className="tw-compare-card sample">
                    <div className="tw-compare-label">{I.spark} Sample</div>
                    <div className="tw-compare-body">{s.sample_text}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!canSubmit}
          onClick={() => onSubmit()}
        >
          {I.send} Submit essay
        </button>
      )}
    </div>
  );
}

function SectionEditor({
  section,
  value,
  onChange,
  activeIdx,
  totalSections,
  onPrev,
  onNext,
}: {
  section: EssaySection;
  value: string;
  onChange: (next: string) => void;
  activeIdx: number;
  totalSections: number;
  onPrev: () => void;
  onNext: () => void;
}) {
  const wc = countWords(value);
  const met = wc >= section.minimum_word_count;
  return (
    <div className="tw-card">
      <div className="tw-q-number-row">
        <div className="tw-q-number-badge">{activeIdx + 1}</div>
        <div className="tw-q-stem">
          <strong>{sectionTitle(section)}</strong>
          <br />
          <span style={{ fontSize: 13.5, fontWeight: 500, color: "var(--tw-ink-muted)" }}>
            {section.section_prompt}
          </span>
        </div>
      </div>
      <textarea
        className="tw-write-area"
        style={{ minHeight: 160 }}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Write this section…"
      />
      <div className="tw-write-helper">
        <span>Minimum {section.minimum_word_count} words for this section</span>
        <span className={`tw-count ${met ? "ok" : "short"}`}>
          {wc} / {section.minimum_word_count} words {met ? "· ✓ met" : `· ${section.minimum_word_count - wc} to go`}
        </span>
      </div>
      <div className="tw-section-nav">
        <button className="tw-nav-btn prev" onClick={onPrev} disabled={activeIdx === 0}>
          {I.arrowL} Previous
        </button>
        <button
          className="tw-nav-btn next"
          onClick={onNext}
          disabled={activeIdx >= totalSections - 1}
        >
          Next section {I.arrowR}
        </button>
      </div>
    </div>
  );
}
