"use client";

import type React from "react";
import { Check, FileText, Headphones, Mic2, PenLine, Play, Send } from "lucide-react";
import type { SessionTask, TaskWidgetKind } from "./tasks/source";
import { RuleCallout, TaskWidgetFrame, roundIconButton } from "./tasks/task_widgets/TaskWidgetFrame";

export type WidgetKey =
  | "mcq"
  | "fill_in_blanks"
  | "open_text"
  | "timed_text"
  | "structured_essay"
  | "speak_and_record"
  | "listen_and_respond"
  | "error_spotting"
  | "storyboard"
  | "error_correction";

export type AnyTaskPayload = Record<string, unknown> & {
  widget: WidgetKey;
  task_widget?: string;
  inner_widget?: string;
  blueprint_contract?: Record<string, unknown>;
};

export interface WidgetProps {
  payload: AnyTaskPayload;
  answers: Record<string, unknown>;
  setAnswers: (answers: Record<string, unknown>) => void;
  state: "before" | "after";
  onSubmit: (answers: Record<string, unknown>) => void;
}

const WIDGET_ALIASES: Record<string, WidgetKey> = {
  FillInBlanks: "fill_in_blanks",
  fill_blanks: "fill_in_blanks",
  fill_in_blanks: "fill_in_blanks",
  MCQList: "mcq",
  mcq: "mcq",
  OpenTextList: "open_text",
  open_text: "open_text",
  ErrorSpotting: "error_spotting",
  error_spotting: "error_spotting",
  ErrorCorrection: "error_correction",
  error_correction: "error_correction",
  SentenceTransform: "open_text",
  sentence_transform: "open_text",
  StructuredEssay: "structured_essay",
  structured_essay: "structured_essay",
  TimedWriting: "timed_text",
  timed_text: "timed_text",
  Storyboard: "storyboard",
  storyboard: "storyboard",
  SpeakAndRecord: "speak_and_record",
  speak_and_record: "speak_and_record",
  speak_record: "speak_and_record",
  speak_timed: "speak_and_record",
  read_aloud: "speak_and_record",
  speak_pic_desc: "speak_and_record",
  speak_present: "speak_and_record",
  speak_roleplay: "speak_and_record",
  speak_interview: "speak_and_record",
  speak_smalltalk: "speak_and_record",
  speak_debate: "speak_and_record",
  "ListenAndAnswer+MCQList": "listen_and_respond",
  "ListenAndAnswer+FillInBlanks": "listen_and_respond",
  "ListenAndAnswer+OpenTextList": "listen_and_respond",
  "ListenAndAnswer+SpeakAndRecord": "listen_and_respond",
  listen_and_respond: "listen_and_respond",
  listen_mcq: "listen_and_respond",
  listen_cloze: "listen_and_respond",
  listen_dictation: "listen_and_respond",
  listen_infer: "listen_and_respond",
  listen_tone: "listen_and_respond",
  listen_shadow: "listen_and_respond",
  listen_retell: "listen_and_respond",
};

export function normalizeWidgetKey(widget?: string | null): WidgetKey {
  const raw = String(widget || "").trim();
  if (raw in WIDGET_ALIASES) return WIDGET_ALIASES[raw];
  const snake = raw
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/[+\-\s]+/g, "_")
    .toLowerCase();
  return WIDGET_ALIASES[snake] ?? "open_text";
}

export const WIDGET_SECTION_LABEL: Record<WidgetKey, string> = {
  mcq: "Multiple choice",
  fill_in_blanks: "Fill in the blanks",
  open_text: "Writing task",
  timed_text: "Timed writing",
  structured_essay: "Essay",
  speak_and_record: "Speaking task",
  listen_and_respond: "Listening task",
  error_spotting: "Error spotting",
  storyboard: "Storyboard",
  error_correction: "Error correction",
};

export const WIDGET_COMPONENTS: Record<WidgetKey, React.ComponentType<WidgetProps>> = {
  mcq: RuntimeTaskWidget,
  fill_in_blanks: RuntimeTaskWidget,
  open_text: RuntimeTaskWidget,
  timed_text: RuntimeTaskWidget,
  structured_essay: RuntimeTaskWidget,
  speak_and_record: RuntimeTaskWidget,
  listen_and_respond: RuntimeTaskWidget,
  error_spotting: RuntimeTaskWidget,
  storyboard: RuntimeTaskWidget,
  error_correction: RuntimeTaskWidget,
};

