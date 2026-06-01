"""Reproduce the worked example from the restructure spec (§13.6).

The spec text classifies a raw_score of 6.0 as 'Average' (24 pts) in its
worked example. The same spec's tier table (§13.2) and its edge-case note
(§13.7) both state that boundary scores fall into the higher tier — so 6.0
should be Good (40 pts). The engine follows the rule, not the worked
example, so the expected numbers below are recomputed accordingly.

We translate doc sub-skill names to code names per RESTRUCTURE_DECISIONS.md §2:
  thought_org → expression, listening → comprehension, tone_social → tone.
"""

from app.scoring.archetypes import get_archetype
from app.scoring.constants import CourseLength, MAX_POINTS_PER_SUBSKILL
from app.scoring.engine import build_session_aggregation
from app.scoring.types import ActivityScore


def test_full_session_walkthrough_with_corrected_boundary():
    activities = [
        ActivityScore(
            archetype_id="READ_CONTEXT_MCQ",
            raw_score=7.0,                                # Good → 40
            weight_map=get_archetype("READ_CONTEXT_MCQ").weight_map,
        ),
        ActivityScore(
            archetype_id="WRITE_EMAIL",
            raw_score=5.0,                                # Average → 24
            weight_map=get_archetype("WRITE_EMAIL").weight_map,
        ),
        ActivityScore(
            archetype_id="LISTEN_MCQ",
            raw_score=8.0,                                # Excellent → 55
            weight_map=get_archetype("LISTEN_MCQ").weight_map,
        ),
        ActivityScore(
            archetype_id="SPEAK_ROLEPLAY",
            raw_score=6.0,                                # Good → 40 (spec says Average; rule wins)
            weight_map=get_archetype("SPEAK_ROLEPLAY").weight_map,
        ),
    ]

    current = {
        "grammar": 3800,
        "vocabulary": 4100,
        "pronunciation": 5000,
        "fluency": 5500,
        "expression": 4500,
        "comprehension": 4200,
        "tone": 3000,
    }

    agg = build_session_aggregation(activities, CourseLength.WEEKS_24, current_totals=current)

    # Per-activity contributions before rounding:
    #   READ_CONTEXT_MCQ(40)  grammar 4.0   vocab 28.0                          expr 8.0
    #   WRITE_EMAIL(24)       grammar 6.0   vocab 4.8                           expr 3.6   tone 9.6
    #   LISTEN_MCQ(55)                       vocab 13.75                         expr 8.25  comp 33.0
    #   SPEAK_ROLEPLAY(40)    grammar 6.0   vocab 8.0  pron 4.0  fluency 10.0              tone 12.0
    # Sum then round once per sub-skill at session end (engine.aggregate_session):
    expected_earned = {
        "grammar":       16,   # 4.0 + 6.0 + 0 + 6.0 = 16.0
        "vocabulary":    55,   # 28.0 + 4.8 + 13.75 + 8.0 = 54.55 → 55
        "pronunciation": 4,    # 4.0
        "fluency":       10,   # 10.0
        "expression":    20,   # 8.0 + 3.6 + 8.25 = 19.85 → 20
        "comprehension": 33,   # 33.0
        "tone":          22,   # 9.6 + 12.0 = 21.6 → 22
    }
    assert agg.points_earned == expected_earned

    # Totals = current + earned, capped at MAX_POINTS_PER_SUBSKILL. None hits the cap here.
    expected_totals = {
        "grammar":       3816,
        "vocabulary":    4155,
        "pronunciation": 5004,
        "fluency":       5510,
        "expression":    4520,
        "comprehension": 4233,
        "tone":          3022,
    }
    assert agg.subskill_totals_after == expected_totals

    # Dashboard at 1 decimal, half-up at the 100-pt step.
    assert agg.dashboard_after == {
        "grammar":       3.8,
        "vocabulary":    4.2,
        "pronunciation": 5.0,
        "fluency":       5.5,
        "expression":    4.5,
        "comprehension": 4.2,
        "tone":          3.0,
    }


def test_cap_holds_dashboard_at_ten_while_earned_keeps_logging():
    """A user already at the cap still earns visible "+N" deltas; their
    internal total and dashboard score stop moving."""
    activities = [
        ActivityScore(
            # Synthetic pronunciation-heavy split (0.85/0.15) to make the cap
            # math obvious; archetype_id is just a label and isn't looked up.
            archetype_id="WORKED_EXAMPLE_PRON",
            raw_score=9.0,                                # Excellent → 55 (24w)
            weight_map={"pronunciation": 0.85, "fluency": 0.15},
        ),
    ]
    agg = build_session_aggregation(
        activities,
        CourseLength.WEEKS_24,
        current_totals={"pronunciation": MAX_POINTS_PER_SUBSKILL, "fluency": 9000},
    )

    # 55 pts split 0.85 / 0.15 → pron 46.75 → 47, fluency 8.25 → 8
    assert agg.points_earned == {"pronunciation": 47, "fluency": 8}
    assert agg.subskill_totals_after == {
        "pronunciation": MAX_POINTS_PER_SUBSKILL,
        "fluency":       9008,
    }
    assert agg.dashboard_after == {"pronunciation": 10.0, "fluency": 9.0}


def test_skipped_activity_simply_isnt_in_the_list():
    # Doc §13.7 edge case: "User skips an activity | Not evaluated, contributes
    # 0 points, doesn't appear in aggregation". The session service is expected
    # to omit skipped attempts when assembling the ActivityScore list.
    activities = [
        ActivityScore(
            archetype_id="READ_COMP_MCQ",
            raw_score=8.0,
            weight_map=get_archetype("READ_COMP_MCQ").weight_map,
        ),
        # Two further activities deliberately omitted (would-be skips).
    ]
    agg = build_session_aggregation(activities, CourseLength.WEEKS_24)
    assert agg.points_earned == {"grammar": 14, "vocabulary": 22, "expression": 19}
    # 55 pts × 0.25 = 13.75 → 14
    # 55 pts × 0.40 = 22.0  → 22
    # 55 pts × 0.35 = 19.25 → 19


def test_48w_track_rewards_are_lower_for_the_same_session():
    """Same activity list, different track. 48w yields ~half the points."""
    activities = [
        ActivityScore(
            archetype_id="WRITE_PARA",
            raw_score=8.0,                                # Excellent
            weight_map=get_archetype("WRITE_PARA").weight_map,
        ),
    ]
    earned_24 = build_session_aggregation(activities, CourseLength.WEEKS_24).points_earned
    earned_48 = build_session_aggregation(activities, CourseLength.WEEKS_48).points_earned

    # WRITE_PARA Excellent: 55 (24w) vs 28 (48w). Weight map grammar 0.35 /
    # vocab 0.25 / expression 0.40 → rounds shouldn't flip the inequality.
    for skill in earned_24:
        assert earned_24[skill] >= earned_48[skill], (
            f"{skill}: 24w earned {earned_24[skill]} not ≥ 48w {earned_48[skill]}"
        )
