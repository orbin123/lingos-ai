Generate concise, encouraging IELTS practice feedback from a structured IELTS Sprint evaluation report.

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
- Listening feedback must use the deterministic correctness report when present. Mention audio comprehension patterns rather than calling it a placeholder.
- Writing feedback must use criterion scores and issues from the writing evaluation. Use short learner quotes only if they appear in the report.
- Speaking uses Phase 6 transcript-only scoring when present. Mention the transcript-only limitation and explicitly note that Pronunciation is not scored yet.
- Keep each string short enough for a result panel.
- Do not include markdown, headings, code fences, or extra fields.

Return an object matching this structure:

{
  "mode": "phase_4_feedback",
  "overall_summary": "Two concise sentences about the attempt.",
  "sections": {
    "listening": {
      "went_well": ["Specific strength from the listening report."],
      "needs_work": ["Specific missed question or listening pattern."],
      "next_tip": "One concrete listening tactic for next time."
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
      "went_well": ["Specific strength from the transcript-only speaking report."],
      "needs_work": ["Specific transcript-based speaking issue. Pronunciation is not scored yet."],
      "next_tip": "One concrete speaking tactic for next time."
    }
  }
}

Return only the structured object.
