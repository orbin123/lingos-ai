"use client";

import { useState } from "react";
import type { ErrorSpottingTaskContent, GrammarRule } from "@/lib/tasks-api";

const ERROR_TYPE_LABELS: Record<string, string> = {
  past_simple: "Past Simple",
  past_continuous: "Past Continuous",
  present_simple: "Present Simple",
  present_perfect: "Present Perfect",
  past_perfect: "Past Perfect",
  future_simple: "Future Simple",
  subject_verb_agreement: "Subject-Verb Agreement",
  preposition: "Preposition",
  article: "Article",
  conditional: "Conditional",
  passive_voice: "Passive Voice",
  active_voice: "Active Voice",
  modal_verb: "Modal Verb",
  relative_clause: "Relative Clause",
  conjunction: "Conjunction",
};

const GRAMMAR_RULE_ORDER = Object.keys(ERROR_TYPE_LABELS) as GrammarRule[];
const MAX_ERROR_TYPE_OPTIONS = 4;

function uniqueRules(rules: Array<GrammarRule | null>): GrammarRule[] {
  return rules.filter(
    (rule, index): rule is GrammarRule =>
      rule !== null && rules.indexOf(rule) === index,
  );
}

function answerOptionsForSentence(
  correctErrorType: GrammarRule | null,
  taskErrorTypes: GrammarRule[],
): Array<{ value: GrammarRule | "correct"; label: string }> {
  const candidates = uniqueRules([
    correctErrorType,
    ...taskErrorTypes,
    ...GRAMMAR_RULE_ORDER,
  ]).slice(0, MAX_ERROR_TYPE_OPTIONS);

  return [
    { value: "correct", label: "Correct" },
    ...candidates.map((value) => ({
      value,
      label: ERROR_TYPE_LABELS[value],
    })),
  ];
}

interface Props {
  content: ErrorSpottingTaskContent;
  onSubmit: (answers: Record<string, string>) => void;
  isPending: boolean;
}

/**
 * Error Spotting task: show sentences and one answer pill per evaluator label.
 */
export function GeneratedErrorSpotting({
  content,
  onSubmit,
  isPending,
}: Props) {
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const allAnswered = content.sentences.every((s) => Boolean(answers[s.sentence_id]));
  const taskErrorTypes = uniqueRules(content.sentences.map((s) => s.error_type));

  const setAnswer = (id: string, value: GrammarRule | "correct") => {
    setAnswers((prev) => ({
      ...prev,
      [id]: value,
    }));
  };

  const handleSubmit = () => {
    if (!allAnswered) return;
    // Payload shape: { sentence_id: "correct" | "grammar_rule_literal" }
    const flat: Record<string, string> = {};
    content.sentences.forEach((s) => {
      flat[s.sentence_id] = answers[s.sentence_id];
    });
    onSubmit(flat);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
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
      <p
        style={{
          fontSize: 13,
          color: "oklch(45% 0.07 240)",
          margin: 0,
          fontStyle: "italic",
        }}
      >
        Choose Correct if the sentence is okay. If it has a mistake, choose
        the grammar label.
      </p>

      {/* Sentences */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {content.sentences.map((sent, i) => {
          const selected = answers[sent.sentence_id];
          const answerOptions = answerOptionsForSentence(
            sent.error_type,
            taskErrorTypes,
          );
          return (
            <div
              key={sent.sentence_id}
              style={{
                background: "rgba(255,255,255,0.85)",
                backdropFilter: "blur(16px)",
                WebkitBackdropFilter: "blur(16px)",
                borderRadius: 10,
                border: selected
                  ? selected === "correct"
                    ? "1.5px solid oklch(55% 0.18 155)"
                    : "1.5px solid oklch(58% 0.2 15)"
                  : "1px solid rgba(80,120,200,0.12)",
                padding: "18px 20px",
                transition: "all 0.2s ease",
              }}
            >
              {/* Sentence */}
              <p
                style={{
                  fontSize: 14,
                  fontWeight: 500,
                  color: "oklch(20% 0.07 240)",
                  margin: "0 0 14px",
                  lineHeight: 1.6,
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: 24,
                    height: 24,
                    borderRadius: "50%",
                    background: "oklch(52% 0.18 240)",
                    color: "white",
                    fontSize: 12,
                    fontWeight: 700,
                    marginRight: 10,
                    flexShrink: 0,
                  }}
                >
                  {i + 1}
                </span>
                {sent.sentence}
              </p>

              {/* Answer pills */}
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 8,
                }}
              >
                {answerOptions.map((option) => {
                  const isSelected = selected === option.value;
                  const isCorrectPill = option.value === "correct";
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setAnswer(sent.sentence_id, option.value)}
                      aria-pressed={isSelected}
                      style={{
                        padding: "8px 11px",
                        borderRadius: 999,
                        border: isSelected
                          ? isCorrectPill
                            ? "1.5px solid oklch(55% 0.18 155)"
                            : "1.5px solid oklch(58% 0.2 15)"
                          : "1px solid rgba(80,120,200,0.15)",
                        background: isSelected
                          ? isCorrectPill
                            ? "oklch(93% 0.04 155)"
                            : "oklch(95% 0.04 15)"
                          : "rgba(255,255,255,0.9)",
                        color: isSelected
                          ? isCorrectPill
                            ? "oklch(30% 0.12 155)"
                            : "oklch(38% 0.12 15)"
                          : "oklch(25% 0.07 240)",
                        fontSize: 12,
                        fontWeight: isSelected ? 700 : 600,
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {content.sentences.some((s) => !answers[s.sentence_id]) && (
        <p
          style={{
            fontSize: 12,
            color: "oklch(45% 0.07 240)",
            margin: 0,
          }}
        >
          Choose one pill for every sentence to submit.
        </p>
      )}

      {/* Submit */}
      <button
        type="button"
        disabled={!allAnswered || isPending}
        onClick={handleSubmit}
        style={{
          width: "100%",
          padding: "14px 0",
          borderRadius: 12,
          border: "none",
          background: allAnswered
            ? "oklch(52% 0.18 240)"
            : "oklch(85% 0.03 240)",
          color: allAnswered ? "white" : "oklch(55% 0.05 240)",
          fontSize: 15,
          fontWeight: 700,
          cursor: allAnswered ? "pointer" : "not-allowed",
          transition: "all 0.2s ease",
          opacity: isPending ? 0.6 : 1,
        }}
      >
        {isPending ? "Submitting…" : "Submit answers"}
      </button>
    </div>
  );
}
