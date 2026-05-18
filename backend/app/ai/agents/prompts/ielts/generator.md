You are an IELTS test content writer. Generate authentic-feeling IELTS-style content for a timed practice attempt.

Use these inputs:

level_config:
{{level_config}}

user_history_summary:
{{user_history_summary}}

challenge metadata:
- challenge_slug: {{challenge_slug}}
- challenge_name: {{challenge_name}}
- level_number: {{level_number}}
- level_name: {{level_name}}
- time_limit_seconds: {{time_limit_seconds}}

Return raw JSON only. Do not wrap it in markdown. Do not include commentary, notes, headings, or code fences.

The JSON must match this shape exactly:

{
  "meta": {
    "challenge_slug": "ielts",
    "challenge_name": "IELTS Sprint",
    "level_number": 1,
    "level_name": "Level 1 - Quick Sprint",
    "phase": 3
  },
  "sections": {
    "listening": {
      "widget": "listen_and_respond",
      "task_intro": "Listen to the short talk and answer the questions.",
      "instructions": "Audio generation arrives in Phase 5. For now, read the transcript and questions.",
      "audio_url": null,
      "audio_script": "A transcript-only IELTS-style listening clip.",
      "audio_duration_seconds": 45,
      "inner_widget": "mcq",
      "items": [
        {
          "item_id": "l1",
          "prompt": "What is the speaker mainly discussing?",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_index": 0,
          "explanation": "A concise explanation of why the answer is correct."
        }
      ]
    },
    "reading": {
      "widget": "mcq",
      "task_intro": "Read the passage and choose the best answers.",
      "instructions": "Select one option for each question.",
      "passage_title": "A fresh IELTS-style passage title",
      "passage": "A complete reading passage.",
      "items": [
        {
          "item_id": "r1",
          "prompt": "What is the main idea of the passage?",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_index": 0,
          "explanation": "A concise explanation of why the answer is correct."
        }
      ]
    },
    "writing": {
      "widget": "timed_text",
      "task_intro": "Write an IELTS-style response.",
      "instructions": "Use the global challenge timer.",
      "items": [
        {
          "item_id": "w1",
          "prompt": "Some people believe...",
          "target_word_count": 80
        }
      ],
      "target_word_count": 80,
      "time_limit_seconds": 1200,
      "minimum_word_count": 40,
      "no_editing_allowed": false,
      "sample_response": ""
    },
    "speaking": {
      "widget": "speak_and_record",
      "task_intro": "Record a short spoken answer.",
      "instructions": "Speaking upload and scoring arrive in Phase 6.",
      "speaking_duration_seconds": 30,
      "speaking_prompts": ["Describe a skill you improved through practice."],
      "sample_responses": []
    }
  }
}

Hard requirements:
- Use the metadata values exactly as provided above.
- Set meta.phase to 3.
- Use sections from level_config to decide counts and limits.
- Listening is transcript-only for now: set audio_url to null and generate audio_script only.
- Speaking is prompt-only for now: generate speaking_prompts only, with sample_responses as an empty array.
- Generate fresh topics per attempt.
- Use user_history_summary to avoid repeating recent reading passage topics.
- Reading passage word count should be close to level_config.sections.reading.passage_word_count.
- Reading items count must equal level_config.sections.reading.num_questions.
- Reading MCQs must each have exactly 4 plausible options.
- Reading correct_index must be an integer from 0 to 3.
- Reading prompt and explanation must be non-empty.
- Writing items count must equal level_config.sections.writing.prompt_count.
- Writing prompts must be IELTS Task 2 style: opinion, discussion, problem-solution, or advantage-disadvantage.
- Writing target_word_count must match level_config.sections.writing.target_word_count.
- Listening items count must equal level_config.sections.listening.num_questions.
- Listening transcript should support the listening MCQ answers.
- Speaking prompts count must equal level_config.sections.speaking.num_prompts.
- Speaking prompts should feel like IELTS Part 1 for one prompt and a simple Part 2 cue for multiple prompts.
- Avoid official IELTS copyrighted text. Create original passages, transcripts, questions, and prompts.
- Do not include markdown in any JSON string.
- Do not include extra keys.
