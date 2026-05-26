# Curriculum Day Authoring Reference

Planning guide for writing `DaySource` objects in `backend/app/data/courses/curriculum/source_24w.py`.

Use this when authoring all **24 weeks × 7 days = 168 days**. Only **Week 1 / Day 1** is fully authored today; everything else is blank `DaySource()`.

---

## 1. What a day controls

Each populated `DaySource` drives three runtime systems:

| System | Source field | Agent / code |
|--------|--------------|--------------|
| **Teaching chat** (before practice) | `title`, `description`, `teacher_agent_behaviour` | Teacher LLM (`app/ai/agents/teacher.py`) |
| **Practice task order & types** | `task_archetypes_used` | `SessionService.start_session()` reads file source instead of planner |
| **Per-task content hints** | `task_specs` (one dict per archetype, same order) | Task Generator LLM + TTS (`LLMTaskGenerator`) |
| **Scoring nudges** (optional) | `evaluator_overrides`, `feedback_overrides` | Evaluator + Feedback LLMs |

When a day has a `title` **or** `task_archetypes_used`, it is **file-authored**. The session uses your archetype list **exactly** (filtered only by the learner’s disabled activity preferences), **not** the DB planner’s `mandatory_activities` / `suggested_archetypes`.

---

## 2. 24-week skeleton

Structure enforced by tests (`source_24w.py` header):

```
6 cycles × 4 themes = 24 weeks
Theme order per cycle: grammar → communication → vocabulary → confidence
7 days per week (Day 1 = Monday … Day 7 = Sunday in product copy)
```

| Cycle | Weeks | CEFR | Sub-level range | Label (in source) |
|-------|-------|------|-----------------|-------------------|
| 1 — Foundation | 1–4 | A1 | 1–2 | |
| 2 — Daily Life | 5–8 | A2 | 3–3 | |
| 3 — Functioning | 9–12 | B1 | 4–5 | |
| 4 — Connecting | 13–16 | B1+ | 5–6 | |
| 5 — Reasoning | 17–20 | B2 | 6–7 | |
| 6 — Polishing | 21–24 | C1 | 8–8 | |

| Week | Theme | CEFR |
|------|-------|------|
| 1, 5, 9, 13, 17, 21 | grammar | see cycle |
| 2, 6, 10, 14, 18, 22 | communication | |
| 3, 7, 11, 15, 19, 23 | vocabulary | |
| 4, 8, 12, 16, 20, 24 | confidence | |

**Day IDs:** `day_24_WW_DD` (e.g. Week 3 Day 5 → `day_24_03_05`).

---

## 3. `DaySource` schema (copy-paste template)

```python
DaySource(
    title="Short lesson title — grammar point or skill focus",
    description=(
        "2–4 sentences: what the learner will understand and be able to do "
        "by the end of teaching + practice. Becomes `explanation_brief` "
        "for task generation and `lesson_description` for the teacher."
    ),
    teacher_agent_behaviour=(
        "TURN 1 — Open: … Stop here.",
        "TURN 2 — … Stop here.",
        "TURN 3 — … Stop here.",
        "TURN 4 — Wrap-up: if the learner has shown the pattern at least once "
        "correctly across turns 2 and 3, ask exactly: Ready to try the practice task? "
        "Do not add any further explanation, review, or example.",
    ),
    task_archetypes_used=(
        "READ_…",      # activity 1
        "LISTEN_…",    # activity 2
        "WRITE_…",     # activity 3
        "SPEAK_…",     # activity 4
    ),
    task_specs=(
        {"topic_override": "…", "instructions_override": "…", …},
        {"topic_override": "…", "instructions_override": "…", "widget_requirements": "…"},
        {"topic_override": "…", "instructions_override": "…"},
        {"topic_override": "…", "instructions_override": "…", "widget_requirements": "…"},
    ),
    # Optional:
    evaluator_overrides={},   # passed to Evaluator LLM
    feedback_overrides={},    # passed to Feedback LLM
)
```

