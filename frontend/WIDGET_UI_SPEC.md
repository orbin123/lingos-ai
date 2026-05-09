# LingosAI — Widget UI Specification

> **Why this doc exists.** The backend produces 28 different task types,
> but they all render through just **8 generic widgets**. This doc tells
> you exactly what data each widget receives, what it shows, what the user
> does, and what gets sent back to the backend. Build the widgets once;
> let the LLM-generated content flow through them.

---

## Table of contents

1. [Big-picture data flow](#big-picture-data-flow)
2. [Common envelope (every task carries this)](#common-envelope-every-task-carries-this)
3. [The 8 widgets — full I/O spec](#the-8-widgets--full-io-spec)
   - [Widget 1: `mcq`](#widget-1-mcq)
   - [Widget 2: `fill_in_blanks`](#widget-2-fill_in_blanks)
   - [Widget 3: `open_text`](#widget-3-open_text)
   - [Widget 4: `timed_text`](#widget-4-timed_text)
   - [Widget 5: `structured_essay`](#widget-5-structured_essay)
   - [Widget 6: `speak_and_record`](#widget-6-speak_and_record)
   - [Widget 7: `listen_and_respond`](#widget-7-listen_and_respond)
   - [Widget 8: `storyboard`](#widget-8-storyboard)
4. [The 28 task → widget mapping](#the-28-task--widget-mapping)
5. [Build order recommendation](#build-order-recommendation)

---

## Big-picture data flow

```
┌─────────────────┐    GET task     ┌──────────────────────┐
│   Frontend      │ ──────────────▶ │   Backend            │
│   (Next.js)     │                 │   /api/tasks/:id     │
│                 │ ◀────────────── │                      │
└─────────────────┘   task JSON     └──────────────────────┘
        │
        │ 1. Read task.widget → pick component
        │ 2. Render component(task.content)
        │ 3. User completes the task
        │ 4. Build response object (per-widget shape)
        │
        ▼
┌─────────────────┐  POST response  ┌──────────────────────┐
│   Frontend      │ ──────────────▶ │   Backend            │
│                 │                 │   /api/responses     │
└─────────────────┘                 └──────────────────────┘
                                            │
                                            ▼
                                    Evaluator → Feedback
                                    → return scores + feedback
```

**Key principle:** the widget never needs to know what sub-skill or topic
the task belongs to. It only reads the widget-specific fields and the
common envelope. The LLM-generated content is what makes the task feel
topic-aware.

---

## Common envelope (every task carries this)

Every task object the backend sends has these fields **regardless of widget**.
Build a small `<TaskHeader />` component once and reuse it.

```ts
interface TaskEnvelope {
  // ─── Common ─────────────────────────────────────────
  task_intro: string                  // 1–2 sentence friendly intro
  estimated_time_minutes: number      // 1–30
  widget: WidgetType                  // which renderer to use
  topic_id: string                    // "1:1" — matches curriculum JSON
  topic_name: string                  // "Present Simple Tense — Basics"
  sub_skill: SubSkill                 // "grammar" | "vocabulary" | ...
  sub_level: number                   // 1..10
  activity: "read" | "write" | "listen" | "speak"

  // ─── Widget-specific fields (see each widget below) ─
  // ...
}

type WidgetType =
  | "mcq"
  | "fill_in_blanks"
  | "open_text"
  | "timed_text"
  | "structured_essay"
  | "speak_and_record"
  | "listen_and_respond"
  | "storyboard"
```

**`<TaskHeader />`** shows: `topic_name`, `task_intro`, a small
"sub_skill • activity • ~N min" pill. Same on every screen.

---

## The 8 widgets — full I/O spec

### Widget 1: `mcq`

**Used by 4 task types.** Most common widget, also the simplest.

#### What the widget receives (input from backend)

```ts
interface MCQTask extends TaskEnvelope {
  widget: "mcq"
  instructions: string                         // shown above the questions
  items: Array<{
    item_id: string                            // stable ID for response keying
    prompt: string                             // the question text
    options: [string, string, string, string]  // exactly 4 options
    correct_index: 0 | 1 | 2 | 3               // for grading (DO NOT show)
    explanation: string                        // shown after submit only
  }>

  // Some MCQ variants carry extra context — render only if present:
  target_words?: string[]                      // VocabularyReadTask
  question_types_used?: string[]               // ComprehensionReadTask
  pattern_explained?: string                   // PronunciationWriteTask
  tone_concepts_taught?: string[]              // ToneReadTask
}
```

#### What the user sees

| Section          | Content                                                   |
| ---------------- | --------------------------------------------------------- |
| Header           | `<TaskHeader />`                                          |
| Instructions     | `instructions` text block                                 |
| (Optional) Chips | If `target_words` / `tone_concepts_taught` exist, show as small pills below instructions |
| Questions        | One card per `items[i]` — each card shows `prompt` + 4 buttons |
| Submit button    | Disabled until every item has an answer                   |
| After submit     | Per-item ✔/✗ + `explanation` reveal                       |

#### What the user does

Tap one of 4 option buttons per question. Move to next question (auto-advance is fine; or all visible at once — either works).

#### What the widget sends back (response payload)

```ts
interface MCQResponse {
  task_id: string                              // from URL, not from task
  widget: "mcq"
  answers: Array<{
    item_id: string
    selected_index: 0 | 1 | 2 | 3
  }>
  time_spent_seconds: number
}
```

#### Notes for the dev

- Never reveal `correct_index` or `explanation` until submit
- Keyboard support: 1/2/3/4 keys to pick, Enter to advance
- Mobile: stack options vertically; on tablet/desktop you can do 2x2 grid
- The grader is rule-based — just exact-match `selected_index === correct_index`

---

### Widget 2: `fill_in_blanks`

**Used by 1 task type** (`GrammarReadTask`). The most "schoolbook" widget.

#### What the widget receives

```ts
interface FillInBlanksTask extends TaskEnvelope {
  widget: "fill_in_blanks"
  instructions: string
  passage: string | null                       // optional context text — show if present
  grammar_rule_explained: string               // 1–2 sentences explaining the rule
  items: Array<{
    item_id: string
    sentence_with_blank: string                // contains literal "___" where blank goes
    correct_answer: string                     // for grading
    distractors: string[]                      // optional MCQ options (may be empty)
    explanation: string                        // shown after submit
  }>
}
```

#### What the user sees

| Section         | Content                                                      |
| --------------- | ------------------------------------------------------------ |
| Header          | `<TaskHeader />`                                             |
| Rule callout    | `grammar_rule_explained` in a soft tinted box                |
| Passage         | `passage` rendered as paragraph (skip if null)               |
| Items           | Each item shows `sentence_with_blank` with the `___` replaced by an inline input (or 4-button MCQ if `distractors.length === 3`) |
| Submit & review | Same pattern as MCQ                                          |

#### What the user does

If `distractors` is non-empty → tap one of the buttons (acts like inline MCQ).
If `distractors` is empty → type the answer in the inline input.

> **Practical advice:** For sub-levels 1–4 always render with distractors (MCQ-style) — it's less frustrating for beginners. For 5–10 you can render as typed input. The backend may send distractors regardless, so you choose render mode based on `sub_level`.

#### What the widget sends back

```ts
interface FillInBlanksResponse {
  task_id: string
  widget: "fill_in_blanks"
  answers: Array<{
    item_id: string
    user_answer: string                        // typed text OR selected option text
    selected_index?: number                    // present if rendered as MCQ
  }>
  time_spent_seconds: number
}
```

#### Notes

- Inline input width should auto-grow with the answer
- Trim whitespace, lowercase before client-side hint comparison; backend does the same on grading
- After submit, color the input green (correct) or red (wrong) and show `correct_answer` faded next to wrong ones

---

### Widget 3: `open_text`

**Used by 5 task types.** A list of prompts the user answers in free-form.

#### What the widget receives

```ts
interface OpenTextTask extends TaskEnvelope {
  widget: "open_text"
  instructions: string
  items: Array<{
    item_id: string
    prompt: string                             // the question
    sample_answer: string                      // shown only after submit
    answer_hints: string[]                     // shown only after submit
  }>

  // Variant-specific extras (render conditionally):
  grammar_rule_explained?: string              // GrammarWriteTask
  common_mistakes?: string[]                   // GrammarWriteTask, ToneWriteTask
  target_words?: string[]                      // VocabularyWriteTask
  minimum_target_words_used?: number           // VocabularyWriteTask
  passage?: string                             // ExpressionReadTask
  structure_pattern_taught?: string            // ExpressionReadTask
  source_passage?: string | null               // ComprehensionWriteTask
  source_audio_script?: string | null          // ComprehensionWriteTask
  source_audio_url?: string | null             // ComprehensionWriteTask
  target_register?: string                     // ToneWriteTask
}
```

#### What the user sees

| Section         | Content                                                      |
| --------------- | ------------------------------------------------------------ |
| Header          | `<TaskHeader />`                                             |
| Context block   | If any of `passage` / `source_passage` / `source_audio_url` exists → show it first (passage as text, audio as audio player) |
| Helper hints    | If `target_words` exists → show as removable chips (so user can track which words they've used). If `grammar_rule_explained` exists → show as soft callout. |
| Items           | Each item: prompt text + a textarea below it                |
| Submit          | Disabled until every textarea has at least 5 chars          |
| After submit    | Per-item: user's answer • `sample_answer` • `answer_hints`  |

#### What the user does

Reads the prompt → types into each textarea → submits.

#### What the widget sends back

```ts
interface OpenTextResponse {
  task_id: string
  widget: "open_text"
  answers: Array<{
    item_id: string
    user_answer: string                        // freeform text
  }>
  time_spent_seconds: number
}
```

#### Notes

- Auto-resize textareas, min 3 rows
- For `target_words`: track which words appear in the user's answers (case-insensitive substring match). Cross out chips as they're used. Don't gate submit on this — let the evaluator decide.
- For comprehension variants: lock the audio player after first complete listen if you want to test memory; otherwise allow re-listen.

---

### Widget 4: `timed_text`

**Used by 1 task type** (`FluencyWriteTask`). Like `open_text` but with one prompt and a hard timer.

#### What the widget receives

```ts
interface TimedTextTask extends TaskEnvelope {
  widget: "timed_text"
  instructions: string
  writing_prompt: string                       // the single topic
  time_limit_seconds: number                   // 60–900
  minimum_word_count: number
  target_word_count: number
  no_editing_allowed: boolean                  // if true: disable backspace/delete after 3s
  sample_response: string                      // shown after submit only
}
```

#### What the user sees

| Section         | Content                                                  |
| --------------- | -------------------------------------------------------- |
| Header          | `<TaskHeader />`                                         |
| Big prompt card | `writing_prompt` styled large                            |
| Counters        | "MM:SS remaining" • "current word count / target"        |
| Textarea        | One large textarea, fills most of the screen             |
| Submit early    | "Done early" button (still records `time_spent`)         |
| Auto-submit     | When timer hits 0, lock textarea + submit automatically  |
| After submit    | User's answer • `sample_response` • word count & time stats |

#### What the user does

Reads the prompt → starts typing immediately → keeps writing till timer ends.

#### What the widget sends back

```ts
interface TimedTextResponse {
  task_id: string
  widget: "timed_text"
  user_answer: string
  word_count: number
  time_spent_seconds: number                   // ≤ time_limit_seconds
  hit_target_word_count: boolean
}
```

#### Notes

- **Disable backspace/delete after 3 seconds of typing** if `no_editing_allowed` is true. This is the whole point of the widget — train flow over polish. Track via `keyDown` handler.
- Show timer as a calm countdown; flash red only at last 30s
- Word count: simple `text.trim().split(/\s+/).filter(Boolean).length`
- Disable browser autocorrect — autocorrect undoes the no-editing rule

---

### Widget 5: `structured_essay`

**Used by 1 task type** (`ExpressionWriteTask`). The biggest single widget.

#### What the widget receives

```ts
interface StructuredEssayTask extends TaskEnvelope {
  widget: "structured_essay"
  instructions: string
  overall_topic: string
  structure_pattern: string                    // "intro-body-conclusion" etc.
  total_target_words: number
  sections: Array<{
    section_id: string
    section_name:
      | "introduction" | "background" | "main_point"
      | "supporting_detail" | "counter_point" | "conclusion"
    section_prompt: string
    minimum_word_count: number
    sample_text: string                        // shown after submit only
  }>
}
```

#### What the user sees

| Section         | Content                                                  |
| --------------- | -------------------------------------------------------- |
| Header          | `<TaskHeader />`                                         |
| Topic banner    | `overall_topic` with `structure_pattern` as subtitle     |
| Progress strip  | Visual indicator: section 1 of 4, total words X / target |
| Section cards   | One scrollable card per section. Each card: `section_name` heading, `section_prompt`, textarea, per-section word count |
| Section nav     | Prev / Next buttons OR collapsing accordion              |
| Submit          | Enabled only when every section meets `minimum_word_count` |
| After submit    | Per-section: user's text + `sample_text` for comparison  |

#### What the user does

Writes each section in order. Can scroll back to edit.

#### What the widget sends back

```ts
interface StructuredEssayResponse {
  task_id: string
  widget: "structured_essay"
  sections: Array<{
    section_id: string
    user_answer: string
    word_count: number
  }>
  total_word_count: number
  time_spent_seconds: number
}
```

#### Notes

- Don't auto-submit — essays need re-reading
- Per-section minimum is a soft guide; show "X words to go" but allow submit if total > total_target_words even if one section is short. The evaluator weighs structure separately.
- This is the only widget where saving drafts mid-task makes sense for v2; for MVP just keep state in React.

---

### Widget 6: `speak_and_record`

**Used by 11 task types.** Most-used speak widget. Has the most variants.

#### What the widget receives

```ts
interface SpeakAndRecordTask extends TaskEnvelope {
  widget: "speak_and_record"
  instructions: string
  speaking_duration_seconds: number            // hard cap on recording length

  // ─── Variant A: list of prompts (Grammar, Pronunciation, Vocabulary speak)
  speaking_prompts?: string[]
  sample_responses?: string[]
  speaking_items?: string[]                    // for pronunciation: words/phrases
  target_pattern?: string                      // pron variants
  reference_audio_url?: string | null          // pron — user can hear correct version
  use_azure_scoring?: boolean                  // pron variants

  // ─── Variant B: single prompt (Vocabulary speak, Fluency speak, Comprehension speak)
  speaking_prompt?: string
  sample_response?: string
  preparation_seconds?: number                 // fluency speak
  fluency_focus?: string                       // fluency speak
  sample_talking_points?: string[]             // shown ONLY after submit
  target_words?: string[]                      // vocab speak
  minimum_words_used?: number                  // vocab speak

  // ─── Variant C: read-aloud (Pronunciation read, Fluency read)
  text_to_read_aloud?: string                  // pron read
  target_sounds_or_patterns?: string[]
  expected_difficult_words?: string[]
  passage?: string                             // fluency read (long form)
  word_count?: number                          // fluency read
  target_wpm?: number                          // fluency read
  time_limit_seconds?: number                  // fluency read

  // ─── Variant D: retell from audio (Comprehension speak)
  source_audio_script?: string
  source_audio_url?: string | null
  retelling_prompt?: string
  key_points_expected?: string[]               // shown ONLY after submit

  // ─── Variant E: roleplay (Tone speak)
  scenario_description?: string
  target_tone?: string
  turns?: Array<{
    turn_id: string
    speaker: "ai" | "user"
    ai_line: string | null
    expected_user_tone: string | null
  }>
  sample_user_responses?: string[]
}
```

> Yes, this widget has many optional fields. **You don't need branches** — render whichever fields are present. Most variants share the same core: text or audio → mic button → recording.

#### What the user sees (5 sub-modes)

**Mode A — multi-prompt list** (e.g. grammar speak, pron drill):
- Show each prompt or item in a card; one mic button per item; user records each separately.

**Mode B — single prompt** (e.g. fluency speak, vocab speak):
- One big prompt card, one mic button. If `preparation_seconds > 0`, show a prep countdown before mic activates. If `target_words` exists, show as chips.

**Mode C — read-aloud** (pron read, fluency read):
- Show `text_to_read_aloud` or `passage` as the main content, mic button below. For fluency read, show countdown timer based on `time_limit_seconds`.

**Mode D — retell from audio** (comprehension speak):
- Audio player at top, user listens (maybe lock to one playthrough), then `retelling_prompt` appears, then mic button.

**Mode E — roleplay** (tone speak):
- Conversation-style: AI lines play as TTS audio (synthesized from `ai_line`), user records reply for each `speaker: "user"` turn. Show `target_tone` as a banner above the conversation.

#### Common UI elements (all modes)

| Element             | Behavior                                                  |
| ------------------- | --------------------------------------------------------- |
| Mic button          | Big circle. Tap to start, tap to stop. Visual waveform/pulse while recording |
| Recording timer     | Counts up; auto-stops at `speaking_duration_seconds`       |
| Reference audio     | If `reference_audio_url` exists, "🔊 Hear correct" button |
| Re-record           | After recording, allow user to re-record (max 3 attempts) |
| Submit              | Sends recording(s); disables mic                          |
| After submit        | Show transcript (from STT), sample_response/sample_responses, key_points_expected, etc. |

#### What the user does

Speaks into the mic. May re-record. Submits.

#### What the widget sends back

```ts
interface SpeakAndRecordResponse {
  task_id: string
  widget: "speak_and_record"
  recordings: Array<{
    item_id?: string                           // for multi-prompt modes
    turn_id?: string                           // for roleplay
    audio_blob_url: string                     // uploaded blob URL
    duration_seconds: number
    attempt_number: number                     // 1–3
  }>
  time_spent_seconds: number
}
```

#### Notes

- **MediaRecorder API** with mime type `audio/webm;codecs=opus` for Chrome/Firefox; Safari needs `audio/mp4`. Detect via `MediaRecorder.isTypeSupported(...)`.
- Upload blobs to your blob storage (S3 or local for dev), get a URL, put that URL in the response.
- Permissions: ask for mic on the **first speak task** of the session, not on app load.
- Show an obvious "Microphone permission needed" empty state with a "Grant permission" button if denied.
- For pron tasks where `use_azure_scoring` is true, the backend will return phoneme-level scores. UI just sends the audio; it doesn't decide scoring.
- For roleplay (mode E), use TTS to play AI lines; otherwise the conversation feels broken. Cache the TTS audio per turn.

---

### Widget 7: `listen_and_respond`

**Used by 7 task types.** A composite widget: audio player + an inner widget.

#### What the widget receives

```ts
interface ListenAndRespondTask extends TaskEnvelope {
  widget: "listen_and_respond"
  instructions: string
  audio_script: string                         // text the TTS spoke
  audio_url: string | null                     // populated by backend before delivery
  inner_widget: "mcq" | "fill_in_blanks" | "open_text" | "speak_and_record"

  // ─── Inner widget content (one of these will be present):
  items?: MCQTask["items"] | OpenTextTask["items"]   // for inner mcq / open_text
  text_to_shadow?: string                      // for inner speak_and_record (Fluency listen)
  speed?: "slow" | "natural" | "fast"          // shadowing
  delay_seconds?: number                       // shadowing
  minimum_match_percentage?: number            // shadowing

  // ─── Variant-specific extras
  target_words_in_audio?: string[]             // vocab listen
  target_pattern?: string                      // pron listen
  audio_genre?: string                         // comprehension listen
  voice_style_hint?: string                    // tone listen
  structure_to_identify?: string               // expression listen
}
```

#### What the user sees

| Stage                | Content                                                  |
| -------------------- | -------------------------------------------------------- |
| Stage 1: Listening   | Big audio player. Play, pause, scrub. Optional "Show transcript" toggle (off by default). User listens. |
| Stage 2: Inner task  | After first complete play (or skip-button), the inner widget appears below the player. |
| Stage 3: Submit      | Submits the inner widget's response, plus listen analytics |

#### What the user does

Plays audio (1+ times depending on policy) → completes inner widget → submits.

#### What the widget sends back

```ts
interface ListenAndRespondResponse {
  task_id: string
  widget: "listen_and_respond"
  listen_analytics: {
    play_count: number                         // how many times they hit play
    total_listen_seconds: number
    transcript_revealed: boolean
  }
  inner_response:                              // shape matches the inner widget
    | MCQResponse
    | FillInBlanksResponse
    | OpenTextResponse
    | SpeakAndRecordResponse
  time_spent_seconds: number
}
```

#### Notes

- **Reuse the inner-widget components.** Don't rebuild MCQ inside listen_and_respond. Just import and pass props.
- For shadowing tasks (`inner_widget: "speak_and_record"` + `text_to_shadow`): the inner UI needs simultaneous play + record. Start playback, mic listens at the same time with `delay_seconds` offset. This is the most complex sub-mode.
- Limit replays to 2 for comprehension-style listening; unlimited for pronunciation-listen tasks.
- Auto-grant mic permission upgrade only when the inner widget needs it.

---

### Widget 8: `storyboard`

**Used by 1 task type** (`ExpressionSpeakTask`). The most distinctive widget.

#### What the widget receives

```ts
interface StoryboardTask extends TaskEnvelope {
  widget: "storyboard"
  instructions: string
  overall_story_premise: string
  narrative_pattern: string                    // "beginning-middle-end" etc.
  speaking_duration_seconds: number
  sample_narration: string                     // shown after submit only
  scenes: Array<{
    scene_id: string
    scene_number: number                       // 1..6
    image_prompt: string                       // (debug only — don't show)
    image_url: string | null                   // populated by ImageGen backend
    narration_focus: string                    // what to talk about for this scene
  }>
}
```

#### What the user sees

| Section          | Content                                                  |
| ---------------- | -------------------------------------------------------- |
| Header           | `<TaskHeader />`                                         |
| Premise banner   | `overall_story_premise` + `narrative_pattern` chip       |
| Scene strip      | Horizontal scroll: 3–6 image cards. Each card shows the AI-generated image and below it `narration_focus` as a small caption |
| Active scene     | Highlight current scene (light glow); others dimmed     |
| Mic button       | Single mic button below the strip                        |
| Recording timer  | Counts up to `speaking_duration_seconds`                 |
| Scene advance    | "Next scene" button to manually advance, OR auto-advance based on `speaking_duration_seconds / scenes.length` |
| Submit           | After timer or "Done"                                    |
| After submit     | Transcript • `sample_narration`                          |

#### What the user does

Looks at scene 1 → starts narrating → moves to scene 2 (manually or auto) → continues until end → submits.

#### What the widget sends back

```ts
interface StoryboardResponse {
  task_id: string
  widget: "storyboard"
  audio_blob_url: string                       // single continuous recording
  scene_timestamps: Array<{
    scene_id: string
    started_at_seconds: number
    ended_at_seconds: number
  }>
  duration_seconds: number
  time_spent_seconds: number
}
```

#### Notes

- `image_url` may be `null` while ImageGen finishes. Show skeleton loaders. Poll the task or use SSE to get the URL when ready. **Don't block the user from starting** if scene 1's image is loaded — the rest can lazy-load.
- Single continuous recording works best (one audio blob, with timestamps). Chunked per-scene recording is hardest to grade and hardest for the learner to feel flow.
- For MVP: skip auto-advance; let the user tap "Next" between scenes. Auto-advance is a v2 polish.

---

## The 28 task → widget mapping

Quick reference for "which widget renders which task". Use this to pick what to build first.

| #   | Task class               | Widget                | Variant notes                   |
| --- | ------------------------ | --------------------- | ------------------------------- |
| 1   | `GrammarReadTask`        | `fill_in_blanks`      | with passage + rule callout     |
| 2   | `GrammarWriteTask`       | `open_text`           | shows `grammar_rule_explained`  |
| 3   | `GrammarListenTask`      | `listen_and_respond`  | inner = `mcq`                   |
| 4   | `GrammarSpeakTask`       | `speak_and_record`    | mode A (multi-prompt list)      |
| 5   | `VocabularyReadTask`     | `mcq`                 | shows `target_words` chips      |
| 6   | `VocabularyWriteTask`    | `open_text`           | shows `target_words` chips      |
| 7   | `VocabularyListenTask`   | `listen_and_respond`  | inner = `mcq`                   |
| 8   | `VocabularySpeakTask`    | `speak_and_record`    | mode B (single prompt)          |
| 9   | `PronunciationReadTask`  | `speak_and_record`    | mode C (read aloud, Azure)      |
| 10  | `PronunciationWriteTask` | `mcq`                 | phonetic-awareness MCQs         |
| 11  | `PronunciationListenTask`| `listen_and_respond`  | inner = `mcq`                   |
| 12  | `PronunciationSpeakTask` | `speak_and_record`    | mode A + reference audio        |
| 13  | `FluencyReadTask`        | `speak_and_record`    | mode C (timed read-aloud)       |
| 14  | `FluencyWriteTask`       | `timed_text`          | the only timed_text task        |
| 15  | `FluencyListenTask`      | `listen_and_respond`  | inner = `speak_and_record` (shadow) |
| 16  | `FluencySpeakTask`       | `speak_and_record`    | mode B + prep timer             |
| 17  | `ExpressionReadTask`     | `open_text`           | shows passage + structure       |
| 18  | `ExpressionWriteTask`    | `structured_essay`    | the only structured_essay task  |
| 19  | `ExpressionListenTask`   | `listen_and_respond`  | inner = `open_text`             |
| 20  | `ExpressionSpeakTask`    | `storyboard`          | the only storyboard task        |
| 21  | `ComprehensionReadTask`  | `mcq`                 | with passage above              |
| 22  | `ComprehensionWriteTask` | `open_text`           | with passage OR audio source    |
| 23  | `ComprehensionListenTask`| `listen_and_respond`  | inner = `mcq`                   |
| 24  | `ComprehensionSpeakTask` | `speak_and_record`    | mode D (retell from audio)      |
| 25  | `ToneReadTask`           | `mcq`                 | tone-classification MCQs        |
| 26  | `ToneWriteTask`          | `open_text`           | rewrite-in-target-register      |
| 27  | `ToneListenTask`         | `listen_and_respond`  | inner = `mcq`                   |
| 28  | `ToneSpeakTask`          | `speak_and_record`    | mode E (roleplay turns)         |

### Coverage by widget (sorted by impact)

| Widget               | # tasks | Build effort | Build first? |
| -------------------- | ------- | ------------ | ------------ |
| `speak_and_record`   | 11      | High         | NO — too complex for first |
| `mcq`                | 4       | Low          | **YES — start here** |
| `listen_and_respond` | 7       | Medium       | After mcq + speak  |
| `open_text`          | 5       | Low          | **YES — second**   |
| `fill_in_blanks`     | 1       | Low          | After mcq          |
| `timed_text`         | 1       | Medium       | Later              |
| `structured_essay`   | 1       | Medium       | Later              |
| `storyboard`         | 1       | High         | Last (needs ImageGen wiring) |

---

## Build order recommendation

You should **not** build all 8 widgets at once. Vertical-slice instead:

### Phase 1 — Prove the model (1 widget)
Build `mcq` only. Wire it to `VocabularyReadTask` (template #5). Run end-to-end:
curriculum entry → task generator → MCQ JSON → frontend renders → user submits → response saves.
This unlocks **4 task types** as soon as it works.

### Phase 2 — Cover read+write (3 widgets)
Add `open_text` and `fill_in_blanks`. Now you cover **10 task types** (all read + write tasks except expression-write, fluency-write).

### Phase 3 — Cover listen (1 widget that wraps 3 inner widgets)
Build `listen_and_respond` reusing the 3 inner widgets you already have (mcq, fill_in_blanks, open_text). Skip the speak inner mode for now. This adds **5 more task types** (listen tasks except fluency-listen which needs shadowing).

### Phase 4 — The big one: speak (1 widget, 5 sub-modes)
Build `speak_and_record` mode B (single prompt) first — it's the simplest. Then mode A, C, D, E as you need them. STT integration is the hard part. Whisper-only is fine for MVP; Azure pronunciation scoring is a Phase 5+ concern.

### Phase 5 — Edge cases
Build `timed_text`, `structured_essay`, `storyboard`. These are one-off widgets — only build when you have a learner who's actually reached those topics in the curriculum. Don't pre-build.

---

## Final reminder

The widget never knows the topic. It just renders fields. The LLM-generated
content is what makes Day 1 (Present Simple) and Day 8 (Articles) feel
different to the learner — same widget, different prompts and items.

**Build 8 widgets. Render 28 task types. Learn 168 (or 336) topics.**
That's the whole architecture in one line.
