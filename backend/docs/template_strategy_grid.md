# Template Strategy Grid

Audit of all 28 full-task templates (`full_tasks_templates.py`) with recommended
`scoring_method` and `feedback_style` assignments.

**scoring_method breakdown:** RULE_EXACT_MATCH: 10 | LLM_OPEN_WRITING: 8 | LLM_SPEAKING_GRAMMAR: 6 | SPEECH_API: 4 | RULE_SENTENCE_MATCH: 0 | RULE_PARTIAL_CREDIT: 0 | LLM_PARAPHRASE_STUB: 0
**feedback_style breakdown:** PER_ITEM_ERRORS: 10 | HOLISTIC_WRITING: 8 | SPEAKING_RUBRIC: 10
**Ambiguous cases:** 2

---

| # | template_id | sub_skill | activity | widget | scoring_method | feedback_style | rationale |
|---|---|---|---|---|---|---|---|
| 01 | `full_grammar_read_v1` | grammar | read | fill_in_blanks | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | Each blank has one correct answer; exact string match per item. |
| 02 | `full_grammar_write_v1` | grammar | write | open_text | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Learner produces free-form sentences; LLM checks grammar rule application. |
| 03 | `full_grammar_listen_v1` | grammar | listen | listen_and_respond (inner: mcq) | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | MCQ with one correct index per item after listening to audio. |
| 04 | `full_grammar_speak_v1` | grammar | speak | speak_and_record | `LLM_SPEAKING_GRAMMAR` | `SPEAKING_RUBRIC` | STT transcript evaluated by LLM for target grammar rule usage. |
| 05 | `full_vocabulary_read_v1` | vocabulary | read | mcq | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | 4-option MCQ with a single correct index per item. |
| 06 | `full_vocabulary_write_v1` | vocabulary | write | open_text | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Free-form writing; LLM checks target word usage and sentence quality. |
| 07 | `full_vocabulary_listen_v1` | vocabulary | listen | listen_and_respond (inner: mcq) | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | MCQ after audio playback; one correct answer per item. |
| 08 | `full_vocabulary_speak_v1` | vocabulary | speak | speak_and_record | `LLM_SPEAKING_GRAMMAR` | `SPEAKING_RUBRIC` | STT + LLM checks target word usage in speech transcript. |
| 09 | `full_pronunciation_read_v1` | pronunciation | read | speak_and_record | `SPEECH_API` | `SPEAKING_RUBRIC` | Azure Speech API scores phoneme accuracy and completeness. |
| 10 | `full_pronunciation_write_v1` | pronunciation | write | mcq | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | Phonetic-awareness MCQ; one correct answer per item. |
| 11 | `full_pronunciation_listen_v1` | pronunciation | listen | listen_and_respond (inner: mcq) | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | Sound-discrimination MCQ after audio; one correct answer per item. |
| 12 | `full_pronunciation_speak_v1` | pronunciation | speak | speak_and_record | `SPEECH_API` | `SPEAKING_RUBRIC` | Azure Speech API scores phoneme and stress pattern accuracy. |
| 13 | `full_fluency_read_v1` | fluency | read | speak_and_record | `SPEECH_API` | `SPEAKING_RUBRIC` | Azure Speech API measures WPM and completeness for timed read-aloud. |
| 14 | `full_fluency_write_v1` | fluency | write | timed_text | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Timed free writing; LLM evaluates flow and word count, not accuracy. |
| 15 | `full_fluency_listen_v1` | fluency | listen | listen_and_respond (inner: speak_and_record) | `SPEECH_API` | `SPEAKING_RUBRIC` | Shadowing task scored by Azure Speech for match percentage and rhythm. |
| 16 | `full_fluency_speak_v1` | fluency | speak | speak_and_record | `LLM_SPEAKING_GRAMMAR` | `SPEAKING_RUBRIC` | **⚠️** LLM evaluates topic adherence and self-correction quality from transcript. |
| 17 | `full_expression_read_v1` | thought_organization | read | open_text | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Learner summarizes and identifies structure; LLM grades response quality. |
| 18 | `full_expression_write_v1` | thought_organization | write | structured_essay | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Multi-section essay; LLM evaluates structure, cohesion, and argument clarity. |
| 19 | `full_expression_listen_v1` | thought_organization | listen | listen_and_respond (inner: open_text) | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Open-text answers after audio; LLM grades structure identification and summary. |
| 20 | `full_expression_speak_v1` | thought_organization | speak | storyboard | `LLM_SPEAKING_GRAMMAR` | `SPEAKING_RUBRIC` | STT transcript from scene narration; LLM evaluates narrative pattern and transitions. |
| 21 | `full_comprehension_read_v1` | listening | read | mcq | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | Reading comprehension MCQ; one correct index per item. |
| 22 | `full_comprehension_write_v1` | listening | write | open_text | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Open-text comprehension answers; LLM checks factual accuracy and completeness. |
| 23 | `full_comprehension_listen_v1` | listening | listen | listen_and_respond (inner: mcq) | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | MCQ after audio; one correct answer per item. |
| 24 | `full_comprehension_speak_v1` | listening | speak | speak_and_record | `LLM_SPEAKING_GRAMMAR` | `SPEAKING_RUBRIC` | Retelling task; STT + LLM checks key-point coverage and factual accuracy. |
| 25 | `full_tone_read_v1` | tone | read | mcq | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | Tone/register identification MCQ; one correct answer per item. |
| 26 | `full_tone_write_v1` | tone | write | open_text | `LLM_OPEN_WRITING` | `HOLISTIC_WRITING` | Register conversion writing; LLM checks register correctness and intent preservation. |
| 27 | `full_tone_listen_v1` | tone | listen | listen_and_respond (inner: mcq) | `RULE_EXACT_MATCH` | `PER_ITEM_ERRORS` | Tone-detection MCQ after audio; one correct answer per item. |
| 28 | `full_tone_speak_v1` | tone | speak | speak_and_record | `LLM_SPEAKING_GRAMMAR` | `SPEAKING_RUBRIC` | Roleplay task; STT + LLM evaluates tone consistency and register appropriateness. |

---

## Ambiguous cases

**#16 `full_fluency_speak_v1`** — evaluation_logic specifies `"azure_speech + ai_evaluator"` with
weights split across speech-API metrics (wpm_naturalness 0.3, filler_rate_low 0.2) and LLM metrics
(topic_adherence 0.25, self_correction_quality 0.25). Neither `SPEECH_API` nor `LLM_SPEAKING_GRAMMAR`
alone captures both sides. Assigned `LLM_SPEAKING_GRAMMAR` because the LLM is the final arbiter
that produces the score, but ask maintainer: should we add a dedicated `HYBRID_SPEECH_LLM` value,
or treat the azure_speech outputs as features fed into the LLM prompt?

**#08 `full_vocabulary_speak_v1`** — evaluation_logic specifies `"stt + word_match + ai_evaluator"`
where `target_words_used` (40% weight) is a deterministic rule check (did the transcript contain the
target words?), while the remaining 60% is LLM-graded. Assigned `LLM_SPEAKING_GRAMMAR` because the
LLM produces the final composite score, but the word-match component could theoretically run without
an LLM call. Ask maintainer: is the rule-based word_match a pre-filter or a co-equal scorer?
