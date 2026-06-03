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
  ErrorCorrectionTask,
  ErrorSpottingTask,
  FillBlanksTask,
  ListenClozeTask,
  ListenDictationTask,
  ListenInferTask,
  ListenMcqTask,
  ListenRetellTask,
  ListenShadowTask,
  ListenToneTask,
  McqItem,
  OpenTextTask,
  ReadAloudTask,
  ReadCompMcqTask,
  ReadContextMcqTask,
  ReadStructureTask,
  ReadTfngTask,
  ReadToneIdTask,
  ReadWordMatchTask,
  SentenceTransformTask,
  SessionTask,
  SpeakDebateTask,
  SpeakInterviewTask,
  SpeakPicDescTask,
  SpeakPresentTask,
  SpeakRoleplayTask,
  SpeakSmalltalkTask,
  SpeakTimedTask,
  TaskWidgetKind,
  WriteBulletsToParaTask,
  WriteEmailTask,
  WriteParagraphTask,
  WriteParaphraseTask,
  WriteTimedTask,
  WriteWordUpgradeTask,
} from "./tasks/source";

const CONVERGED_WIDGETS: ReadonlySet<TaskWidgetKind> = new Set<TaskWidgetKind>([
  "fill_blanks",
  "listen_cloze",
  "listen_mcq",
  "open_text",
  "speak_timed",
  // Mcq family
  "read_comp_mcq",
  "read_context_mcq",
  "read_tone_id",
  "read_word_match",
  "listen_infer",
  "listen_tone",
  // OpenText family
  "write_paragraph",
  "write_email",
  "write_timed",
  "write_paraphrase",
  "write_word_upgrade",
  "write_bullets_to_para",
  // Transform family
  "sentence_transform",
  // Dictation family
  "listen_dictation",
  // Speaking (non-pronunciation) family
  "speak_pic_desc",
  "speak_present",
  "speak_smalltalk",
  "speak_roleplay",
  "speak_interview",
  "speak_debate",
  "listen_retell",
  // Tail
  "read_tfng",
  "read_structure",
  "error_correction",
  "error_spotting",
  // Speaking (pronunciation) family
  "read_aloud",
  "listen_shadow",
]);

/**
 * The raw `task_widget` string a contract task event declares (empty when the
 * payload is not a contract task at all). Used to tell "no rich widget yet" from
 * "not a contract task" so the live page can scream on the former.
 */
export function rawContractTaskWidget(payload: AnyTaskPayload): string {
  const contract = (payload.activity_contract ?? {}) as Record<string, unknown>;
  const blueprint = (payload.blueprint_contract ?? {}) as Record<string, unknown>;
  return String(contract.task_widget ?? blueprint.task_widget ?? payload.task_widget ?? "");
}

/**
 * The rich task widget an event's contract routes to, or `null` when this
 * archetype has not yet been converged onto the rich library.
 */