### Hard rules

1. **`len(task_specs) == len(task_archetypes_used)`** when `task_specs` is non-empty — or omit `task_specs` entirely (generator uses archetype + day topic only).
2. **Blank day** = `DaySource()` with no title and no archetypes → session cannot start for that day.
3. **`task_archetypes_used` order = delivery order** in chat (sequence 1, 2, 3, 4…).
4. Pick archetypes whose **CEFR range** covers the week’s level (see §5). Invalid IDs crash at import/lookup.
5. Week 1 Day 1 uses **4 tasks** (read → listen → write → speak). You can use **2–4** archetypes; match your teaching depth.

---

## 4. Theme → activity conventions

From `loader.py` — used when a day is **not** file-authored, but still guides which skills each theme emphasizes.

### Mandatory activities (if using planner fallback)

| Theme | Must include | Optional (when user wants 3–4 tasks/day) |
|-------|--------------|------------------------------------------|
| **grammar** | read, write | listen, speak |
| **communication** | write, speak | read, listen |
| **vocabulary** | read, write | listen, speak |
| **confidence** | listen, speak | read, write |

### Default archetype pools (CEFR-filtered)

Pick from these when choosing `task_archetypes_used`. First entry = default if using planner only.

**Grammar**

| Activity | Archetypes (simple → rich) |
|----------|----------------------------|
| read | `READ_CLOZE`, `READ_COMP_MCQ`, `READ_ERROR_SPOT` |
| write | `WRITE_OPEN_SENT`, `WRITE_SENT_TRANS`, `WRITE_ERROR_CORR`, `WRITE_VOICE_CONV`, `WRITE_PARA` |
| listen | `LISTEN_MCQ`, `LISTEN_CLOZE`, `LISTEN_DICTATION` |
| speak | `SPEAK_READ_ALOUD`, `SPEAK_TIMED` |

**Communication**

| Activity | Archetypes |
|----------|------------|
| read | `READ_COMP_MCQ`, `READ_TFNG`, `READ_STRUCTURE_ID` |
| write | `WRITE_SENT_TRANS`, `WRITE_EMAIL`, `WRITE_PARA`, `WRITE_PARAPHRASE`, `WRITE_BULLETS_TO_PARA`, `WRITE_IDEA_PARA` |
| listen | `LISTEN_MCQ`, `LISTEN_INFER`, `LISTEN_RETELL` |
| speak | `SPEAK_PIC_DESC`, `SPEAK_ROLEPLAY`, `SPEAK_INTERVIEW`, `SPEAK_OPINION` |

**Vocabulary**

| Activity | Archetypes |
|----------|------------|
| read | `READ_WORD_MATCH`, `READ_CONTEXT_MCQ` |
| write | `WRITE_SENT_TRANS`, `WRITE_WORD_UPGRADE`, `WRITE_PARA`, `WRITE_PARAPHRASE` |
| listen | `LISTEN_MCQ`, `LISTEN_DICTATION` |
| speak | `SPEAK_PIC_DESC`, `SPEAK_TIMED` |

**Confidence**

| Activity | Archetypes |
|----------|------------|
| read | `READ_COMP_MCQ`, `READ_TONE_ID` |
| write | `WRITE_SENT_TRANS`, `WRITE_TIMED` |
| listen | `LISTEN_SHADOW`, `LISTEN_MCQ`, `LISTEN_TONE` |
| speak | `SPEAK_READ_ALOUD`, `SPEAK_TIMED`, `SPEAK_PIC_DESC`, `SPEAK_SMALLTALK`, `SPEAK_PRESENT`, `SPEAK_DEBATE` |

---

## 5. Full archetype catalog

Source of truth: `backend/app/scoring/archetypes.py` (`ARCHETYPE_REGISTRY`).

**Not implemented:** `LISTEN_REG_MIS` (Listen for Register Mismatch) — do not use.

### Reading (8)

