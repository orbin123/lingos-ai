Evaluate the learner's IELTS Writing responses for a Phase 4 IELTS Sprint attempt.

Official scoring references to follow:
- IELTS scoring in detail: https://ielts.org/take-a-test/your-results/ielts-scoring-in-detail
- IELTS Writing band descriptors PDF: https://ielts.org/cdn/ielts-guides/ielts-writing-band-descriptors.pdf

Use the IELTS Writing Task 2 criteria:
- Task Response
- Coherence and Cohesion
- Lexical Resource
- Grammatical Range and Accuracy

Calibration rules:
- Scores must be IELTS bands from 0.0 to 9.0 in 0.5 increments.
- Apply the public Task 2 descriptors consistently. Band 9 is fully developed, precise, natural, and controlled. Band 7 is clear and developed with minor lapses. Band 6 addresses the main parts but may have underdeveloped support and noticeable language issues. Band 5 is limited or only partly developed. Bands 0-4 reflect missing, off-topic, very limited, or hard-to-follow responses.
- If a response is empty, unrelated, not English, copied from the prompt, or too short to rate meaningfully, score it conservatively and explain why.
- Quote short learner phrases only when identifying issues. Do not invent quotes.
- Do not score Reading, Listening, or Speaking here. The service layer handles those sections.

Inputs:

attempt_id:
{{attempt_id}}

task_payload:
{{task_payload}}

response_payload:
{{response_payload}}

writing_task:
{{writing_task}}

writing_responses:
{{writing_responses}}

Return an object matching this structure:

{
  "mode": "ai_writing_phase_4",
  "items": [
    {
      "item_id": "w1",
      "prompt": "The writing prompt text",
      "response_excerpt": "A short excerpt from the learner response",
      "response_word_count": 95,
      "criteria": {
        "task_response": {
          "band": 6.0,
          "rationale": "Specific reason tied to Task Response"
        },
        "coherence_and_cohesion": {
          "band": 6.0,
          "rationale": "Specific reason tied to organisation and cohesion"
        },
        "lexical_resource": {
          "band": 6.0,
          "rationale": "Specific reason tied to vocabulary range and accuracy"
        },
        "grammatical_range_and_accuracy": {
          "band": 6.0,
          "rationale": "Specific reason tied to grammar range and accuracy"
        }
      },
      "issues": [
        {
          "quote": "learner phrase",
          "issue": "What is weak or incorrect",
          "correction": "Optional corrected wording",
          "suggestion": "One concrete way to improve this issue"
        }
      ],
      "band": 6.0,
      "summary": "Concise summary for this prompt"
    }
  ],
  "section_band": 6.0,
  "summary": "Concise summary across all writing prompts"
}

Return only the structured object. No markdown, no commentary, no extra fields.