export function contractTaskWidget(payload: AnyTaskPayload): TaskWidgetKind | null {
  const raw = rawContractTaskWidget(payload);
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
    case "read_comp_mcq":
      return adaptReadCompMcq(payload);
    case "read_context_mcq":
      return adaptReadContextMcq(payload);
    case "read_tone_id":
      return adaptReadToneId(payload);
    case "read_word_match":
      return adaptReadWordMatch(payload);
    case "listen_infer":
      return adaptListenInfer(payload);
    case "listen_tone":
      return adaptListenTone(payload);
    case "write_paragraph":
      return adaptWriteParagraph(payload);
    case "write_email":
      return adaptWriteEmail(payload);
    case "write_timed":
      return adaptWriteTimed(payload);
    case "write_paraphrase":
      return adaptWriteParaphrase(payload);
    case "write_word_upgrade":
      return adaptWriteWordUpgrade(payload);
    case "write_bullets_to_para":
      return adaptWriteBulletsToPara(payload);
    case "sentence_transform":
      return adaptSentenceTransform(payload);
    case "listen_dictation":
      return adaptListenDictation(payload);
    case "speak_pic_desc":
      return adaptSpeakPicDesc(payload);
    case "speak_present":
      return adaptSpeakPresent(payload);
    case "speak_smalltalk":
      return adaptSpeakSmalltalk(payload);
    case "speak_roleplay":
      return adaptSpeakRoleplay(payload);
    case "speak_interview":
      return adaptSpeakInterview(payload);
    case "speak_debate":
      return adaptSpeakDebate(payload);
    case "listen_retell":
      return adaptListenRetell(payload);
    case "read_tfng":
      return adaptReadTfng(payload);
    case "read_structure":
      return adaptReadStructure(payload);
    case "error_correction":
      return adaptErrorCorrection(payload);
    case "error_spotting":
      return adaptErrorSpotting(payload);
    case "read_aloud":
      return adaptReadAloud(payload);
    case "listen_shadow":
      return adaptListenShadow(payload);
    default: {
      // Every Week 1–4 archetype is converged. A non-empty raw task_widget that
      // reaches here is a regression (a new/renamed archetype with no adapter) —
      // make it scream in dev rather than silently dropping to the generic widget.
      const raw = rawContractTaskWidget(payload);
      if (raw && process.env.NODE_ENV !== "production") {
        // eslint-disable-next-line no-console
        console.error(
          `[contractTaskAdapter] task_widget="${raw}" has no rich-widget adapter; ` +
            `it will fall back to the generic runtime widget. Add it to CONVERGED_WIDGETS + adaptContractTask.`,
        );
      }
      return null;
    }
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
// ── Mcq family ────────────────────────────────────────────────────────────
// Every Mcq archetype emits the same `items[{item_id, prompt, options,
// correct_index, explanation}]` body (McqPayload). The per-widget adapters reuse
// this and add their own framing (reading passage vs listening audio).
function mcqItems(payload: AnyTaskPayload): McqItem[] {
  return arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    prompt: textValue(raw.prompt),
    options: stringArray(raw.options),
    correctIndex: numberValue(raw.correct_index),
    explanation: textValue(raw.explanation),
  }));
}

function adaptReadCompMcq(payload: AnyTaskPayload): ReadCompMcqTask {
  return {
    ...baseFields(payload),
    widget: "read_comp_mcq",
    passageTitle: textValue(payload.passage_title) || "Passage",
    passage: textValue(payload.passage),
    grammarRule: grammarRule(payload),
    items: mcqItems(payload),
    answers: { correct: {}, wrong: {} },
  };
}

function adaptReadContextMcq(payload: AnyTaskPayload): ReadContextMcqTask {
  return {
    ...baseFields(payload),
    widget: "read_context_mcq",
    passageTitle: textValue(payload.passage_title) || "Passage",
    passage: textValue(payload.passage),
    grammarRule: grammarRule(payload),
    items: mcqItems(payload),
    answers: { correct: {}, wrong: {} },
  };
}

function adaptReadToneId(payload: AnyTaskPayload): ReadToneIdTask {
  // `sender`/`message` are mock-only embellishments absent from the wire; the
  // widget falls back to rendering the prompt + options when they are empty.
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    sender: "",
    message: "",
    prompt: textValue(raw.prompt),
    options: stringArray(raw.options),
    correctIndex: numberValue(raw.correct_index),
    explanation: textValue(raw.explanation),
  }));
  return {
    ...baseFields(payload),
    widget: "read_tone_id",
    passageTitle: textValue(payload.passage_title) || "Messages",
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: {}, wrong: {} },
  };
}

function adaptReadWordMatch(payload: AnyTaskPayload): ReadWordMatchTask {
  // READ_WORD_MATCH is an Mcq archetype on the wire (objective index scoring):
  // live items carry their own options + correct index and submit `selected_index`.
  const items = arrayValue(payload.items).map((raw, index) => {
    const options = stringArray(raw.options);
    const correctIndex = numberValue(raw.correct_index);
    return {
      itemId: textValue(raw.item_id) || `item_${index + 1}`,
      prompt: textValue(raw.prompt),
      options,
      correctIndex,
      correctAnswer: options[correctIndex] ?? "",
      explanation: textValue(raw.explanation),
    };
  });
  return {
    ...baseFields(payload),
    widget: "read_word_match",
    grammarRule: grammarRule(payload),
    items,
    options: items[0]?.options ?? [],
    answers: { correct: {}, wrong: {} },
  };
}