function RuntimeTaskWidget({
  payload,
  answers,
  setAnswers,
  state,
  onSubmit,
}: WidgetProps) {
  const disabled = state === "after";
  const frameTask = buildRuntimeSessionTask(payload);
  const grammarRule =
    textValue(payload.grammar_rule) ||
    textValue(payload.grammar_rule_explained) ||
    textValue(payload.grammar_rule_to_practice);
  const targetWords = stringArray(payload.target_words);

  return (
    <TaskWidgetFrame task={frameTask} icon={runtimeTaskIcon(frameTask.widget)}>
      {grammarRule && <RuleCallout label="Focus rule">{grammarRule}</RuleCallout>}
      {targetWords.length > 0 && (
        <div className="tw-target-chip-row" style={{ marginBottom: 14 }}>
          {targetWords.map((word) => (
            <span className="tw-target-chip used" key={word}>
              {word}
            </span>
          ))}
        </div>
      )}

      <WidgetBody
        payload={payload}
        answers={answers}
        setAnswers={setAnswers}
        disabled={disabled}
      />

      <button
        type="button"
        className="tw-submit-btn"
        disabled={disabled}
        onClick={() => onSubmit(answers)}
      >
        <Send size={15} />
        Submit answers
      </button>
    </TaskWidgetFrame>
  );
}

export function buildRuntimeSessionTask(payload: AnyTaskPayload): SessionTask {
  const contract = objectValue(payload.blueprint_contract);
  const topic =
    textValue(payload.topic_name) ||
    textValue(payload.topic) ||
    textValue(contract.topic) ||
    WIDGET_SECTION_LABEL[payload.widget];
  const activity =
    textValue(payload.core_activity) ||
    textValue(payload.activity) ||
    textValue(contract.activity) ||
    activityLabelForWidget(payload.widget);
  const estimatedMinutes =
    numberValue(payload.estimated_time_minutes) ||
    numberValue(payload.estimatedMinutes) ||
    numberValue(contract.estimated_time_minutes) ||
    3;

  return {
    id:
      textValue(payload.activity_id) ||
      textValue(payload.attempt_id) ||
      textValue(contract.activity_id) ||
      `runtime-${payload.widget}`,
    sequence:
      numberValue(payload.sequence) ||
      numberValue(payload.activity_sequence) ||
      numberValue(contract.sequence) ||
      1,
    archetypeId:
      textValue(payload.archetype_id) ||
      textValue(contract.archetype_id) ||
      textValue(payload.task_widget) ||
      payload.widget,
    widget: normalizeRuntimeTaskKind(payload, contract),
    sectionLabel: WIDGET_SECTION_LABEL[payload.widget],
    topic,
    taskIntro:
      textValue(payload.task_intro) ||
      textValue(payload.title) ||
      textValue(payload.instructions_override) ||
      WIDGET_SECTION_LABEL[payload.widget],
    instructions:
      textValue(payload.instructions) ||
      textValue(payload.prompt) ||
      "Complete the activity below.",
    subSkill:
      textValue(payload.sub_skill) ||
      textValue(payload.skill_name) ||
      textValue(contract.sub_skill) ||
      "Practice",
    activity,
    estimatedMinutes,
  } as SessionTask;
}

