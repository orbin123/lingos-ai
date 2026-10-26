# 5. Session lifecycle walkthrough

1. The learner starts a daily session. The session service loads the curriculum blueprint and creates/loads the V2 session rows.
2. The planner selects the next deterministic activity. Its archetype is resolved through the single contract registry.
3. The task generator may use an LLM to create content, constrained by task schemas and the archetype contract.
4. The frontend receives a REST response or WebSocket event and selects the matching task widget.
5. The learner submits text or audio. Audio may first pass through STT/transcription and pronunciation assessment.
6. The evaluator returns a structured judgment. The feedback generator can retrieve relevant feedback memory and produces structured feedback.
7. `SessionService.submit_activity` persists the evaluation and feedback in one logical transaction, records streak activity, and guards replayed submissions.
8. The deterministic scoring engine converts the graded activity into sub-skill rewards. The score writer updates `SkillPoints` once for the valid attempt.
9. Completion produces a scorecard and the dashboard reads progress, streaks, and skill totals.

The key exam answer is: LLM output is probabilistic; the application wraps it in typed contracts, validates it, and persists it through ordinary service/repository rules.