function adaptListenInfer(payload: AnyTaskPayload): ListenInferTask {
  return {
    ...baseFields(payload),
    widget: "listen_infer",
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    intentFocus: grammarRule(payload),
    items: mcqItems(payload),
    answers: { correct: {}, wrong: {} },
  };
}

function adaptListenTone(payload: AnyTaskPayload): ListenToneTask {
  return {
    ...baseFields(payload),
    widget: "listen_tone",
    grammarRule: grammarRule(payload),
    intros: [],
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    items: mcqItems(payload),
    answers: { correct: {}, wrong: {} },
  };
}

// ── OpenText family ─────────────────────────────────────────────────────────
// Every OpenText archetype emits `items[{item_id, prompt, sample_answer,
// answer_hints}]` plus top-level `prompt`/`sample_answer`/`minimum_words`/
// `bullets`. Single-prompt widgets read the top-level fields + the first item_id;
// multi-item widgets (paraphrase, word-upgrade) map each item. All submit the
// flat `{item_id: text}` map the LLM evaluator reads.
function firstItemId(payload: AnyTaskPayload): string {
  return textValue(arrayValue(payload.items)[0]?.item_id) || "item_1";
}

function adaptWriteParagraph(payload: AnyTaskPayload): WriteParagraphTask {
  const items = arrayValue(payload.items);
  return {
    ...baseFields(payload),
    widget: "write_paragraph",
    prompt: textValue(payload.prompt) || textValue(items[0]?.prompt),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    minimumWords: numberValue(payload.minimum_words),
    sampleAnswer: textValue(payload.sample_answer) || textValue(items[0]?.sample_answer),
    answerHints: stringArray(items[0]?.answer_hints),
    itemId: firstItemId(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptWriteEmail(payload: AnyTaskPayload): WriteEmailTask {
  const items = arrayValue(payload.items);
  return {
    ...baseFields(payload),
    widget: "write_email",
    prompt: textValue(payload.prompt) || textValue(items[0]?.prompt),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    minimumWords: numberValue(payload.minimum_words),
    sampleAnswer: textValue(payload.sample_answer) || textValue(items[0]?.sample_answer),
    answerHints: stringArray(items[0]?.answer_hints),
    itemId: firstItemId(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptWriteTimed(payload: AnyTaskPayload): WriteTimedTask {
  const items = arrayValue(payload.items);
  return {
    ...baseFields(payload),
    widget: "write_timed",
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    writingDurationSeconds: numberValue(payload.writing_duration_seconds) || 300,
    prompt: textValue(payload.prompt) || textValue(items[0]?.prompt),
    sampleAnswer: textValue(payload.sample_answer) || textValue(items[0]?.sample_answer),
    answerHints: stringArray(items[0]?.answer_hints),
    itemId: firstItemId(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptWriteBulletsToPara(payload: AnyTaskPayload): WriteBulletsToParaTask {
  const items = arrayValue(payload.items);
  return {
    ...baseFields(payload),
    widget: "write_bullets_to_para",
    bullets: stringArray(payload.bullets),
    prompt: textValue(payload.prompt) || textValue(items[0]?.prompt),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    minimumWords: numberValue(payload.minimum_words),
    sampleAnswer: textValue(payload.sample_answer) || textValue(items[0]?.sample_answer),
    answerHints: stringArray(items[0]?.answer_hints),
    itemId: firstItemId(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptWriteParaphrase(payload: AnyTaskPayload): WriteParaphraseTask {
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    incorrectSentence: textValue(raw.incorrect_sentence) || textValue(raw.prompt) || textValue(raw.source_sentence),
    sampleAnswer: textValue(raw.sample_answer),
    watchHints: firstStringArray(raw.watch_hints, raw.answer_hints),
  }));
  return {
    ...baseFields(payload),
    widget: "write_paraphrase",
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: [], wrong: [] },
  };
}

function adaptWriteWordUpgrade(payload: AnyTaskPayload): WriteWordUpgradeTask {
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    sourceSentence: textValue(raw.prompt) || textValue(raw.source_sentence),
    targetUpgradeWord: textValue(raw.target_upgrade_word),
    sampleAnswer: textValue(raw.sample_answer),
    watchHints: stringArray(raw.answer_hints),
  }));
  return {
    ...baseFields(payload),
    widget: "write_word_upgrade",
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: [], wrong: [] },
  };
}

// ── Speaking (non-pronunciation) family ─────────────────────────────────────
// All SpeakingPayload archetypes share `prompts`/`sample_responses` +
// `speaking_duration_seconds`; per-widget framing comes from `image_url`,
// `dialogue_context`, `questions`, `passage_to_retell`. Recordings submit the
// canonical `{recordings, time_spent_seconds}` shape (see LiveSpeakingRecorder).
function speakingPrompts(payload: AnyTaskPayload): string[] {
  return firstStringArray(payload.prompts, payload.speaking_prompts);
}
function speakingSamples(payload: AnyTaskPayload): string[] {
  return firstStringArray(payload.sample_responses, payload.sample_answers);
}
function speakingDuration(payload: AnyTaskPayload, fallback: number): number {
  return numberValue(payload.speaking_duration_seconds) || fallback;
}
function dialogueTurns(payload: AnyTaskPayload): { role: string; text: string; speaker: "partner" | "learner" }[] {
  return arrayValue(payload.dialogue_context).map((raw) => ({
    role: textValue(raw.role),
    text: textValue(raw.text),
    speaker: textValue(raw.speaker) === "learner" ? "learner" : "partner",
  }));
}

function adaptSpeakPicDesc(payload: AnyTaskPayload): SpeakPicDescTask {
  const imageError = textValue(payload.image_error);
  return {
    ...baseFields(payload),
    widget: "speak_pic_desc",
    imageUrl: textValue(payload.image_url),
    imageAlt: textValue(payload.image_alt),
    ...(imageError ? { imageError } : {}),
    grammarRule: grammarRule(payload),
    speakingDurationSeconds: speakingDuration(payload, 45),
    prompts: speakingPrompts(payload),
    sampleResponses: speakingSamples(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptSpeakPresent(payload: AnyTaskPayload): SpeakPresentTask {
  const samples = speakingSamples(payload);
  return {
    ...baseFields(payload),
    widget: "speak_present",
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: speakingDuration(payload, 60),
    visualPromptDescription: textValue(payload.image_alt) || textValue(payload.visual_prompt_description),
    modelPresentation: samples[0],
    prompts: speakingPrompts(payload),
    sampleResponses: samples,
    answers: { correct: [], wrong: [] },
  };
}

function adaptSpeakSmalltalk(payload: AnyTaskPayload): SpeakSmalltalkTask {
  return {
    ...baseFields(payload),
    widget: "speak_smalltalk",
    dialogueContext: dialogueTurns(payload),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: speakingDuration(payload, 45),
    prompts: speakingPrompts(payload),
    sampleResponses: speakingSamples(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptSpeakRoleplay(payload: AnyTaskPayload): SpeakRoleplayTask {
  return {
    ...baseFields(payload),
    widget: "speak_roleplay",
    dialogueContext: dialogueTurns(payload),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: speakingDuration(payload, 45),
    prompts: speakingPrompts(payload),
    sampleResponses: speakingSamples(payload),
    answers: { correct: [], wrong: [] },
  };
}

function adaptSpeakInterview(payload: AnyTaskPayload): SpeakInterviewTask {
  const rawQuestions = arrayValue(payload.questions);
  const samples = speakingSamples(payload);
  const questions =
    rawQuestions.length > 0
      ? rawQuestions.map((raw, index) => ({
          itemId: textValue(raw.item_id) || `item_${index + 1}`,
          interviewerPrompt: textValue(raw.interviewer_prompt) || textValue(raw.prompt),
          sampleAnswer: textValue(raw.sample_answer),
          answerHint: textValue(raw.answer_hint),
        }))
      : speakingPrompts(payload).map((prompt, index) => ({
          itemId: `item_${index + 1}`,
          interviewerPrompt: prompt,
          sampleAnswer: samples[index] ?? "",
          answerHint: "",
        }));
  return {
    ...baseFields(payload),
    widget: "speak_interview",
    interviewContext: textValue(payload.interview_context) || textValue(payload.image_alt),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: speakingDuration(payload, 60),
    questions,
    answers: { correct: [], wrong: [] },
  };
}

function adaptSpeakDebate(payload: AnyTaskPayload): SpeakDebateTask {
  const debateContext = arrayValue(payload.dialogue_context).map((raw) => ({
    role: textValue(raw.role),
    text: textValue(raw.text),
    speaker: (textValue(raw.speaker) === "learner" ? "learner" : "ai") as "ai" | "learner",
  }));
  return {
    ...baseFields(payload),
    widget: "speak_debate",
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: speakingDuration(payload, 60),
    debateContext,
    prompts: speakingPrompts(payload),
    sampleResponses: speakingSamples(payload),
    answers: { correct: [], wrong: [] },
  };
}

/** Reference retell shown as "Model response" after submit (mirrors backend contract fields). */
export function resolveListenRetellModelAnswer(payload: AnyTaskPayload): string {
  const audioScript = textValue(payload.audio_script);
  const samples = firstStringArray(payload.sample_responses, payload.sample_answers);
  const fallbackSample = textValue(payload.sample_response);
  const allSamples = samples.length > 0 ? samples : fallbackSample ? [fallbackSample] : [];
  const passage = textValue(payload.passage_to_retell);
  const readAloud = textValue(payload.text_to_read_aloud);
  const distinctReadAloud =
    readAloud && readAloud !== audioScript ? readAloud : "";
  return passage || allSamples[0] || distinctReadAloud || "";
}

function adaptListenRetell(payload: AnyTaskPayload): ListenRetellTask {
  const modelAnswer = resolveListenRetellModelAnswer(payload);
  const fallbackPrompt = textValue(payload.speaking_prompt) || textValue(payload.prompt);
  const prompts = speakingPrompts(payload);
  const allPrompts =
    prompts.length > 0 ? prompts : fallbackPrompt ? [fallbackPrompt] : [];
  return {
    ...baseFields(payload),
    widget: "listen_retell",
    responseMode: "spoken",
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    passageToRetell: modelAnswer,
    prompts: allPrompts,
    sampleResponses: modelAnswer ? [modelAnswer] : speakingSamples(payload),
    answers: { correct: [], wrong: [] },
  };
}

// ── Speaking (pronunciation) family ─────────────────────────────────────────
function adaptReadAloud(payload: AnyTaskPayload): ReadAloudTask {
  return {
    ...baseFields(payload),
    widget: "read_aloud",
    textToReadAloud:
      textValue(payload.text_to_read_aloud) ||
      textValue(payload.passage) ||
      textValue(payload.primary_text),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    speakingDurationSeconds: numberValue(payload.speaking_duration_seconds) || 45,
    answers: { correct: [], wrong: [] },
  };
}

function adaptListenShadow(payload: AnyTaskPayload): ListenShadowTask {
  return {
    ...baseFields(payload),
    widget: "listen_shadow",
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    textToShadow:
      textValue(payload.text_to_read_aloud) ||
      textValue(payload.passage_to_retell) ||
      textValue(payload.audio_script),
    answers: { correct: [], wrong: [] },
  };
}

// ── Tail (tfng / structure / error correction / error spotting) ─────────────
function adaptReadTfng(payload: AnyTaskPayload): ReadTfngTask {
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    prompt: textValue(raw.prompt),
    correctAnswer: textValue(raw.correct_answer) as "True" | "False" | "Not Given",
    explanation: textValue(raw.explanation),
  }));
  return {
    ...baseFields(payload),
    widget: "read_tfng",
    passageTitle: textValue(payload.passage_title) || "Passage",
    passage: textValue(payload.passage),
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: {}, wrong: {} },
  };
}

function adaptReadStructure(payload: AnyTaskPayload): ReadStructureTask {
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    label: textValue(raw.label) || undefined,
    paragraph: textValue(raw.paragraph),
    correctAnswer: textValue(raw.correct_answer),
    explanation: textValue(raw.explanation),
  }));
  return {
    ...baseFields(payload),
    widget: "read_structure",
    passageTitle: textValue(payload.passage_title) || "Passage",
    grammarRule: grammarRule(payload),
    structureLabels: stringArray(payload.structure_labels),
    items,
    answers: { correct: {}, wrong: {} },
  };
}

function adaptErrorCorrection(payload: AnyTaskPayload): ErrorCorrectionTask {
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    incorrectSentence: textValue(raw.incorrect_sentence) || textValue(raw.prompt),
    sampleAnswer: textValue(raw.sample_answer),
    watchHints: stringArray(raw.watch_hints),
  }));
  return {
    ...baseFields(payload),
    widget: "error_correction",
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: [], wrong: [] },
  };
}

