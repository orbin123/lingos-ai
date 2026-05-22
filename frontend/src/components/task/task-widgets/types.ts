import type { WidgetState } from "./shared";

export type WidgetKey =
  | "mcq"
  | "fill_in_blanks"
  | "open_text"
  | "timed_text"
  | "structured_essay"
  | "speak_and_record"
  | "listen_and_respond"
  | "storyboard";

export interface TaskEnvelope {
  task_intro?: string;
  estimated_time_minutes?: number;
  widget: WidgetKey;
  topic_id?: string;
  topic_name?: string;
  sub_skill?: string;
  sub_level?: number;
  activity?: string;
  instructions?: string;
}

export interface MCQItem {
  item_id: string;
  prompt: string;
  options: string[];
  correct_index: number;
  explanation: string;
}

export interface MCQPayload extends TaskEnvelope {
  widget: "mcq";
  items: MCQItem[];
  target_words?: string[];
  question_types_used?: string[];
  pattern_explained?: string;
  tone_concepts_taught?: string[];
}

export interface BlankItem {
  item_id?: string;
  blank_id?: string;
  sentence_with_blank: string;
  base_verb?: string | null;
  correct_answer: string;
  distractors?: string[];
  options?: string[];
  grammar_rule?: string;
  explanation: string;
}

export interface FillInBlanksPayload extends TaskEnvelope {
  widget: "fill_in_blanks";
  grammar_rule_explained?: string;
  passage_title?: string;
  passage?: string | null;
  blanks?: BlankItem[];
  items?: BlankItem[];
  total_blanks?: number;
  topic?: string;
}

export interface OpenTextItem {
  item_id: string;
  prompt: string;
  sample_answer: string;
  answer_hints: string[];
}

export interface OpenTextPayload extends TaskEnvelope {
  widget: "open_text";
  items: OpenTextItem[];
  grammar_rule_explained?: string;
  common_mistakes?: string[];
  target_words?: string[];
  minimum_target_words_used?: number;
  passage?: string;
  structure_pattern_taught?: string;
  source_passage?: string | null;
  source_audio_script?: string | null;
  source_audio_url?: string | null;
  target_register?: string;
}

export interface TimedTextPayload extends TaskEnvelope {
  widget: "timed_text";
  writing_prompt: string;
  time_limit_seconds: number;
  minimum_word_count: number;
  target_word_count: number;
  no_editing_allowed: boolean;
  sample_response: string;
}

export type EssaySectionName =
  | "introduction"
  | "background"
  | "main_point"
  | "supporting_detail"
  | "counter_point"
  | "conclusion";

export interface EssaySection {
  section_id: string;
  section_name: EssaySectionName | string;
  section_prompt: string;
  minimum_word_count: number;
  sample_text: string;
}

export interface StructuredEssayPayload extends TaskEnvelope {
  widget: "structured_essay";
  overall_topic: string;
  structure_pattern: string;
  total_target_words: number;
  sections: EssaySection[];
}

export interface SpeakRoleplayTurn {
  turn_id: string;
  speaker: "ai" | "user";
  ai_line: string | null;
  expected_user_tone: string | null;
}

export interface SpeakAndRecordPayload extends TaskEnvelope {
  widget: "speak_and_record";
  speaking_duration_seconds: number;
  speaking_prompts?: string[];
  sample_responses?: string[];
  speaking_items?: string[];
  target_pattern?: string;
  reference_audio_url?: string | null;
  use_azure_scoring?: boolean;
  grammar_rule_to_practice?: string;
  speaking_prompt?: string;
  sample_response?: string;
  preparation_seconds?: number;
  fluency_focus?: string;
  sample_talking_points?: string[];
  target_words?: string[];
  minimum_words_used?: number;
  text_to_read_aloud?: string;
  target_sounds_or_patterns?: string[];
  expected_difficult_words?: string[];
  passage?: string;
  word_count?: number;
  target_wpm?: number;
  time_limit_seconds?: number;
  source_audio_script?: string;
  source_audio_url?: string | null;
  retelling_prompt?: string;
  key_points_expected?: string[];
  scenario_description?: string;
  target_tone?: string;
  turns?: SpeakRoleplayTurn[];
  sample_user_responses?: string[];
}

export interface ListenAndRespondPayload extends TaskEnvelope {
  widget: "listen_and_respond";
  audio_script: string;
  audio_url: string | null;
  audio_duration_seconds?: number;
  browser_tts_fallback?: boolean;
  tts_error?: string;
  inner_widget: "mcq" | "fill_in_blanks" | "open_text" | "speak_and_record";
  items?: MCQItem[] | OpenTextItem[];
  text_to_shadow?: string;
  speed?: "slow" | "natural" | "fast";
  delay_seconds?: number;
  minimum_match_percentage?: number;
  target_words_in_audio?: string[];
  target_pattern?: string;
  audio_genre?: string;
  voice_style_hint?: string;
  structure_to_identify?: string;
}

export interface StoryboardScene {
  scene_id: string;
  scene_number: number;
  image_prompt: string;
  image_url: string | null;
  narration_focus: string;
}

export interface StoryboardPayload extends TaskEnvelope {
  widget: "storyboard";
  overall_story_premise: string;
  narrative_pattern: string;
  speaking_duration_seconds: number;
  sample_narration: string;
  scenes: StoryboardScene[];
}

export type AnyTaskPayload =
  | MCQPayload
  | FillInBlanksPayload
  | OpenTextPayload
  | TimedTextPayload
  | StructuredEssayPayload
  | SpeakAndRecordPayload
  | ListenAndRespondPayload
  | StoryboardPayload;

export interface WidgetProps<P extends AnyTaskPayload = AnyTaskPayload> {
  payload: P;
  answers: Record<string, unknown>;
  setAnswers: (next: Record<string, unknown>) => void;
  state: WidgetState;
  onSubmit: (answers?: Record<string, unknown>) => void;
}

export function resolveAudioUrl(url?: string | null): string | undefined {
  if (!url) return undefined;
  if (/^https?:\/\//i.test(url)) return url;
  const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  return `${apiBase.replace(/\/$/, "")}${url.startsWith("/") ? url : `/${url}`}`;
}

export function formatDuration(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds || 0));
  const m = Math.floor(safe / 60);
  const s = safe % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function blankId(blank: BlankItem): string {
  return blank.item_id || blank.blank_id || blank.sentence_with_blank;
}

export function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}
