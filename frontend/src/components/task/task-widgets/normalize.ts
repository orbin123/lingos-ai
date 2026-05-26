import type { WidgetKey } from "./types";

const WIDGET_ALIASES: Record<string, WidgetKey> = {
  FillInBlanks: "fill_in_blanks",
  MCQList: "mcq",
  "ListenAndAnswer+MCQList": "listen_and_respond",
  "ListenAndAnswer+FillInBlanks": "listen_and_respond",
  "ListenAndAnswer+OpenTextList": "listen_and_respond",
  "ListenAndAnswer+SpeakAndRecord": "listen_and_respond",
  SpeakAndRecord: "speak_and_record",
  Storyboard: "storyboard",
  StructuredEssay: "structured_essay",
  OpenTextList: "open_text",
  ErrorSpotting: "error_spotting",
  SentenceTransform: "open_text",
  ErrorCorrection: "error_correction",
  TimedText: "timed_text",
};

export function normalizeWidgetKey(widget: string): string {
  return WIDGET_ALIASES[widget] ?? widget;
}
