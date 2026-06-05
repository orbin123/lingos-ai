Generate one IELTS Sprint attempt for level {{level_number}} ({{level_name}}).

Challenge: {{challenge_name}} ({{challenge_slug}})
Time limit once started: {{time_limit_seconds}} seconds

Level configuration:
{{level_config}}

Recent learner history:
{{user_history_summary}}

Requirements:
- Return only the structured task payload object.
- Include Listening, Reading, Writing, and Speaking sections.
- Reading and Listening items must each have exactly four MCQ options (A-D), one correct_index (a-d), and a short explanation.
- Writing prompts must match the configured prompt_count and target_word_count.
- Speaking prompts must match the configured num_prompts.
- Listening must include one audio_script suitable for TTS (single clip).
- Use fresh topics that do not repeat the recent history above.