| ID | Name | Widget | Themes | CEFR | Description |
|----|------|--------|--------|------|-------------|
| `READ_COMP_MCQ` | Reading Comprehension MCQ | MCQList → `mcq` | grammar, communication, vocabulary | A1–C2 | Passage + 4–5 MCQs |
| `READ_TFNG` | True / False / Not Given | TrueFalseNotGiven | grammar, communication | A2–C2 | Passage + T/F/NG statements |
| `READ_ERROR_SPOT` | Error Spotting | ErrorSpotting | grammar | A1–C2 | Flag sentences with grammar errors |
| `READ_CLOZE` | Cloze (Fill-in-blanks) | FillInBlanks → `fill_in_blanks` | grammar, vocabulary | A1–C2 | Paragraph blanks, pick correct form |
| `READ_WORD_MATCH` | Word ↔ Meaning Match | MCQList | vocabulary | A1–C2 | Match word to meaning |
| `READ_CONTEXT_MCQ` | Contextual Vocabulary | MCQList | vocabulary, communication | A1–C2 | Context + meaning MCQ |
| `READ_TONE_ID` | Tone Identification | MCQList | confidence, communication | A2–C2 | Passage + tone MCQ |
| `READ_STRUCTURE_ID` | Structure Identification | OpenTextList → `open_text` | communication | B1–C2 | Label intro/body/conclusion |

### Writing (15)

| ID | Name | Widget | Themes | CEFR | Description |
|----|------|--------|--------|------|-------------|
| `WRITE_OPEN_SENT` | Open Sentence Writing | open_text | grammar | A1–C2 | 3–4 short sentence prompts |
| `WRITE_SENT_TRANS` | Sentence Transformation | SentenceTransform → `open_text` | grammar | A1–C2 | Rewrite for tense/voice/etc. |
| `WRITE_ERROR_CORR` | Error Correction | ErrorCorrection → `open_text` | grammar | A1–C2 | Fix incorrect sentence |
| `WRITE_PARA` | Paragraph Writing | OpenTextList → `open_text` | grammar, communication, vocabulary | A2–C2 | 80–150 word paragraph |
| `WRITE_ESSAY` | Structured Essay | StructuredEssay → `structured_essay` | communication | B1–C2 | 200–400 word essay |
| `WRITE_EMAIL` | Email Writing | OpenTextList → `open_text` | communication | A2–C2 | Scenario email 80–200 words |
| `WRITE_CONCISE` | Conciseness Rewrite | ErrorCorrection → `open_text` | grammar, communication | A2–C2 | Trim wordy sentence |
| `WRITE_WORD_UPGRADE` | Word Upgrade | OpenTextList → `open_text` | vocabulary | A2–C2 | Replace simple word |
| `WRITE_PARAPHRASE` | Paraphrasing | OpenTextList → `open_text` | communication, vocabulary | A2–C2 | Same idea, new words |
| `WRITE_REGISTER` | Register Conversion | ErrorCorrection → `open_text` | communication, confidence | B1–C2 | Formal ↔ informal rewrite |
| `WRITE_IDEA_PARA` | Idea Paraphrasing | OpenTextList → `open_text` | communication | B1–C2 | Restate a concept |
| `WRITE_SUMMARY` | Passage Summary | PassageSummary → `open_text` | communication | A2–C2 | Summarize in N words |
| `WRITE_TIMED` | Timed Writing | TimedWriting → `timed_text` | confidence | A2–C2 | Write against timer |
| `WRITE_VOICE_CONV` | Active ↔ Passive Voice | SentenceTransform → `open_text` | grammar | A2–C2 | Voice conversion |
| `WRITE_BULLETS_TO_PARA` | Bullets → Paragraph | OpenTextList → `open_text` | communication | A2–C2 | Bullets to prose |

### Listening (7)