function adaptErrorSpotting(payload: AnyTaskPayload): ErrorSpottingTask {
  const sentences = arrayValue(payload.sentences).map((raw, index) => {
    const tokens = arrayValue(raw.tokens).map((token) => ({
      tokenId: textValue(token.token_id),
      text: textValue(token.text),
      isError: Boolean(token.is_error),
    }));
    const error = (raw.error && typeof raw.error === "object" ? raw.error : {}) as Record<string, unknown>;
    return {
      sentenceId: textValue(raw.sentence_id) || `s_${index + 1}`,
      tokens,
      error: {
        tokenId: textValue(error.token_id),
        incorrectPhrase: textValue(error.incorrect_phrase),
        correction: textValue(error.correction),
        rule: textValue(error.rule),
        explanation: textValue(error.explanation),
      },
    };
  });
  return {
    ...baseFields(payload),
    widget: "error_spotting",
    passageTitle: textValue(payload.passage_title) || "Passage",
    grammarRule: grammarRule(payload),
    sentences,
    answers: { correct: [], wrong: [] },
  };
}

// ── Dictation family ────────────────────────────────────────────────────────
function dictationCorrectAnswer(
  raw: Record<string, unknown>,
  index: number,
  targetWords: string[],
): string {
  const prompt = textValue(raw.prompt);
  let answer = textValue(raw.correct_answer) || textValue(raw.sample_answer);
  if (!answer && index < targetWords.length) {
    answer = targetWords[index] ?? "";
  }
  if (!answer) return "";
  if (!prompt.includes("___")) return answer;
  const parts = prompt.split("___").map((part) => part.trim()).filter(Boolean);
  if (parts.length > 0 && parts.every((part) => answer.toLowerCase().includes(part.toLowerCase()))) {
    return answer;
  }
  return prompt.replace("___", answer.trim()).trim();
}