function normalizeRuntimeTaskKind(
  payload: AnyTaskPayload,
  contract: Record<string, unknown>,
): TaskWidgetKind {
  const raw = (
    textValue(payload.task_widget) ||
    textValue(contract.task_widget) ||
    textValue(payload.archetype_id) ||
    payload.widget
  ).toLowerCase();
  const archetype = textValue(payload.archetype_id).toUpperCase();
  const inner = normalizeWidgetKey(textValue(payload.inner_widget));

  if (payload.widget === "fill_in_blanks") return "fill_blanks";
  if (payload.widget === "listen_and_respond") {
    if (raw.includes("cloze") || inner === "fill_in_blanks") return "listen_cloze";
    if (raw.includes("dictation")) return "listen_dictation";
    if (raw.includes("infer")) return "listen_infer";
    if (raw.includes("tone")) return "listen_tone";
    if (raw.includes("shadow")) return "listen_shadow";
    if (raw.includes("retell")) return "listen_retell";
    return "listen_mcq";
  }
  if (payload.widget === "speak_and_record") {
    if (raw.includes("timed") || archetype.includes("TIMED")) return "speak_timed";
    if (raw.includes("read_aloud") || archetype.includes("READ_ALOUD")) return "read_aloud";
    if (raw.includes("roleplay")) return "speak_roleplay";
    if (raw.includes("interview")) return "speak_interview";
    if (raw.includes("pic")) return "speak_pic_desc";
    if (raw.includes("present")) return "speak_present";
    if (raw.includes("smalltalk")) return "speak_smalltalk";
    if (raw.includes("debate")) return "speak_debate";
    return "speak_record";
  }
  if (payload.widget === "timed_text") return "write_timed";
  if (payload.widget === "structured_essay") return "write_paragraph";
  if (payload.widget === "storyboard") return "write_paragraph";
  if (payload.widget === "mcq") return "read_comp_mcq";
  return payload.widget;
}

function runtimeTaskIcon(widget: TaskWidgetKind) {
  if (widget.startsWith("listen_")) return <Headphones size={18} strokeWidth={2.5} />;
  if (widget.startsWith("speak_") || widget === "read_aloud") return <Mic2 size={18} strokeWidth={2.5} />;
  if (widget.startsWith("write_") || widget === "open_text" || widget === "sentence_transform") {
    return <PenLine size={18} strokeWidth={2.5} />;
  }
  return <FileText size={18} strokeWidth={2.5} />;
}

function activityLabelForWidget(widget: WidgetKey): string {
  if (widget === "listen_and_respond") return "Listen";
  if (widget === "speak_and_record") return "Speak";
  if (
    widget === "open_text" ||
    widget === "timed_text" ||
    widget === "structured_essay" ||
    widget === "storyboard" ||
    widget === "error_correction"
  ) {
    return "Write";
  }
  return "Read";
}