| ID | Name | Widget | Themes | CEFR | Description |
|----|------|--------|--------|------|-------------|
| `LISTEN_MCQ` | Audio MCQ | ListenAndAnswer+MCQList → `listen_and_respond` | grammar, communication, vocabulary | A1–C2 | Audio + MCQs |
| `LISTEN_CLOZE` | Cloze Listening | ListenAndAnswer+FillInBlanks | grammar, vocabulary | A1–C2 | Fill words from audio |
| `LISTEN_DICTATION` | Dictation | ListenAndAnswer+OpenTextList | grammar, vocabulary | A1–C2 | Type what you hear |
| `LISTEN_INFER` | Inference Listening | ListenAndAnswer+MCQList | communication | B1–C2 | Implied-meaning MCQ |
| `LISTEN_RETELL` | Retell What You Heard | ListenAndAnswer+SpeakAndRecord | communication, confidence | B1–C2 | Speak summary of audio |
| `LISTEN_SHADOW` | Shadow Speaking | ListenAndAnswer+SpeakAndRecord | confidence | A1–C2 | Repeat while audio plays |
| `LISTEN_TONE` | Detect Speaker Tone | ListenAndAnswer+MCQList | confidence, communication | A2–C2 | Emotion/register MCQ |

### Speaking (11)

| ID | Name | Widget | Themes | CEFR | Description |
|----|------|--------|--------|------|-------------|
| `SPEAK_READ_ALOUD` | Read Aloud | SpeakAndRecord → `speak_and_record` | confidence | A1–C2 | Pronunciation focus |
| `SPEAK_PIC_DESC` | Picture Description | SpeakAndRecord | confidence, vocabulary | A1–C2 | Describe image 3–5 sentences |
| `SPEAK_TIMED` | Timed Speaking | SpeakAndRecord | confidence | A1–C2 | Speak on prompt, fluency |
| `SPEAK_STORYBOARD` | Storyboard Narration | Storyboard → `storyboard` | communication | A2–C2 | Narrate scene sequence |
| `SPEAK_INTERVIEW` | Interview Response | SpeakAndRecord | communication, confidence | B1–C2 | Interview-style answer |
| `SPEAK_ROLEPLAY` | Roleplay | SpeakAndRecord | communication, confidence | A2–C2 | Multi-turn scenario |
| `SPEAK_OPINION` | Opinion Speaking | SpeakAndRecord | communication, confidence | B1–C2 | Defend a position |
| `SPEAK_SMALLTALK` | Small Talk Simulation | SpeakAndRecord | confidence, communication | A2–C2 | Casual back-and-forth |
| `SPEAK_DEBATE` | Debate Response | SpeakAndRecord | confidence, communication | B2–C2 | Argue + rebut |
| `SPEAK_PRON_DRILL` | Pronunciation Drill | SpeakAndRecord | confidence | A1–C2 | Repeat target sounds |
| `SPEAK_PRESENT` | Presentation Practice | SpeakAndRecord | confidence, communication | B1–C2 | Mini-presentation |

### Scoring rubrics (for evaluator)

Each archetype has a `rubric` tuple (e.g. `grammatical_accuracy`, `fluency`, `accuracy`) and a `weight_map` across sub-skills: `grammar`, `vocabulary`, `pronunciation`, `fluency`, `expression`, `comprehension`, `tone`. You rarely need to touch these in day authoring unless using `evaluator_overrides`.

---

## 6. AI agents & tools (runtime pipeline)

```
Teaching phase          → Teacher LLM (OpenAI via ILLMClient)
Learner says "ready"    → Task Generator LLM (+ TTS for listening)
Learner submits task    → Evaluator LLM → Feedback LLM
Listening audio         → TTS service (`app/ai/tts`) synthesizes `audio_script`
```

| Agent | When | Input from your day | Output |
|-------|------|---------------------|--------|
| **Teacher** | Before each practice task | `title`, `description`, `teacher_agent_behaviour` | Short chat turns; ends with “Ready to try the practice task?” |
| **Task Generator** | When task is delivered | `title`, `description`, `task_specs[i]`, archetype metadata, learner interests | JSON `task_content` for frontend widget |
| **Evaluator** | On submit | `task_content`, user response, optional `evaluator_overrides` | `raw_score`, `rubric_scores` |
| **Feedback** | After eval | score + response, optional `feedback_overrides` | `summary`, `did_well`, `mistakes`, `next_tip` |
| **TTS** | LISTEN_* tasks | `audio_script` from generator | `audio_url`, `audio_duration_seconds` |

