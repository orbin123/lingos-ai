import type { BlankItem, FillInBlanksPayload } from "./types";

interface LegacyFillBlankActivity {
  activity_type?: string;
  instruction?: string;
  instructions?: string;
  questions?: Record<string, unknown>;
  answers?: Record<string, unknown>;
  explanations?: Record<string, unknown>;
  passage?: unknown;
  primary_text?: unknown;
  source?: { text?: unknown } | null;
}

interface LegacyFillBlankPayload extends FillInBlanksPayload {
  instruction?: string;
  source?: { text?: unknown } | null;
  primary_text?: string | null;
  activities?: LegacyFillBlankActivity[];
  answers?: Record<string, unknown> | unknown[];
  answer_key?: Record<string, unknown> | unknown[];
  correct_answers?: Record<string, unknown> | unknown[];
}

const LEGACY_FILL_BLANK_TYPES = new Set(["fill_in_the_blanks", "fill_in_blanks"]);

export function normalizeFillInBlanksPayload(
  payload: FillInBlanksPayload,
): FillInBlanksPayload {
  const source = payload as LegacyFillBlankPayload;
  const legacyActivity = source.activities?.find((activity) =>
    LEGACY_FILL_BLANK_TYPES.has(String(activity.activity_type || "")),
  );
  const instructions =
    cleanText(source.instructions) ||
    cleanText(source.instruction) ||
    cleanText(legacyActivity?.instructions) ||
    cleanText(legacyActivity?.instruction) ||
    source.instructions;
  const passage =
    cleanText(source.passage) ||
    cleanText(source.source?.text) ||
    cleanText(source.primary_text) ||
    cleanText(legacyActivity?.passage) ||
    cleanText(legacyActivity?.source?.text) ||
    cleanText(legacyActivity?.primary_text) ||
    source.passage;
  const normalizedPassage = normalizeBlankMarkers(cleanText(passage) || "");
  const items =
    nativeItems(source) ||
    legacyItems(legacyActivity) ||
    passageItems(normalizedPassage, source);

  return {
    ...payload,
    ...(instructions ? { instructions } : {}),
    ...(normalizedPassage ? { passage: normalizedPassage } : {}),
    ...(items ? { items, blanks: items, total_blanks: items.length } : {}),
  };
}

export function areFillInBlanksAnswered(
  blanks: BlankItem[],
  answers: Record<string, unknown>,
): boolean {
  return (
    blanks.length > 0 &&
    blanks.every((blank) => {
      const value = answers[answerKey(blank)];
      return typeof value === "string" && value.trim().length > 0;
    })
  );
}

function nativeItems(payload: FillInBlanksPayload): BlankItem[] | null {
  const rawItems = payload.items ?? payload.blanks;
  if (!rawItems || rawItems.length === 0) return null;
  const items = rawItems
    .map((item, index) => normalizeItem(item, index + 1))
    .filter((item): item is BlankItem => item !== null);
  return items.length > 0 ? items : null;
}

function legacyItems(activity?: LegacyFillBlankActivity): BlankItem[] | null {
  if (!activity?.questions) return null;
  const items = Object.entries(activity.questions)
    .map(([id, sentence], index) => {
      const itemId = id.trim() || `blank_${index + 1}`;
      return normalizeItem(
        {
          item_id: itemId,
          blank_id: itemId,
          sentence_with_blank: String(sentence || ""),
          correct_answer: String(
            activity.answers?.[id] ?? activity.answers?.[itemId] ?? "",
          ),
          explanation: String(
            activity.explanations?.[id] ??
              activity.explanations?.[itemId] ??
              "Review the target grammar for this blank.",
          ),
        },
        index + 1,
      );
    })
    .filter((item): item is BlankItem => item !== null);
  return items.length > 0 ? items : null;
}

function passageItems(
  passage: string,
  payload: LegacyFillBlankPayload,
): BlankItem[] | null {
  const total = passage.match(/_{3,}/g)?.length ?? 0;
  if (total === 0) return null;
  const answers = answerLookup(payload);
  return Array.from({ length: total }, (_, offset) => {
    const index = offset + 1;
    const itemId = `blank_${index}`;
    return normalizeItem(
      {
        item_id: itemId,
        blank_id: itemId,
        sentence_with_blank: `Blank ${index}: ___`,
        correct_answer: String(
          answers[itemId] ?? answers[`Q${index}`] ?? answers[index] ?? "",
        ),
        explanation: "Review the target grammar for this blank.",
      },
      index,
    );
  }).filter((item): item is BlankItem => item !== null);
}

function normalizeItem(item: BlankItem, index: number): BlankItem | null {
  const sentence = normalizeBlankMarkers(cleanText(item.sentence_with_blank) || "");
  if (!sentence) return null;
  const itemId = item.item_id || item.blank_id || `blank_${index}`;
  return {
    ...item,
    item_id: itemId,
    blank_id: item.blank_id || itemId,
    sentence_with_blank: sentence,
    correct_answer: item.correct_answer || "",
    explanation: item.explanation || "",
  };
}

function cleanText(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function normalizeBlankMarkers(value: string): string {
  return value.replace(/_{3,}/g, "___");
}

function answerLookup(payload: LegacyFillBlankPayload): Record<string | number, unknown> {
  const raw = payload.answers || payload.answer_key || payload.correct_answers || {};
  if (Array.isArray(raw)) {
    return Object.fromEntries(raw.map((answer, index) => [index + 1, answer]));
  }
  return raw;
}

function answerKey(blank: BlankItem): string {
  return blank.item_id || blank.blank_id || blank.sentence_with_blank;
}
