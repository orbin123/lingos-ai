"""Per-user course preference state for the daily-sessions flow.

A `UserCoursePreference` carries the four pieces of state that used to live
on `UserEnrollment`:
  - `course_length` (24w | 48w)
  - `tasks_per_day` (2..4)
  - `allow_read` / `allow_write` / `allow_listen` / `allow_speak`
  - `current_week`, `current_day_in_week` (+ `current_day_started_at`,
    `last_completed_on`)

Exactly one row per user. Created lazily on first access — see
`PreferenceService.get`.
"""