All three session agents share **one parameterized prompt template** (`app/ai/sessions/prompts.py`). Archetype-specific extra instructions exist today for:

- `READ_CLOZE` / `fill_in_blanks`
- `LISTEN_MCQ` / `listen_and_respond` + inner `mcq`
- `WRITE_OPEN_SENT` / `open_text` (exactly 3 items)
- `SPEAK_TIMED` / `speak_and_record` (prompts + samples lists)

Other archetypes still generate via the generic template but get **less post-validation** — author `widget_requirements` carefully.

---

## 7. `task_specs` keys

One dict per archetype in `task_archetypes_used` (same index).

| Key | Purpose |
|-----|---------|
| `topic_override` | Short topic for this task (defaults to day `title`) |
| `instructions_override` | **Verbatim** learner-facing instruction sentence for Task Generator |
| `primary_text_seed` | Seed passage / prompt the LLM should build on |
| `target_words` | `list[str]` — vocabulary to centre the task on |
| `difficulty_note` | Extra CEFR / complexity hint |
| `widget_requirements` | Free-text contract for exact JSON fields (see Week 1 Day 1 `LISTEN_MCQ` / `SPEAK_TIMED`) |
| `task_intro` | Short imperative header shown above widget |
| `estimated_time_minutes` | UI time hint (1–30) |

**Static authored content (bypass LLM for cloze):** put full payload under `fill_in_blanks`, `payload`, or `content` in `task_spec` — only used for `FillInBlanks` widget today.

---

## 8. Widget payload contracts

Normalized widget keys (what chat UI renders): `frontend/src/app/task/chat/[sessionId]/page.tsx`.

Types defined in: `frontend/src/components/task/task-widgets/types.ts`.

### `fill_in_blanks` — `READ_CLOZE`, `LISTEN_CLOZE` (inner)

**Required:** `topic`, `instructions`, `items[]`

Each **BlankItem:**

```json
{
  "item_id": "routine_1",
  "sentence_with_blank": "She usually ___ breakfast at seven.",
  "base_verb": "eat",
  "correct_answer": "eats",
  "distractors": ["eat", "eating"],
  "options": ["eat", "eats", "eating"],
  "grammar_rule": "She adds -s to the verb.",
  "explanation": "With she, add -s: she eats."
}
```

**LLM rules (READ_CLOZE):** 5–7 connected sentences; every item needs `base_verb`; mix I/he/she/they subjects; 2 distractors each; story tied to learner interests.

Also supported: `task_intro`, `grammar_rule_explained`, `passage`, `passage_title`, `estimated_time_minutes`.

---

### `listen_and_respond` — all `LISTEN_*`

**Required:** `audio_script`, `audio_url: null` (backend fills URL), `inner_widget`, inner fields

**MCQ inner (`LISTEN_MCQ`, `LISTEN_INFER`, `LISTEN_TONE`):**

```json
{
  "inner_widget": "mcq",
  "audio_script": "60–120 word spoken passage…",
  "items": [
    {
      "item_id": "q1",
      "prompt": "What time does Maria wake up?",
      "options": ["Six", "Seven", "Eight", "Nine"],
      "correct_index": 1,
      "explanation": "…"
    }
  ]
}
```

- Exactly **4 options** per MCQ item; `correct_index` is **0-based**.
- 3–4 questions typical for A1–A2; more for higher levels.
- If TTS fails → `browser_tts_fallback: true` still allows play via browser.

**Other inner widgets:** `fill_in_blanks`, `open_text`, `speak_and_record` — see `ListenAndRespondPayload` in `types.ts`.

---

### `open_text` — `WRITE_OPEN_SENT`, most writing/reading open tasks

