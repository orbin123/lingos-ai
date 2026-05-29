/**
 * Contract task adapter (M4 — rich-widget convergence).
 *
 * Bridges the validated backend task payload (the snake_case JSON emitted on the
 * WS `task` event, shaped by the backend contract in
 * `app/modules/sessions/contracts`) to the rich `SessionTask` shape the
 * `TaskWidgetRenderer` widget library consumes (camelCase, with answer views).
 *
 * The adapter produces the task *structure* only. In production the widget runs
 * in live interactive mode (see `LiveTaskController`): it collects answers and
 * renders its own review state from the learner's answers, so the answer views
 * baked into `SessionTask` here are left empty.
 *
 * Converged for the Week 1 Day 1 widget set: `fill_blanks`, `listen_mcq`,
 * `listen_cloze`, `open_text`, `speak_timed`. Other archetypes return `null`,
 * and the caller falls back to the generic widget.
 */

import { buildRuntimeSessionTask, type AnyTaskPayload } from "./runtimeMapping";
import type {
  FillBlanksTask,
  ListenClozeTask,
  ListenMcqTask,
  OpenTextTask,
  SessionTask,
  SpeakTimedTask,
  TaskWidgetKind,
} from "./tasks/source";

const CONVERGED_WIDGETS: ReadonlySet<TaskWidgetKind> = new Set<TaskWidgetKind>([
  "fill_blanks",
  "listen_cloze",
  "listen_mcq",
  "open_text",
  "speak_timed",
]);

/**
 * The rich task widget an event's contract routes to, or `null` when this
 * archetype has not yet been converged onto the rich library.
 */
export function contractTaskWidget(payload: AnyTaskPayload): TaskWidgetKind | null {
  const contract = (payload.activity_contract ?? {}) as Record<string, unknown>;
  const blueprint = (payload.blueprint_contract ?? {}) as Record<string, unknown>;
  const raw = String(contract.task_widget ?? blueprint.task_widget ?? payload.task_widget ?? "");
  return CONVERGED_WIDGETS.has(raw as TaskWidgetKind) ? (raw as TaskWidgetKind) : null;
}

/**
 * Adapt a validated backend task payload into a rich `SessionTask`. Returns
 * `null` for archetypes not yet converged onto the rich library.
 */
export function adaptContractTask(payload: AnyTaskPayload): SessionTask | null {
  switch (contractTaskWidget(payload)) {
    case "fill_blanks":
      return adaptFillBlanks(payload);
    case "listen_mcq":
      return adaptListenMcq(payload);
    case "listen_cloze":
      return adaptListenCloze(payload);
    case "open_text":
      return adaptOpenText(payload);
    case "speak_timed":
      return adaptSpeakTimed(payload);
    default:
      return null;
  }
}

function adaptFillBlanks(payload: AnyTaskPayload): FillBlanksTask {
  const base = baseFields(payload);
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || textValue(raw.blank_id) || `item_${index + 1}`,
    sentenceWithBlank: textValue(raw.sentence_with_blank),
    baseVerb: textValue(raw.base_verb),
    correctAnswer: textValue(raw.correct_answer),
    explanation: textValue(raw.explanation),
  }));
  return {
    ...base,
    widget: "fill_blanks",
    passageTitle: textValue(payload.passage_title) || "Passage",
    passage: textValue(payload.passage),
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: {}, wrong: {} },
  };
}

function adaptListenMcq(payload: AnyTaskPayload): ListenMcqTask {
  const base = baseFields(payload);
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    prompt: textValue(raw.prompt),
    options: stringArray(raw.options),
    correctIndex: numberValue(raw.correct_index),
    explanation: textValue(raw.explanation),
  }));
  return {
    ...base,
    widget: "listen_mcq",
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    innerWidget: "mcq",
    items,
    answers: { correct: {}, wrong: {} },
  };
}

function adaptListenCloze(payload: AnyTaskPayload): ListenClozeTask {
  const base = baseFields(payload);
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || textValue(raw.blank_id) || `item_${index + 1}`,
    sentenceWithBlank: textValue(raw.sentence_with_blank),
    baseVerb: textValue(raw.base_verb),
    correctAnswer: textValue(raw.correct_answer),
    explanation: textValue(raw.explanation),
  }));
  return {
    ...base,
    widget: "listen_cloze",
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    passageTitle: textValue(payload.passage_title) || "Passage",
    passage: textValue(payload.passage),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    items,
    answers: { correct: {}, wrong: {} },
  };
}

function adaptOpenText(payload: AnyTaskPayload): OpenTextTask {
  const base = baseFields(payload);
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || textValue(raw.id) || `item_${index + 1}`,
    prompt: textValue(raw.prompt),
    sampleAnswer: textValue(raw.sample_answer),
    answerHints: stringArray(raw.answer_hints),
  }));
  return {
    ...base,
    widget: "open_text",
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    commonMistakes: stringArray(payload.common_mistakes),
    items,
    answers: { correct: [], wrong: [] },
  };
}

function adaptSpeakTimed(payload: AnyTaskPayload): SpeakTimedTask {
  const base = baseFields(payload);
  const fallbackPrompt = textValue(payload.speaking_prompt) || textValue(payload.prompt);
  const fallbackSample = textValue(payload.sample_response);
  const prompts = firstStringArray(payload.prompts, payload.speaking_prompts);
  const samples = firstStringArray(payload.sample_responses, payload.sample_answers);
  const allPrompts = prompts.length > 0 ? prompts : fallbackPrompt ? [fallbackPrompt] : [];
  const allSamples = samples.length > 0 ? samples : fallbackSample ? [fallbackSample] : [];
  return {
    ...base,
    widget: "speak_timed",
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: numberValue(payload.speaking_duration_seconds) || 45,
    prompts: allPrompts,
    sampleResponses: allSamples,
    prompt: allPrompts[0] || "",
    sampleResponse: allSamples[0] || "",
    answers: { correct: [], wrong: [] },
  };
}

// ── shared mapping helpers ──────────────────────────────────────────

/** BaseTask fields, reusing the runtime mapping so derivations stay consistent. */
function baseFields(payload: AnyTaskPayload) {
  const b = buildRuntimeSessionTask(payload);
  return {
    id: b.id,
    sequence: b.sequence,
    archetypeId: b.archetypeId,
    sectionLabel: b.sectionLabel,
    topic: b.topic,
    taskIntro: b.taskIntro,
    instructions: b.instructions,
    subSkill: b.subSkill,
    activity: b.activity,
    estimatedMinutes: b.estimatedMinutes,
  };
}

function grammarRule(payload: AnyTaskPayload): string {
  return (
    textValue(payload.grammar_rule) ||
    textValue(payload.grammar_rule_explained) ||
    textValue(payload.grammar_rule_to_practice)
  );
}

function textValue(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function numberValue(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((v) => String(v)) : [];
}

function firstStringArray(...values: unknown[]): string[] {
  for (const value of values) {
    const strings = stringArray(value).filter((item) => item.trim().length > 0);
    if (strings.length > 0) return strings;
  }
  return [];
}

function arrayValue(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter(
        (item): item is Record<string, unknown> =>
          typeof item === "object" && item !== null,
      )
    : [];
}