function adaptListenDictation(payload: AnyTaskPayload): ListenDictationTask {
  const targetWords = stringArray(payload.target_words);
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    prompt: textValue(raw.prompt),
    correctAnswer: dictationCorrectAnswer(raw, index, targetWords),
    explanation: textValue(raw.explanation),
  }));
  return {
    ...baseFields(payload),
    widget: "listen_dictation",
    audioGenre: textValue(payload.audio_genre) || "Audio",
    audioScript: textValue(payload.audio_script),
    audioUrl: textValue(payload.audio_url) || null,
    audioDurationSeconds: numberValue(payload.audio_duration_seconds),
    grammarRule: grammarRule(payload),
    targetWords: stringArray(payload.target_words),
    items,
    answers: { correct: {}, wrong: {} },
  };
}

// ── Transform family ────────────────────────────────────────────────────────
function adaptSentenceTransform(payload: AnyTaskPayload): SentenceTransformTask {
  const items = arrayValue(payload.items).map((raw, index) => ({
    itemId: textValue(raw.item_id) || `item_${index + 1}`,
    sourceSentence: textValue(raw.source_sentence) || textValue(raw.prompt),
    sampleAnswer: textValue(raw.sample_answer),
    watchHints: stringArray(raw.watch_hints),
  }));
  return {
    ...baseFields(payload),
    widget: "sentence_transform",
    grammarRule: grammarRule(payload),
    items,
    answers: { correct: [], wrong: [] },
  };
}

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