**Required:** `items[]` (for multi-prompt tasks)

Each **OpenTextItem:**

```json
{
  "item_id": "routine_i",
  "prompt": "Write one affirmative routine sentence with I and a frequency adverb.",
  "sample_answer": "I usually drink water in the morning.",
  "answer_hints": ["Start with I.", "Use the base verb."]
}
```

**WRITE_OPEN_SENT validation:** exactly **3 items** with all fields populated.

Also useful: `grammar_rule_explained`, `common_mistakes`, `target_words`, `task_intro`, `estimated_time_minutes`.

---

### `speak_and_record` — `SPEAK_*`, listening retell/shadow inner

**Required:**

```json
{
  "task_intro": "Record your routine sentences.",
  "instructions": "One imperative sentence.",
  "speaking_prompts": ["Say one …", "Say one …", "Say one …"],
  "sample_responses": ["Model answer 1", "Model answer 2", "Model answer 3"],
  "speaking_duration_seconds": 45,
  "grammar_rule_to_practice": "One short rule sentence.",
  "target_words": ["always", "usually", "often"]
}
```

- `speaking_prompts` and `sample_responses` **same length** (typically 2–3).
- Do **not** use singular `speaking_prompt` — always the list form.

**Archetype-specific optional fields:** `text_to_read_aloud` (read aloud), `scenario_description` + `turns` (roleplay), `key_points_expected`, `passage`, etc. — see `SpeakAndRecordPayload`.

---

### `mcq` — standalone reading MCQ (no audio)

Same `items[]` shape as listening MCQ inner widget.

---

### `timed_text` — `WRITE_TIMED`

`writing_prompt`, `time_limit_seconds`, `minimum_word_count`, `target_word_count`, `sample_response`, `no_editing_allowed`.

---

### `structured_essay` — `WRITE_ESSAY`

`overall_topic`, `structure_pattern`, `total_target_words`, `sections[]` with `section_prompt`, `minimum_word_count`, `sample_text`.

---

### `storyboard` — `SPEAK_STORYBOARD`

`overall_story_premise`, `narrative_pattern`, `scenes[]` with `image_prompt`, `narration_focus`, `sample_narration`.

---

## 9. `teacher_agent_behaviour` guidelines

Stored as tuple of strings → passed to teacher as `__scripted_plan`.

**Teacher contract** (`app/ai/agents/teacher.py`):

- One message per turn; **≤1 question**; **≤60 words**.
- Follow steps **in order**; do not add grammar not mentioned in steps.
- Each step once; wrong answer → one correction + one retry → advance.
- Final step: standalone **“Ready to try the practice task?”** (exact phrase in Week 1).
- Never deliver or evaluate practice tasks.

**Recommended pattern (4 turns for A1 grammar days):**

1. **Open** — greet, one concept, one personal question.
2. **Core rule** — use learner’s sentence; one probe.
3. **Extension** — second pattern (e.g. frequency adverbs); one production prompt.
4. **Wrap-up** — readiness question only (no recap).

Scale to **3–5 turns** for higher CEFR; never exceed **5 turns** before readiness.

---

## 10. Gold reference — Week 1 Day 1

Authoritative example in `source_24w.py` (Week 1, first `DaySource`):

| # | Archetype | Role |
|---|-----------|------|
| 1 | `READ_CLOZE` | Guided cloze on simple present routines |
| 2 | `LISTEN_MCQ` | Audio routines + comprehension MCQ |
| 3 | `WRITE_OPEN_SENT` | Produce I/he/she + frequency adverb sentences |
| 4 | `SPEAK_TIMED` | Say routine sentences with mic |

Teaching focus: simple present, subject–verb agreement, frequency adverbs.

Copy this **read → listen → write → speak** quad when a day teaches one grammar point end-to-end.

---

## 11. Suggested archetype mixes by theme

Use as starting points; adjust for day topic and CEFR.

### Grammar week (e.g. Week 1, 5, 9…)

Typical day:

