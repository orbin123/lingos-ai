"""Sessions module — new daily-session lifecycle.

Owns:
  - `DailySession`, `ActivityAttempt`, `ActivityEvaluation`, `ActivityFeedback`,
    `SessionScorecard` ORM models
  - The Planner that turns a CurriculumDay into a session skeleton
  - `SessionService` orchestrating start / next-activity / submit / complete
  - The replay guard and the writer that pushes the scorecard into SkillPoints

Phase 3 keeps Evaluator and FeedbackGenerator as stubs so the math + lifecycle
can ship without LLM integration. Phase 4 replaces them with the real agents.
"""
