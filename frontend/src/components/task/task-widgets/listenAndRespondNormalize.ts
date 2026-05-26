import type { BlankItem, ListenAndRespondPayload, MCQItem, OpenTextItem } from "./types";

const INNER_WIDGET_ALIASES: Record<string, ListenAndRespondPayload["inner_widget"]> = {
  mcq: "mcq",
  mcqlist: "mcq",
  mcq_list: "mcq",
  multiplechoice: "mcq",
  multiple_choice: "mcq",
  "multiple-choice": "mcq",
  open_text: "open_text",
  opentext: "open_text",
  open_text_list: "open_text",
  opentextlist: "open_text",
  fill_in_blanks: "fill_in_blanks",
  fillinblanks: "fill_in_blanks",
  speak_and_record: "speak_and_record",
  speakandrecord: "speak_and_record",
};

export interface ListenAnalytics {
  play_count: number;
  total_listen_seconds: number;
  transcript_revealed: boolean;
}

export interface ListenAndRespondAnswers {
  listen_analytics?: Partial<ListenAnalytics>;
  inner_response?: {
    widget?: string;
    answers?: Array<Record<string, unknown>>;
  };
  time_spent_seconds?: number;
}

export function normalizeListenAndRespondPayload(
  payload: ListenAndRespondPayload,
): ListenAndRespondPayload {
  const innerWidget = normalizeInnerWidget(payload.inner_widget);
  const items = Array.isArray(payload.items) ? payload.items : [];
  const blankItems = innerWidget === "fill_in_blanks"
    ? normalizeBlankItems((items.length ? items : payload.blanks ?? []) as BlankItem[])
    : [];
  return {
    ...payload,
    inner_widget: innerWidget,
    items: innerWidget === "mcq"
      ? normalizeMCQItems(items)
      : innerWidget === "fill_in_blanks"
        ? blankItems
        : items,
    ...(innerWidget === "fill_in_blanks" ? { blanks: blankItems, total_blanks: blankItems.length } : {}),
  };
}

export function isPlayableListeningTask(payload: ListenAndRespondPayload): boolean {
  if (!(payload.audio_url || payload.audio_script?.trim())) return false;
  if (payload.inner_widget === "speak_and_record") return true;
  return Array.isArray(payload.items) && payload.items.length > 0;
}

export const isPlayableListeningMCQ = isPlayableListeningTask;

export function selectionsFromListenAnswers(
  answers: Record<string, unknown>,
): Record<string, number> {
  const rows = ((answers as ListenAndRespondAnswers).inner_response?.answers ?? []);
  const out: Record<string, number> = {};
  for (const row of rows) {
    const itemId = row?.item_id;
    const selectedIndex = row?.selected_index;
    if (typeof itemId === "string" && typeof selectedIndex === "number") {
      out[itemId] = selectedIndex;
    }
  }
  return out;
}

export function openTextFromListenAnswers(
  answers: Record<string, unknown>,
): Record<string, string> {
  const rows = ((answers as ListenAndRespondAnswers).inner_response?.answers ?? []);
  const out: Record<string, string> = {};
  for (const row of rows) {
    const itemId = row?.item_id;
    const userAnswer = row?.user_answer;
    if (typeof itemId === "string" && typeof userAnswer === "string") {
      out[itemId] = userAnswer;
    }
  }
  return out;
}

export function blanksFromListenAnswers(
  answers: Record<string, unknown>,
): Record<string, string> {
  const rows = ((answers as ListenAndRespondAnswers).inner_response?.answers ?? []);
  const out: Record<string, string> = {};
  for (const row of rows) {
    const itemId = row?.item_id ?? row?.blank_id;
    const userAnswer = row?.user_answer;
    if (typeof itemId === "string" && typeof userAnswer === "string") {
      out[itemId] = userAnswer;
    }
  }
  return out;
}

export function analyticsFromListenAnswers(
  answers: Record<string, unknown>,
): ListenAnalytics {
  const analytics = (answers as ListenAndRespondAnswers).listen_analytics ?? {};
  return {
    play_count: Number(analytics.play_count ?? 0) || 0,
    total_listen_seconds: Number(analytics.total_listen_seconds ?? 0) || 0,
    transcript_revealed: Boolean(analytics.transcript_revealed),
  };
}

export function countCorrectListeningMCQ(
  items: MCQItem[],
  selections: Record<string, number>,
): number {
  return items.filter((item) => selections[item.item_id] === item.correct_index).length;
}

export function countCorrectListeningBlanks(
  items: BlankItem[],
  values: Record<string, string>,
): number {
  return items.filter((item) => {
    const itemId = item.item_id || item.blank_id || item.sentence_with_blank;
    return (values[itemId] ?? "").trim().toLowerCase() === item.correct_answer.trim().toLowerCase();
  }).length;
}

function normalizeInnerWidget(raw: string): ListenAndRespondPayload["inner_widget"] {
  const key = String(raw || "").trim();
  if (!key) return "mcq";
  const compact = key.replace(/\s+/g, "_").toLowerCase();
  return INNER_WIDGET_ALIASES[compact] ?? (key as ListenAndRespondPayload["inner_widget"]);
}

function normalizeMCQItems(items: Array<MCQItem | OpenTextItem | BlankItem>): MCQItem[] {
  return items
    .map((item, index) => normalizeMCQItem(item, index))
    .filter((item): item is MCQItem => item !== null);
}

function normalizeBlankItems(items: BlankItem[]): BlankItem[] {
  return items
    .map((item, index) => normalizeBlankItem(item, index))
    .filter((item): item is BlankItem => item !== null);
}

function normalizeBlankItem(item: BlankItem, index: number): BlankItem | null {
  const raw = item as unknown as Record<string, unknown>;
  const sentence = String(raw.sentence_with_blank ?? "").replace(/_{3,}/g, "___").trim();
  const correct = String(raw.correct_answer ?? "").trim();
  if (!sentence || !sentence.includes("___") || !correct) return null;
  const itemId = String(raw.item_id || raw.blank_id || `b${index + 1}`);
  return {
    ...item,
    item_id: itemId,
    blank_id: String(raw.blank_id || itemId),
    sentence_with_blank: sentence,
    correct_answer: correct,
    explanation: String(raw.explanation ?? ""),
  };
}

function normalizeMCQItem(item: MCQItem | OpenTextItem | BlankItem, index: number): MCQItem | null {
  const raw = item as unknown as Record<string, unknown>;
  const options = Array.isArray(raw.options)
    ? raw.options.map((option) => String(option).trim()).filter(Boolean)
    : [];
  const correctIndex = Number(raw.correct_index);
  const prompt = String(raw.prompt ?? "").trim();
  if (!prompt || options.length !== 4 || !Number.isInteger(correctIndex)) {
    return null;
  }
  if (correctIndex < 0 || correctIndex >= options.length) return null;
  return {
    item_id: String(raw.item_id || `q${index + 1}`),
    prompt,
    options,
    correct_index: correctIndex,
    explanation: String(raw.explanation ?? ""),
  };
}
