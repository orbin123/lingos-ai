"use client";

import { useState } from "react";
import { I } from "./shared";
import type {
  ErrorSpottingError,
  ErrorSpottingPayload,
  ErrorSpottingToken,
  WidgetProps,
} from "./types";

type Props = WidgetProps<ErrorSpottingPayload>;

interface ErrorSpottingAnswers {
  selected_token_ids?: string[];
  time_spent_seconds?: number;
}

function selectedIdsFromAnswers(answers: Record<string, unknown>): string[] {
  const selected = (answers as ErrorSpottingAnswers).selected_token_ids;
  return Array.isArray(selected)
    ? selected.map(String).filter(Boolean)
    : [];
}

function errorByToken(payload: ErrorSpottingPayload): Map<string, ErrorSpottingError> {
  const out = new Map<string, ErrorSpottingError>();
  for (const sentence of payload.passage_sentences ?? []) {
    if (sentence.error?.token_id) {
      out.set(sentence.error.token_id, sentence.error);
    }
  }
  return out;
}

function answerSummary(payload: ErrorSpottingPayload, selectedIds: string[]) {
  const errors = errorByToken(payload);
  const selectedSet = new Set(selectedIds);
  const found = selectedIds.filter((id) => errors.has(id));
  const missed = [...errors.entries()]
    .filter(([id]) => !selectedSet.has(id))
    .map(([, error]) => error);
  const wrong = selectedIds.filter((id) => !errors.has(id));
  return { errors, found, missed, wrong };
}

export function ErrorSpottingWidget({
  payload,
  answers,
  setAnswers,
  state,
  onSubmit,
}: Props) {
  const [startedAt] = useState(() => Date.now());
  const submitted = state === "after";
  const selectedIds = selectedIdsFromAnswers(answers);
  const selectedSet = new Set(selectedIds);
  const totalErrors = payload.total_errors || payload.passage_sentences?.length || 0;
  const summary = answerSummary(payload, selectedIds);
  const canSubmit = selectedIds.length > 0 && selectedIds.length <= totalErrors;

  const toggleToken = (tokenId: string) => {
    if (submitted) return;
    let next = selectedIds;
    if (selectedSet.has(tokenId)) {
      next = selectedIds.filter((id) => id !== tokenId);
    } else if (selectedIds.length < totalErrors) {
      next = [...selectedIds, tokenId];
    }
    setAnswers({
      selected_token_ids: next,
      time_spent_seconds: Math.round((Date.now() - startedAt) / 1000),
    });
  };

  const tokenClass = (token: ErrorSpottingToken) => {
    const selected = selectedSet.has(token.token_id);
    const isError = summary.errors.has(token.token_id);
    if (!submitted && selected) return "tw-error-token selected";
    if (!submitted) return "tw-error-token";
    if (selected && isError) return "tw-error-token found";
    if (!selected && isError) return "tw-error-token missed";
    if (selected && !isError) return "tw-error-token wrong";
    return "tw-error-token";
  };

  const recall = totalErrors ? Math.round((summary.found.length / totalErrors) * 100) : 0;
  const bannerTone =
    summary.found.length === totalErrors && summary.wrong.length === 0
      ? "good"
      : summary.found.length > 0
        ? "mid"
        : "bad";

  return (
    <div className="tw-root">
      <div className="tw-error-head">
        <div>
          <div className="tw-error-kicker">READ</div>
          <div className="tw-error-title">Error spotting</div>
          <div className="tw-error-intro">
            {payload.instructions || "Tap each word in the passage that contains a grammatical error."}
          </div>
        </div>
      </div>

      <div className="tw-error-subtitle">
        {submitted
          ? "Errors revealed."
          : payload.task_intro || "Tap each word that has a grammatical error."}
      </div>

      <div className="tw-error-passage">
        {(payload.passage_sentences ?? []).map((sentence) => (
          <div key={sentence.sentence_id} className="tw-error-sentence">
            {sentence.tokens.map((token) => (
              <button
                key={token.token_id}
                type="button"
                className={tokenClass(token)}
                disabled={submitted}
                onClick={() => toggleToken(token.token_id)}
                aria-pressed={selectedSet.has(token.token_id)}
              >
                {token.text}
              </button>
            ))}
          </div>
        ))}
      </div>

      {submitted && (
        <div className={`tw-result-banner ${bannerTone}`}>
          <div className="tw-result-icon">{I.spark}</div>
          <div className="tw-result-text">
            <div className="tw-result-headline">
              {summary.found.length} of {totalErrors} errors found
            </div>
            <div className="tw-result-sub">
              {summary.missed.length > 0
                ? `You missed ${summary.missed.length} error${summary.missed.length === 1 ? "" : "s"}.`
                : "All error words were found."}
            </div>
          </div>
          <div>
            <div className="tw-result-score">
              {recall}<span style={{ fontSize: 14 }}>%</span>
            </div>
            <div className="tw-result-score-sub">RECALL</div>
          </div>
        </div>
      )}

      {!submitted && (
        <div className="tw-error-meta">
          <span>Flagged: <strong>{selectedIds.length}</strong></span>
          <span>Errors in passage: <strong>{totalErrors}</strong></span>
        </div>
      )}

      {!submitted && (
        <button
          className="tw-submit-btn"
          disabled={!canSubmit}
          onClick={() => onSubmit({
            selected_token_ids: selectedIds,
            time_spent_seconds: Math.round((Date.now() - startedAt) / 1000),
          })}
        >
          {I.spark} Submit my flags
        </button>
      )}
    </div>
  );
}