function WidgetBody({
  payload,
  answers,
  setAnswers,
  disabled,
}: {
  payload: AnyTaskPayload;
  answers: Record<string, unknown>;
  setAnswers: (answers: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  if (payload.widget === "listen_and_respond") {
    return (
      <>
        <AudioCard payload={payload} />
        <InnerResponse payload={payload} answers={answers} setAnswers={setAnswers} disabled={disabled} />
      </>
    );
  }
  return <InnerResponse payload={payload} answers={answers} setAnswers={setAnswers} disabled={disabled} />;
}

function InnerResponse({
  payload,
  answers,
  setAnswers,
  disabled,
}: {
  payload: AnyTaskPayload;
  answers: Record<string, unknown>;
  setAnswers: (answers: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  const inner = normalizeWidgetKey(textValue(payload.inner_widget));
  if (payload.widget === "fill_in_blanks" || inner === "fill_in_blanks") {
    return (
      <FillBlankInputs
        payload={payload}
        answers={answers}
        setAnswers={setAnswers}
        disabled={disabled}
      />
    );
  }
  if (payload.widget === "mcq" || inner === "mcq") {
    return <McqInputs payload={payload} answers={answers} setAnswers={setAnswers} disabled={disabled} />;
  }
  if (payload.widget === "speak_and_record") {
    return <OpenResponse payload={payload} answers={answers} setAnswers={setAnswers} disabled={disabled} label="Transcript" />;
  }
  return <OpenResponse payload={payload} answers={answers} setAnswers={setAnswers} disabled={disabled} />;
}

function AudioCard({ payload }: { payload: AnyTaskPayload }) {
  const script = textValue(payload.audio_script) || textValue(payload.source_audio_script);
  const playScript = () => {
    if (!script || typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(script);
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  };
  if (!script) return null;
  return (
    <div className="tw-card" style={{ background: "oklch(97% 0.02 245)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <button type="button" onClick={playScript} title="Play audio" aria-label="Play audio" style={roundIconButton}>
          <Play size={18} fill="currentColor" />
        </button>
        <div style={{ minWidth: 0 }}>
          <div className="tw-rule-label">{textValue(payload.audio_genre) || "Audio"}</div>
          <div style={{ fontSize: 13.5, lineHeight: 1.55, color: "var(--tw-navy)" }}>{script}</div>
        </div>
      </div>
    </div>
  );
}

function FillBlankInputs({
  payload,
  answers,
  setAnswers,
  disabled,
}: {
  payload: AnyTaskPayload;
  answers: Record<string, unknown>;
  setAnswers: (answers: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  const items = arrayValue(payload.blanks).length ? arrayValue(payload.blanks) : arrayValue(payload.items);
  const passage = textValue(payload.passage);
  return (
    <>
      {passage && (
        <div className="tw-passage">
          <div className="tw-passage-label">{textValue(payload.passage_title) || "Passage"}</div>
          {passage}
        </div>
      )}
      {items.map((item, index) => {
        const id = itemId(item, index);
        return (
          <div className="tw-card" key={id}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{textValue(item.sentence_with_blank) || textValue(item.prompt) || "Fill the blank."}</div>
            </div>
            <input
              className="tw-blank-input"
              disabled={disabled}
              value={String(answers[id] ?? "")}
              onChange={(event) => setAnswers({ ...answers, [id]: event.target.value })}
              style={{ width: "100%", textAlign: "left", minHeight: 38 }}
            />
          </div>
        );
      })}
    </>
  );
}

function McqInputs({
  payload,
  answers,
  setAnswers,
  disabled,
}: {
  payload: AnyTaskPayload;
  answers: Record<string, unknown>;
  setAnswers: (answers: Record<string, unknown>) => void;
  disabled: boolean;
}) {
  const items = arrayValue(payload.items);
  return (
    <>
      {items.map((item, index) => {
        const id = itemId(item, index);
        const selected = answers[id];
        const options = stringArray(item.options);
        return (
          <div className="tw-card" key={id}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{textValue(item.prompt)}</div>
            </div>
            <div className="tw-opt-list">
              {options.map((option, optionIndex) => (
                <button
                  key={option}
                  type="button"
                  disabled={disabled}
                  className={`tw-opt-row${selected === optionIndex ? " selected" : ""}`}
                  onClick={() => setAnswers({ ...answers, [id]: optionIndex })}
                >
                  <span className="tw-opt-key">{optionIndex + 1}</span>
                  <span style={{ flex: 1 }}>{option}</span>
                  {selected === optionIndex && <Check size={14} strokeWidth={2.8} />}
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
}

function OpenResponse({
  payload,
  answers,
  setAnswers,
  disabled,
  label = "Answer",
}: {
  payload: AnyTaskPayload;
  answers: Record<string, unknown>;
  setAnswers: (answers: Record<string, unknown>) => void;
  disabled: boolean;
  label?: string;
}) {
  const items = arrayValue(payload.items);
  const prompts = items.length
    ? items
    : [{ item_id: "response", prompt: textValue(payload.speaking_prompt) || textValue(payload.writing_prompt) || textValue(payload.prompt) || "Your response" }];
  return (
    <>
      {prompts.map((item, index) => {
        const id = itemId(item, index);
        return (
          <div className="tw-card" key={id}>
            <div className="tw-q-number-row">
              <div className="tw-q-number-badge">{index + 1}</div>
              <div className="tw-q-stem">{textValue(item.prompt) || label}</div>
            </div>
            <textarea
              className="tw-write-area"
              disabled={disabled}
              value={String(answers[id] ?? "")}
              onChange={(event) => setAnswers({ ...answers, [id]: event.target.value })}
              placeholder="Write your response here..."
            />
          </div>
        );
      })}
    </>
  );
}

function textValue(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function numberValue(value: unknown): number {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

function objectValue(value: unknown): Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.map((item) => String(item).trim()).filter(Boolean)
    : [];
}

function arrayValue(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null)
    : [];
}

function itemId(item: Record<string, unknown>, index: number): string {
  return (
    textValue(item.item_id) ||
    textValue(item.blank_id) ||
    textValue(item.id) ||
    `item_${index + 1}`
  );
}