```
READ_CLOZE or READ_ERROR_SPOT
LISTEN_MCQ or LISTEN_CLOZE
WRITE_OPEN_SENT or WRITE_SENT_TRANS or WRITE_ERROR_CORR
SPEAK_TIMED or SPEAK_READ_ALOUD
```

Higher cycles: swap in `WRITE_VOICE_CONV`, `READ_TFNG`, `WRITE_PARA`.

### Communication week

```
READ_COMP_MCQ or READ_TFNG
LISTEN_INFER (B1+) or LISTEN_MCQ
WRITE_EMAIL or WRITE_PARA or WRITE_PARAPHRASE
SPEAK_ROLEPLAY or SPEAK_INTERVIEW or SPEAK_OPINION
```

### Vocabulary week

```
READ_WORD_MATCH or READ_CONTEXT_MCQ
LISTEN_DICTATION or LISTEN_MCQ
WRITE_WORD_UPGRADE or WRITE_PARAPHRASE
SPEAK_PIC_DESC or SPEAK_TIMED
```

### Confidence week

```
READ_TONE_ID or READ_COMP_MCQ
LISTEN_SHADOW or LISTEN_TONE
WRITE_TIMED or WRITE_REGISTER (B1+)
SPEAK_SMALLTALK or SPEAK_PRESENT or SPEAK_DEBATE (B2+)
```

---

## 12. Per-day planning worksheet

Copy for each of the 168 days:

```markdown
### Week __ Day __ — `day_24___ __`

- **Theme / CEFR:** 
- **Grammar or skill focus:** 
- **title:** 
- **description:** 
- **teacher turns (N):** 
  1. 
  2. 
  3. 
  4. 
- **task_archetypes_used:** 
  1. 
  2. 
  3. 
  4. 
- **task_specs notes:** 
  - Task 1: topic_override / instructions_override / widget_requirements
  - Task 2: …
  - Task 3: …
  - Task 4: …
- **target_words (if vocab day):** 
- **evaluator_overrides needed?** 
- **Status:** [ ] drafted [ ] in source_24w.py [ ] smoke-tested
```

---

## 13. Authoring status (24 weeks)

| Week | Theme | CEFR | Days authored |
|------|-------|------|---------------|
| 1 | grammar | A1 | 1 / 7 (Day 1 only) |
| 2 | communication | A1 | 0 / 7 |
| 3 | vocabulary | A1 | 0 / 7 |
| 4 | confidence | A1 | 0 / 7 |
| 5–24 | … | … | 0 / 7 each |

**Total:** 1 / 168 days complete.

---

## 14. Verification checklist

After adding a day to `source_24w.py`:

1. `len(task_specs) == len(task_archetypes_used)` (if specs present).
2. Every archetype ID exists in `ARCHETYPE_REGISTRY`.
3. Archetype `cefr_min` ≤ week CEFR ≤ `cefr_max`.
4. Archetype `themes_supported` includes the week’s `theme_type` (soft guideline — not enforced in code, but affects scoring design).
5. Run: `uv run pytest backend/tests/test_file_source.py -q`
6. Start a learning session for that `day_id` and confirm all widgets render.

---

## 15. Key file paths

| What | Path |
|------|------|
| Author curriculum | `backend/app/data/courses/curriculum/source_24w.py` |
| Archetype registry | `backend/app/scoring/archetypes.py` |
| Theme → archetype pools | `backend/app/data/courses/curriculum/loader.py` |
| File-day loader | `backend/app/modules/curriculum/file_source.py` |
| Task gen prompts | `backend/app/ai/sessions/prompts.py` |
| Task gen + validation | `backend/app/ai/sessions/llm_task_generator.py` |
| Payload normalizers | `backend/app/modules/sessions/task_generator.py` |
| Teacher agent | `backend/app/ai/agents/teacher.py` |
| Frontend payload types | `frontend/src/components/task/task-widgets/types.ts` |
| Chat widgets | `frontend/src/app/task/chat/[sessionId]/page.tsx` |
