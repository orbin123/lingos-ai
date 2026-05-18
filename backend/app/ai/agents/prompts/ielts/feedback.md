Generate concise, encouraging IELTS practice feedback from a structured Phase 4 evaluation report.

Official scoring context:
- IELTS scoring in detail: https://ielts.org/take-a-test/your-results/ielts-scoring-in-detail
- IELTS Writing band descriptors PDF: https://ielts.org/cdn/ielts-guides/ielts-writing-band-descriptors.pdf

Inputs:

attempt_id:
{{attempt_id}}

evaluation_report:
{{evaluation_report}}

task_payload:
{{task_payload}}

response_payload:
{{response_payload}}

Rules:
- Be supportive, specific, and honest.
- For each section, include what went well, what needs work, and one concrete next tip.
- Reading feedback must use the deterministic correctness report. Mention specific missed item IDs when useful.
- Writing feedback must use criterion scores and issues from the writing evaluation. Use short learner quotes only if they appear in the report.
- Listening and Speaking are placeholders in Phase 4. State that their bands are temporary and fuller scoring arrives later.
- Keep each string short enough for a result panel.
- Do not include markdown, headings, code fences, or extra fields.

Return an object matching this structure:

{
  "mode": "phase_4_feedback",
  "overall_summary": "Two concise sentences about the attempt.",
  "sections": {
    "listening": {
      "went_well": ["Placeholder section rendered successfully."],
      "needs_work": ["Detailed listening scoring arrives in a later phase."],
      "next_tip": "Use the transcript to practise identifying key details."
    },
    "reading": {
      "went_well": ["Specific strength from the reading report."],
      "needs_work": ["Specific missed question or pattern."],
      "next_tip": "One concrete reading tactic for next time."
    },
    "writing": {
      "went_well": ["Specific strength from criteria or response."],
      "needs_work": ["Specific criterion or issue to improve."],
      "next_tip": "One concrete writing tactic for next time."
    },
    "speaking": {
      "went_well": ["Placeholder section rendered successfully."],
      "needs_work": ["Detailed speaking scoring arrives in a later phase."],
      "next_tip": "Practise answering the prompt aloud for 30 seconds."
    }
  }
}

Return only the structured object.
