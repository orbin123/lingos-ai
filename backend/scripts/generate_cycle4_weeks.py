"""Generate weeks 13-16 DaySource blocks by mirroring weeks 9-12."""

from __future__ import annotations

import dataclasses
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

# Run from backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.modules.curriculum.data.source_L_B1B2 import WEEKS_B1B2  # noqa: E402
from app.modules.curriculum.data.types import (  # noqa: E402
    ActivityBlueprint,
    DaySource,
    EvaluationBlueprint,
    FeedbackBlueprint,
    TaskBlueprint,
    TeacherBlueprint,
    TeacherStep,
    WeekSource,
)

# Global 24w weeks 9-16 ↔ B1B2 band-local weeks 1-8.
WEEKS_24 = WEEKS_B1B2


def _band_week(global_week: int) -> int:
    return global_week - 8


def _find_band_week(global_week: int) -> WeekSource:
    local = _band_week(global_week)
    return next(x for x in WEEKS_24 if x.week_number == local)

THIRD_COND_LISTEN_PAYLOAD: dict[str, Any] = {
    "task_intro": "Listen, then complete the third-conditional notes.",
    "instructions": (
        "Play the audio once, then type the missing third-conditional verbs "
        "in the paraphrased notes."
    ),
    "estimated_time_minutes": 3,
    "inner_widget": "fill_in_blanks",
    "audio_genre": "Reflective regrets monologue",
    "audio_script": (
        "Sometimes I think about different choices. If I had studied harder, I "
        "would have passed the exam. If we had left earlier, we would have "
        "caught the train. If she had known the truth, she would have called "
        "me. If they had invited us, we would have come to the party. "
        "Honestly, if I had listened to your advice, I would have saved a lot "
        "of time."
    ),
    "passage_title": "Different Choices Notes",
    "passage": (
        "If I ___ harder, I would have passed the exam. If we had left earlier, "
        "we ___ the train. If she had known the truth, she ___ me. If they ___ "
        "us, we would have come. If I had listened to your advice, I ___ a lot "
        "of time."
    ),
    "items": [
        {
            "item_id": "b1",
            "blank_id": "b1",
            "sentence_with_blank": "If I ___ harder, I would have passed the exam.",
            "base_verb": "study",
            "correct_answer": "had studied",
            "distractors": ["studied", "would study"],
            "options": ["had studied", "studied", "would study"],
            "grammar_rule": "Use the past perfect in the if-clause of the third conditional.",
            "explanation": "The if-clause needs had + past participle, so we use had studied.",
        },
        {
            "item_id": "b2",
            "blank_id": "b2",
            "sentence_with_blank": "If we had left earlier, we ___ the train.",
            "base_verb": "catch",
            "correct_answer": "would have caught",
            "distractors": ["will catch", "caught"],
            "options": ["would have caught", "will catch", "caught"],
            "grammar_rule": "Use would have + past participle in the result clause.",
            "explanation": "The unreal past result uses would have caught.",
        },
        {
            "item_id": "b3",
            "blank_id": "b3",
            "sentence_with_blank": "If she had known the truth, she ___ me.",
            "base_verb": "call",
            "correct_answer": "would have called",
            "distractors": ["will call", "called"],
            "options": ["would have called", "will call", "called"],
            "grammar_rule": "Use would have + past participle in the result clause.",
            "explanation": "The imagined past result uses would have called.",
        },
        {
            "item_id": "b4",
            "blank_id": "b4",
            "sentence_with_blank": "If they ___ us, we would have come.",
            "base_verb": "invite",
            "correct_answer": "had invited",
            "distractors": ["invited", "would invite"],
            "options": ["had invited", "invited", "would invite"],
            "grammar_rule": "Use the past perfect in the if-clause of the third conditional.",
            "explanation": "The if-clause needs had invited.",
        },
        {
            "item_id": "b5",
            "blank_id": "b5",
            "sentence_with_blank": (
                "If I had listened to your advice, I ___ a lot of time."
            ),
            "base_verb": "save",
            "correct_answer": "would have saved",
            "distractors": ["will save", "saved"],
            "options": ["would have saved", "will save", "saved"],
            "grammar_rule": "Use would have + past participle in the result clause.",
            "explanation": "The imagined past result uses would have saved.",
        },
    ],
    "target_words_in_audio": [
        "had studied",
        "would have caught",
        "would have called",
        "had invited",
        "would have saved",
    ],
}


@dataclasses.dataclass(frozen=True)
class DaySpec:
    title: str
    description: str
    focus: str
    lesson_goal: str
    steps: tuple[tuple[str, str, str], ...]  # id, goal, instruction
    activity_ids: tuple[str, ...]
    topic_overrides: tuple[str, ...]
    generation_instructions: tuple[str, ...]
    widget_requirements: tuple[str | None, ...] = ()
    static_payload_index: int | None = None
    static_payload: dict[str, Any] | None = None


def _week_days(week: int) -> tuple[DaySource, ...]:
    return _find_band_week(week).days


def _apply_strings(obj: Any, pairs: tuple[tuple[str, str], ...]) -> Any:
    if dataclasses.is_dataclass(obj):
        return type(obj)(
            **{
                f.name: _apply_strings(getattr(obj, f.name), pairs)
                for f in dataclasses.fields(obj)
            }
        )
    if isinstance(obj, tuple):
        return tuple(_apply_strings(x, pairs) for x in obj)
    if isinstance(obj, list):
        return [_apply_strings(x, pairs) for x in obj]
    if isinstance(obj, dict):
        return {k: _apply_strings(v, pairs) for k, v in obj.items()}
    if isinstance(obj, str):
        out = obj
        for old, new in pairs:
            out = out.replace(old, new)
        return out
    return obj


def _build_day(mirror: DaySource, spec: DaySpec) -> DaySource:
    steps = tuple(
        TeacherStep(id=s[0], goal=s[1], instruction=s[2]) for s in spec.steps
    )
    teacher = TeacherBlueprint(lesson_goal=spec.lesson_goal, steps=steps)
    activities: list[ActivityBlueprint] = []
    for i, act in enumerate(mirror.activities):
        wr = (
            spec.widget_requirements[i]
            if i < len(spec.widget_requirements) and spec.widget_requirements[i]
            else act.task.widget_requirements
        )
        gen = spec.generation_instructions[i]
        topic = spec.topic_overrides[i]
        task = dataclasses.replace(
            act.task,
            topic_override=topic,
            generation_instructions=gen,
            widget_requirements=wr,
        )
        if spec.static_payload_index == i and spec.static_payload is not None:
            task = dataclasses.replace(task, static_payload=deepcopy(spec.static_payload))
        activities.append(
            dataclasses.replace(act, id=spec.activity_ids[i], task=task)
        )
    return DaySource(
        title=spec.title,
        description=spec.description,
        focus=spec.focus,
        teacher=teacher,
        activities=tuple(activities),
        final_review=mirror.final_review,
    )


def _indent_block(text: str, indent: str) -> str:
    return "\n".join(indent + line if line else line for line in text.split("\n"))


def _emit_str(value: str, indent: str, name: str) -> str:
    if "\n" in value or len(value) > 78:
        parts = re.findall(r".{1,68}(?:\s|$)", value + " ")
        chunks = [p.strip() for p in parts if p.strip()]
        lines = [f'{indent}{name}=(']
        for i, p in enumerate(chunks):
            if i < len(chunks) - 1 and not p.endswith(" "):
                p = p + " "
            lines.append(f'{indent}    "{p}"')
        lines.append(f"{indent}),")
        return "\n".join(lines)
    esc = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'{indent}{name}="{esc}",'


def _emit_teacher(tb: TeacherBlueprint, indent: str) -> list[str]:
    lines = [
        f"{indent}teacher=TeacherBlueprint(",
        f'{indent}    lesson_goal="{tb.lesson_goal}",',
        f"{indent}    steps=(",
    ]
    for s in tb.steps:
        lines.append(f"{indent}        TeacherStep(")
        lines.append(f'{indent}            id="{s.id}",')
        lines.append(f'{indent}            goal="{s.goal}",')
        lines.append(f"{indent}            instruction=(")
        inst_parts = [
            p.strip() for p in re.findall(r".{1,72}(?:\s|$)", s.instruction + " ") if p.strip()
        ]
        for i, part in enumerate(inst_parts):
            if i < len(inst_parts) - 1 and not part.endswith(" "):
                part = part + " "
            lines.append(f'{indent}                "{part}"')
        lines.append(f"{indent}            ),")
        lines.append(f"{indent}        ),")
    lines.append(f"{indent}    ),")
    lines.append(f"{indent}),")
    return lines


def _emit_dict(d: dict[str, Any], indent: str) -> list[str]:
    import pprint

    formatted = pprint.PrettyPrinter(width=88, sort_dicts=False).pformat(d)
    lines = []
    for line in formatted.splitlines():
        lines.append(indent + line)
    return lines


def _emit_task(task: TaskBlueprint, indent: str) -> list[str]:
    lines = [
        f"{indent}task=TaskBlueprint(",
        f'{indent}    archetype_id="{task.archetype_id}",',
        f'{indent}    activity="{task.activity}",',
        f'{indent}    task_widget="{task.task_widget}",',
        f'{indent}    topic_override="{task.topic_override}",',
        f"{indent}    generation_instructions=(",
    ]
    parts = [p.strip() for p in re.findall(r".{1,72}(?:\s|$)", task.generation_instructions + " ") if p.strip()]
    for i, part in enumerate(parts):
        if i < len(parts) - 1 and not part.endswith(" "):
            part = part + " "
        lines.append(f'{indent}        "{part}"')
    lines.append(f"{indent}    ),")
    if task.widget_requirements:
        lines.append(f"{indent}    widget_requirements=(")
        wr_parts = [
            p.strip()
            for p in re.findall(r".{1,72}(?:\s|$)", task.widget_requirements + " ")
            if p.strip()
        ]
        for i, part in enumerate(wr_parts):
            if i < len(wr_parts) - 1 and not part.endswith(" "):
                part = part + " "
            lines.append(f'{indent}        "{part}"')
        lines.append(f"{indent}    ),")
    if task.static_payload is not None:
        lines.append(f"{indent}    static_payload=")
        lines.extend(_emit_dict(task.static_payload, indent + "    "))
        lines[-1] = lines[-1] + ","
    lines.append(f"{indent}),")
    return lines


def _emit_activity(act: ActivityBlueprint, indent: str) -> list[str]:
    lines = [
        f"{indent}ActivityBlueprint(",
        f'{indent}    id="{act.id}",',
        f"{indent}    sequence={act.sequence},",
    ]
    lines.extend(_emit_task(act.task, indent + "    "))
    ev = act.evaluation
    lines.extend(
        [
            f"{indent}    evaluation=EvaluationBlueprint(",
            f'{indent}        evaluator="{ev.evaluator}",',
            f'{indent}        evaluation_widget="{ev.evaluation_widget}",',
            f"{indent}    ),",
        ]
    )
    fb = act.feedback
    fb_lines = [f"{indent}    feedback=FeedbackBlueprint("]
    if fb.generator != "default":
        fb_lines.append(f'{indent}        generator="{fb.generator}",')
    fb_lines.append(f'{indent}        feedback_widget="{fb.feedback_widget}",')
    fb_lines.append(f"{indent}    ),")
    lines.extend(fb_lines)
    lines.append(f"{indent}),")
    return lines


def _emit_day(day: DaySource, indent: str) -> list[str]:
    lines = [f"{indent}DaySource("]
    lines.append(_emit_str(day.title, indent + "    ", "title"))
    lines.append(_emit_str(day.description, indent + "    ", "description"))
    lines.append(_emit_str(day.focus, indent + "    ", "focus"))
    lines.extend(_emit_teacher(day.teacher, indent + "    "))
    lines.append(f"{indent}    activities=(")
    for act in day.activities:
        lines.extend(_emit_activity(act, indent + "        "))
    lines.append(f"{indent}    ),")
    lines.append(f"{indent}),")
    return lines


# fmt: off
DAY_SPECS: dict[tuple[int, int], DaySpec] = {
    # Week 13 grammar (mirror week 9)
    (13, 0): DaySpec(
        title="Past Perfect Continuous - Duration Before a Past Moment",
        description=(
            "Learners use the past perfect continuous (had been + verb-ing) to "
            "show that an action had been ongoing for a period before another "
            "past event, often with for and since."
        ),
        focus="Past perfect continuous (had been + -ing) for ongoing actions before another past moment, with for and since.",
        lesson_goal="Teach the past perfect continuous for duration before a past event.",
        steps=(
            ("open", "Introduce the past perfect continuous.", (
                "Greet the learner. Explain in two sentences that the past perfect "
                "continuous uses had been plus verb-ing to show something had been "
                "happening for a while before another past action. Ask how long they "
                "had been doing their current job or course before a recent change."
            )),
            ("had_been_ing", "Teach had been + verb-ing.", (
                "Use the learner's answer to explain that had been is the same for "
                "every subject and is followed by verb-ing. Ask them to say one sentence "
                "about something a colleague had been working on before a deadline last week."
            )),
            ("for_since", "Teach for and since with the form.", (
                "Introduce for with a length of time and since with a starting point "
                "with the past perfect continuous. Ask for one sentence using since and "
                "had been plus verb-ing."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has shown the pattern at least once, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_cloze_past_perf_cont",
            "listen_mcq_past_perf_cont",
            "write_past_perf_cont_sentences",
            "speak_past_perf_cont_events",
        ),
        topic_overrides=(
            "Past perfect continuous duration",
            "Listening for past perfect continuous",
            "Write past perfect continuous sentences",
            "Say what had been happening before a past moment",
        ),
        generation_instructions=(
            (
                "Write a 4-5 blank connected passage about a busy week where several "
                "actions had been going on for a period before a key moment. Focus on "
                "the past perfect continuous with had been + verb-ing and for or since."
            ),
            (
                "Generate a 70-100 word spoken passage about a person describing a past "
                "situation where longer actions had been in progress, using had been, "
                "for, and since before another event happened."
            ),
            (
                "Ask for affirmative past perfect continuous sentences using I, he, and "
                "she, describing what had been happening for a period before another "
                "past action, with for or since."
            ),
            (
                "Ask the learner to say short past perfect continuous sentences about "
                "what had been happening before a past moment using had been and verb-ing."
            ),
        ),
        widget_requirements=(
            (
                "Always include base_verb for every blank so the learner forms had been "
                "+ verb-ing. Do not repeat base_verb inline in the passage after each "
                "___ — the UI shows it separately."
            ),
            (
                "Generate 3-4 MCQ items with prompt, options, correct_index, and "
                "explanation."
            ),
            None,
            (
                "Create exactly 3 speaking prompts: one with I, one with he, and one with "
                "she. Include speaking_duration_seconds: 45."
            ),
        ),
    ),
    (13, 1): DaySpec(
        title="Third Conditional - Regrets About the Past",
        description=(
            "Learners use the third conditional (if + past perfect, would have + "
            "past participle) to talk about unreal past situations and their "
            "results (If I had known, I would have helped)."
        ),
        focus="Third conditional with if + past perfect and would have + past participle for unreal past situations.",
        lesson_goal="Teach the third conditional for regrets and unreal past situations.",
        steps=(
            ("open", "Introduce the third conditional.", (
                "Greet the learner. Explain in two sentences that the third conditional "
                "talks about an unreal past situation and its imagined result, using if + "
                "past perfect and would have + past participle. Ask what they would have "
                "done differently last year if they had had more time."
            )),
            ("if_clause_pp", "Teach the past perfect in the if-clause.", (
                "Use the learner's idea to explain that the if-clause uses had plus a "
                "past participle (If I had studied..., If we had left...). Ask them to "
                "finish 'If I had known earlier, ...' with their own result."
            )),
            ("would_have", "Teach would have + past participle.", (
                "Show that the result clause uses would have plus a past participle. "
                "Ask them to make one sentence with would have about a choice they did "
                "not make in the past."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has shown the pattern at least once, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_error_spot_third_conditional",
            "listen_cloze_third_conditional",
            "write_error_corr_third_conditional",
            "speak_read_aloud_third_conditional",
        ),
        topic_overrides=(
            "Spot third conditional errors",
            "Listen and fill third conditional forms",
            "Correct third conditional mistakes",
            "Read third conditional passage aloud",
        ),
        generation_instructions=(
            (
                "Generate a 5-sentence passage about regrets and different past choices. "
                "Each sentence must contain exactly one grammatical error, so there are "
                "exactly 5 error tokens. Make mistakes diverse across third-conditional "
                "usage: wrong tense in the if-clause, missing would have, will instead "
                "of would have, wrong past participle after would have, and a "
                "condition-marker mismatch."
            ),
            (
                "Listen to the short regrets audio, then complete the paraphrased notes "
                "with the missing third-conditional verb phrases from the clip."
            ),
            (
                "Give the learner 3 sentences that each contain one third conditional "
                "error — mix wrong tense in the if-clause and would have mistakes. Ask "
                "the learner to rewrite each sentence correctly."
            ),
            (
                "Give the learner a connected third conditional narrative passage of "
                "55-70 words to read aloud, describing several unreal past situations and "
                "their imagined results."
            ),
        ),
        static_payload_index=1,
        static_payload=THIRD_COND_LISTEN_PAYLOAD,
    ),
    (13, 2): DaySpec(
        title="Causative Have & Get - Arranging for Others to Do Things",
        description=(
            "Learners use causative have and get (have something done, get someone "
            "to do something) to say they arrange for another person to perform an "
            "action, not that they do it themselves."
        ),
        focus="Causative have/get: have + object + past participle and get + object + to-infinitive for arranged actions.",
        lesson_goal="Teach causative have and get for arranged actions.",
        steps=(
            ("open", "Introduce causative have and get.", (
                "Greet the learner. Explain in two sentences that causative have and get "
                "show you arrange for someone else to do something (I had my hair cut, I "
                "got him to check it). Ask them to tell you one thing they had done for "
                "them recently by a professional or service."
            )),
            ("have_done", "Teach have + object + past participle.", (
                "Use the learner's example to confirm have + object + past participle "
                "(She had her laptop repaired). Ask them to make one present sentence "
                "about something they need to have done this week."
            )),
            ("get_to", "Teach get + object + to-infinitive.", (
                "Introduce get + someone + to + verb for persuading or arranging (I got "
                "my colleague to help). Ask for one sentence with got and to about a "
                "task someone else did for them."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has shown the pattern at least once, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_comp_mcq_causative",
            "listen_dictation_causative",
            "write_sent_trans_causative",
            "speak_timed_causative",
        ),
        topic_overrides=(
            "Understand causative arrangements in context",
            "Hear causative have/get chunks",
            "Rewrite into causative have or get",
            "Describe arranged services with causative forms",
        ),
        generation_instructions=(
            (
                "Write a 60-75 word passage about someone arranging services (repairs, "
                "deliveries, appointments) using causative have and get naturally. Then "
                "ask comprehension questions and include one item on the correct causative form."
            ),
            (
                "Generate a 35-45 word audio script of 4 short sentences with varied "
                "causative forms (had my phone fixed, got them to send it, is having the "
                "report checked). The learner types each sentence exactly as heard."
            ),
            (
                "Give the learner 3 active sentences they did themselves and ask them to "
                "rewrite each using causative have or get, keeping the same meaning."
            ),
            (
                "Ask the learner to say one causative sentence per prompt about services "
                "or tasks arranged for them, using have + object + past participle or "
                "get + object + to-infinitive."
            ),
        ),
    ),
    (13, 3): DaySpec(
        title="Reduced & Non-Defining Relative Clauses",
        description=(
            "Learners add extra information with non-defining relative clauses "
            "(commas + who/which) and shorten defining clauses by dropping the "
            "pronoun or using a participle phrase (the report we sent, the woman "
            "sitting near the door)."
        ),
        focus="Non-defining relative clauses with commas and reduced defining clauses (omitted pronoun, participle phrases).",
        lesson_goal="Teach non-defining and reduced relative clauses.",
        steps=(
            ("open", "Introduce non-defining and reduced clauses.", (
                "Greet the learner. Explain in two sentences that non-defining clauses add "
                "extra information with commas, and reduced clauses shorten a relative "
                "clause by dropping the pronoun or using -ing/-ed. Ask them to describe a "
                "colleague using a short clause after the noun."
            )),
            ("non_defining", "Teach commas with extra information.", (
                "Confirm their sentence. Explain that non-defining clauses use commas and "
                "who or which for extra detail (My manager, who lives nearby, ...). Ask "
                "them to add a non-defining clause about a thing they use every day."
            )),
            ("wrap_up", "Move to practice.", (
                "Confirm the pattern with a short example (The app, which I use daily, "
                "is fast. The person sitting there is new.) and then ask only: Ready to "
                "try the practice task?"
            )),
        ),
        activity_ids=(
            "read_word_match_relative_reduced",
            "listen_mcq_relative_reduced",
            "write_open_sent_relative_reduced",
            "speak_pic_desc_relative_reduced",
        ),
        topic_overrides=(
            "Match clause types to their punctuation or form",
            "Hearing reduced and non-defining clauses",
            "Write sentences with reduced or non-defining clauses",
            "Describe a scene with reduced relative clauses",
        ),
        generation_instructions=(
            (
                "Ask the learner to match each sentence stub to whether it needs commas "
                "(non-defining), can drop the pronoun (reduced defining), or uses a "
                "participle phrase."
            ),
            (
                "Generate a 35-45 word description mixing one non-defining clause with "
                "commas and at least one reduced clause. Include comprehension questions."
            ),
            (
                "Ask for three short sentences: one non-defining with commas, one reduced "
                "defining without the pronoun, and one with a participle phrase after the noun."
            ),
            (
                "Ask the learner to describe a simple scene aloud using at least one "
                "non-defining clause and one reduced clause."
            ),
        ),
    ),
    (13, 4): DaySpec(
        title="Reporting Verbs & Patterns - Admit, Deny, Suggest & More",
        description=(
            "Learners report what people said using reporting verbs and the "
            "right pattern after each verb (admit + -ing, suggest + clause, "
            "promise + to-infinitive), not only said and told."
        ),
        focus="Reporting verbs with correct patterns: admit/deny + -ing, suggest + clause, promise/refuse + to-infinitive.",
        lesson_goal="Teach reporting verbs and the patterns that follow them.",
        steps=(
            ("open", "Introduce reporting verbs.", (
                "Greet the learner. Explain in two sentences that reporting verbs like "
                "admit, deny, suggest, and promise change the grammar after them (He "
                "admitted making a mistake, She promised to help). Ask them to tell you "
                "something a colleague suggested recently."
            )),
            ("verb_patterns", "Teach verb + pattern combinations.", (
                "Confirm their sentence. Explain that admit and deny take -ing, suggest "
                "often takes a that-clause, and promise takes to + verb. Ask them to "
                "report one more idea using denied or promised with the correct pattern."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has used a reporting verb with the right pattern at least "
                "once, ask only: Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_cloze_reporting_verbs",
            "listen_infer_reporting_verbs",
            "write_para_reporting_verbs",
            "speak_roleplay_reporting_verbs",
        ),
        topic_overrides=(
            "Fill reporting verb pattern blanks",
            "Infer the reporting verb and pattern",
            "Write a paragraph with varied reporting verbs",
            "Pass on a message with reporting verbs",
        ),
        generation_instructions=(
            (
                "Write a short 4-5 sentence passage reporting a meeting, with blanks for "
                "reporting verbs and the correct form after each (admitted, suggested, "
                "promised to, denied)."
            ),
            (
                "Generate a 35-45 word audio clip where someone reports what others said "
                "using varied reporting verbs and patterns. Ask the learner to infer the "
                "original meaning and verb choice."
            ),
            (
                "Ask the learner to write a 3-4 sentence paragraph reporting a short "
                "discussion using at least three different reporting verbs with correct "
                "patterns after each."
            ),
            (
                "Set up a roleplay where the learner passes on what several people said "
                "using reporting verbs (she suggested that, he promised to, they denied) in "
                "2-3 connected sentences."
            ),
        ),
    ),
    (13, 5): DaySpec(
        title="Wish & Regret - I Wish, If Only & Should Have",
        description=(
            "Learners express wishes about the present or past and regrets with "
            "I wish / If only + past simple or past perfect, and should have + "
            "past participle for things they regret not doing."
        ),
        focus="Wish and regret: I wish/If only + past for present regrets; past perfect for past regrets; should have for advice regrets.",
        lesson_goal="Teach wish, if only, and should have for regrets.",
        steps=(
            ("open", "Introduce wish and regret forms.", (
                "Greet the learner and note this is the regrets day of grammar week. "
                "Explain in two sentences that I wish plus past simple talks about "
                "present regrets, and should have plus past participle regrets past "
                "actions not taken. Ask what they wish were different about their routine."
            )),
            ("wish_should_have", "Teach wish vs should have.", (
                "Confirm their answer. Explain that I wish I had... looks back and should "
                "have shows a past action they regret not doing. Ask them to say one "
                "should have sentence about a small mistake last month."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has used the pattern at least once, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_tfng_wish_regret",
            "listen_shadow_wish_regret",
            "write_email_wish_regret",
            "speak_smalltalk_wish_regret",
        ),
        topic_overrides=(
            "Wishes and regrets in text",
            "Repeat wish / should have phrases in speech",
            "Email a friend about a wish or regret",
            "Casual chat about wishes and regrets",
        ),
        generation_instructions=(
            (
                "Write a short profile rich in I wish, If only, and should have sentences "
                "about present and past regrets. Then give True / False / Not Given "
                "statements about what the person wishes or regrets."
            ),
            (
                "Generate a short natural monologue (about 20 seconds) with I wish and "
                "should have phrases blended into connected speech for shadowing."
            ),
            (
                "Ask the learner to write a short email to a friend expressing one wish "
                "and one regret using I wish and should have correctly."
            ),
            (
                "Set up casual small talk where the learner answers with I wish and "
                "should have naturally."
            ),
        ),
    ),
    (13, 6): DaySpec(
        title="Formal Linkers & Nuance - Moreover, Nevertheless & In Addition",
        description=(
            "Learners connect ideas in more formal writing and speech with "
            "linkers such as moreover, nevertheless, in addition, and on the "
            "other hand, choosing the linker that matches the relationship."
        ),
        focus="Formal linkers moreover, nevertheless, in addition, and on the other hand for reason, contrast, and addition.",
        lesson_goal="Teach formal linkers for nuanced connections between ideas.",
        steps=(
            ("open", "Introduce formal linkers.", (
                "Greet the learner and note this is the final wrap-up day of grammar week. "
                "Explain in two sentences that formal linkers like moreover and nevertheless "
                "show addition or contrast in essays and reports. Ask them to finish "
                "'Nevertheless, ___.'"
            )),
            ("addition_contrast", "Teach moreover vs nevertheless.", (
                "Confirm their sentence. Explain that moreover and in addition add a point, "
                "while nevertheless and on the other hand show contrast. Ask them to make "
                "one sentence with moreover linking two ideas."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has used a formal linker correctly at least once, ask "
                "only: Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_context_mcq_formal_linkers",
            "listen_retell_formal_linkers",
            "write_paraphrase_formal_linkers",
            "speak_present_formal_linkers",
        ),
        topic_overrides=(
            "Formal linkers in a short article",
            "Retell a formal mini-talk",
            "Paraphrase with formal linkers",
            "Short talk using formal linkers",
        ),
        generation_instructions=(
            (
                "Write a short formal paragraph (policy or report style) using moreover, "
                "nevertheless, and in addition. Then ask MCQ questions about which linker "
                "fits a gap."
            ),
            (
                "Generate a 40-50 word formal audio clip with clear linker phrases. Ask "
                "the learner to retell the main points using at least two formal linkers."
            ),
            (
                "Give informal sentences and ask the learner to join or rewrite them using "
                "moreover, nevertheless, or on the other hand."
            ),
            (
                "Ask the learner to give a 45-second mini presentation on a work or "
                "study topic using at least two formal linkers naturally."
            ),
        ),
    ),
}
# fmt: on

# Communication week 14 (mirror week 10)
_COMM_SPECS: list[DaySpec] = [
    DaySpec(
        title="Conflict Resolution & Middle Ground",
        description=(
            "Learners resolve disagreements by acknowledging both sides, "
            "proposing middle-ground options, and confirming what both people "
            "can accept (I understand your point / Could we try...?)."
        ),
        focus="Resolve conflict: acknowledge both sides, propose middle-ground options, and confirm shared agreement.",
        lesson_goal="Teach conflict resolution and finding middle ground.",
        steps=(
            ("open", "Introduce conflict resolution.", (
                "Welcome the learner to communication week. Explain in two sentences that "
                "resolving conflict means acknowledging both views and finding a middle "
                "ground both can accept. Ask them to describe one disagreement they handled "
                "or want to handle better."
            )),
            ("middle_ground", "Teach middle-ground phrases.", (
                "React warmly. Explain phrases like 'I see your point' and 'Could we meet "
                "in the middle by...?' Ask them to suggest one compromise for the "
                "situation they named."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has acknowledged a view and offered a compromise, ask "
                "only: Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_comp_mcq_conflict_resolution",
            "listen_mcq_conflict_resolution",
            "write_sent_trans_conflict_resolution",
            "speak_roleplay_conflict_resolution",
        ),
        topic_overrides=(
            "Conflict resolution in messages",
            "Listening to a disagreement resolved",
            "Polite conflict-resolution phrases",
            "Roleplay resolving a conflict",
        ),
        generation_instructions=(
            (
                "Write a short exchange where two people disagree, acknowledge each other's "
                "points, and agree on middle-ground next steps. Ask comprehension questions."
            ),
            (
                "Generate a 35-45 word dialogue resolving a conflict with acknowledgement "
                "and a compromise. Include MCQs on each side's concern and the agreement."
            ),
            (
                "Give 3 blunt conflicting statements and ask the learner to rewrite each "
                "using acknowledgement and middle-ground phrases."
            ),
            (
                "Set up a roleplay where the learner de-escalates a disagreement and "
                "proposes a compromise both sides can accept."
            ),
        ),
    ),
    DaySpec(
        title="Giving Constructive Feedback",
        description=(
            "Learners give constructive feedback using a clear structure: "
            "positive point, specific issue, suggestion, and supportive close "
            "(I liked... / One thing to improve... / You could try...)."
        ),
        focus="Give constructive feedback with positive point, specific issue, suggestion, and supportive tone.",
        lesson_goal="Teach giving constructive feedback in a supportive structure.",
        steps=(
            ("open", "Introduce constructive feedback.", (
                "Welcome the learner to Day 2 of communication week. Explain in two "
                "sentences that constructive feedback balances praise with one clear "
                "suggestion. Ask them to tell you about feedback they found helpful."
            )),
            ("feedback_structure", "Teach the feedback structure.", (
                "Use their example to model 'I liked... / One area to develop is... / "
                "You could try...'. Ask them to give brief constructive feedback on a "
                "sample: 'A teammate submitted a report late.'"
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has praised and suggested an improvement, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_tfng_constructive_feedback",
            "listen_infer_constructive_feedback",
            "write_email_constructive_feedback",
            "speak_interview_constructive_feedback",
        ),
        topic_overrides=(
            "Constructive feedback in writing",
            "Infer tone in feedback conversations",
            "Write constructive feedback",
            "React with constructive feedback in chat",
        ),
        generation_instructions=(
            (
                "Write a short message giving constructive feedback on work quality with "
                "a positive line, one issue, and a suggestion. Then True/False/Not Given items."
            ),
            (
                "Generate a conversation where a manager gives constructive feedback. Ask "
                "the learner to infer tone and the main suggestion."
            ),
            (
                "Ask the learner to write feedback to a colleague with praise, one issue, "
                "and a concrete suggestion."
            ),
            (
                "Run a mini interview where the learner gives constructive feedback on "
                "three short scenarios in full sentences."
            ),
        ),
    ),
    DaySpec(
        title="Pros, Cons & Recommending an Option",
        description=(
            "Learners compare options by listing pros and cons, weighing "
            "trade-offs, and recommending one choice with clear reasons."
        ),
        focus="Compare options with pros and cons, weigh trade-offs, and recommend one choice with reasons.",
        lesson_goal="Teach weighing pros and cons and recommending an option.",
        steps=(
            ("open", "Introduce pros, cons, and recommendations.", (
                "Greet the learner. Explain in two sentences that comparing options means "
                "listing pros and cons and then recommending the best choice with reasons. "
                "Ask them to compare two tools or places they know."
            )),
            ("structure_order", "Teach listing and recommending.", (
                "Confirm their answer. Introduce signposting (on the one hand, however, "
                "overall I would recommend) and ask them to name one pro and one con."
            )),
            ("add_recommendation", "Add a clear recommendation.", (
                "Show how to end with a recommendation and reason (Overall, I would "
                "choose X because...). Ask what they would recommend and why in one sentence."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has listed a pro/con and a recommendation, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_structure_pros_cons",
            "listen_retell_pros_cons",
            "write_para_pros_cons",
            "speak_opinion_pros_cons",
        ),
        topic_overrides=(
            "Identify pros, cons, and recommendation sections",
            "Retell an options comparison",
            "Write a pros-cons recommendation paragraph",
            "State a recommendation aloud",
        ),
        generation_instructions=(
            (
                "Provide a 3-paragraph text comparing two options and ask the learner to "
                "label paragraphs as Pros, Cons, or Recommendation."
            ),
            (
                "Generate a short audio comparing two options with pros, cons, and a final "
                "recommendation. Ask the learner to retell the recommendation and main reason."
            ),
            (
                "Ask the learner to write a paragraph comparing two options and recommending "
                "one with reasons."
            ),
            (
                "Ask the learner to speak for 45 seconds recommending one option with pros, "
                "cons, and a clear conclusion."
            ),
        ),
    ),
    DaySpec(
        title="Leading a Short Meeting",
        description=(
            "Learners lead a brief meeting: open with purpose, guide "
            "agenda items, invite input, and close with actions and owners "
            "(Let's start with... / Any questions on...? / Next steps are...)."
        ),
        focus="Lead a short meeting: purpose, agenda, invitations to speak, and action-focused close.",
        lesson_goal="Teach leading a short meeting with clear structure.",
        steps=(
            ("open", "Introduce leading a meeting.", (
                "Greet the learner. Explain in two sentences that leading a short meeting "
                "means stating the purpose, moving through points, and ending with clear "
                "actions. Ask them to describe a meeting they led or joined recently."
            )),
            ("agenda_actions", "Teach open and close phrases.", (
                "Confirm their answer. Introduce phrases like 'Let's kick off with...' and "
                "'The action items are...'. Ask them to open a one-minute project check-in."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has used an opening or action phrase, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_comp_mcq_leading_meeting",
            "listen_mcq_leading_meeting",
            "write_bullets_to_para_leading_meeting",
            "speak_roleplay_leading_meeting",
        ),
        topic_overrides=(
            "Leading a meeting in writing",
            "Listening to a short meeting",
            "Turn notes into a meeting summary",
            "Roleplay leading a meeting",
        ),
        generation_instructions=(
            (
                "Write a short meeting transcript with purpose, two agenda items, and "
                "action owners. Ask comprehension questions."
            ),
            (
                "Generate a 35-45 word meeting clip with opening, two points, and closing "
                "actions. Include MCQs on purpose and next steps."
            ),
            (
                "Give bullet notes from a meeting and ask the learner to write a clear "
                "summary paragraph with action items."
            ),
            (
                "Set up a roleplay where the learner opens a short meeting, invites one "
                "comment, and closes with next steps."
            ),
        ),
    ),
    DaySpec(
        title="Handling Objections",
        description=(
            "Learners respond to objections calmly: acknowledge the concern, "
            "clarify, respond with evidence or benefit, and check agreement "
            "(I understand why... / That's a fair point / What would help is...)."
        ),
        focus="Handle objections by acknowledging, clarifying, responding with evidence, and checking agreement.",
        lesson_goal="Teach handling objections professionally.",
        steps=(
            ("open", "Introduce handling objections.", (
                "Greet the learner. Explain in two sentences that handling objections "
                "starts by acknowledging the concern before giving a reasoned response. "
                "Ask them to recall an objection they heard at work or school."
            )),
            ("respond_objection", "Teach acknowledge-then-respond.", (
                "Model 'That's a fair point' plus a reason or benefit. Ask them to respond "
                "to: 'It sounds too expensive.'"
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has acknowledged and responded to an objection, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_tfng_handling_objections",
            "listen_infer_handling_objections",
            "write_idea_para_handling_objections",
            "speak_pic_desc_handling_objections",
        ),
        topic_overrides=(
            "Objection handling in text",
            "Infer concerns behind objections",
            "Write a response to objections",
            "Explain handling an objection aloud",
        ),
        generation_instructions=(
            (
                "Write a short sales or project update with two objections and calm responses. "
                "Then True/False/Not Given items."
            ),
            (
                "Generate a dialogue with two objections and nuanced responses. Ask inference "
                "questions about concerns and agreement."
            ),
            (
                "Ask the learner to write a paragraph responding to two objections about an idea."
            ),
            (
                "Ask the learner to describe aloud how they would handle an objection to a "
                "proposal, using acknowledge-then-respond language."
            ),
        ),
    ),
    DaySpec(
        title="Stakeholder Communication",
        description=(
            "Learners tailor messages for different stakeholders: adjust "
            "detail, tone, and focus (executive summary vs team detail) while "
            "keeping the core message consistent."
        ),
        focus="Stakeholder communication: adjust detail, tone, and focus for different audiences while keeping core facts.",
        lesson_goal="Teach stakeholder-aware communication.",
        steps=(
            ("open", "Introduce stakeholder communication.", (
                "Greet the learner. Explain in two sentences that stakeholders need different "
                "levels of detail and tone — leaders want outcomes, teams want steps. Ask "
                "which audience is harder for them to write for."
            )),
            ("tone_detail", "Teach tailoring tone and detail.", (
                "Confirm their answer. Contrast a one-line executive update with a fuller "
                "team message. Ask them to give one headline for a leader and one detail for "
                "a teammate."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has tailored tone or detail for two audiences, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_tone_id_stakeholder_w14",
            "listen_tone_stakeholder_w14",
            "write_paraphrase_stakeholder_w14",
            "speak_smalltalk_stakeholder_w14",
        ),
        topic_overrides=(
            "Identify stakeholder-appropriate tone",
            "Hear tone shifts for stakeholders",
            "Rewrite for a different stakeholder",
            "Small talk with stakeholder-aware replies",
        ),
        generation_instructions=(
            (
                "Provide two short messages on the same update for different stakeholders. "
                "Ask which is for a senior leader vs a project team."
            ),
            (
                "Generate audio with two versions of the same news for different audiences. "
                "Ask tone and detail questions."
            ),
            (
                "Give a detailed team update and ask the learner to rewrite a 2-sentence "
                "executive version."
            ),
            (
                "Set up small talk where the learner answers the same news differently for "
                "a manager vs a peer."
            ),
        ),
    ),
    DaySpec(
        title="Facilitating Discussion",
        description=(
            "Learners facilitate discussion: set topic, invite quieter voices, "
            "paraphrase contributions, and summarise before deciding "
            "(Let's hear from... / So what I'm hearing is... / To sum up...)."
        ),
        focus="Facilitate discussion: set topic, invite voices, paraphrase, and summarise before a decision.",
        lesson_goal="Teach facilitating group discussion.",
        steps=(
            ("open", "Introduce facilitating discussion.", (
                "Greet the learner. Explain in two sentences that facilitating means guiding "
                "the topic, inviting others, and summarising before deciding. Ask when they "
                "last joined a group discussion they could have guided more."
            )),
            ("invite_summarise", "Teach invite and summarise phrases.", (
                "Introduce 'Let's hear from...' and 'So what I'm hearing is...'. Ask them to "
                "invite a quiet member and summarise two ideas in one sentence."
            )),
            ("wrap_up", "Move to practice.", (
                "If the learner has invited or summarised, ask only: "
                "Ready to try the practice task?"
            )),
        ),
        activity_ids=(
            "read_structure_facilitating",
            "listen_retell_facilitating",
            "write_email_facilitating",
            "speak_present_facilitating",
        ),
        topic_overrides=(
            "Structure of a facilitated discussion",
            "Retell a facilitated discussion clip",
            "Email summarising a discussion",
            "Present a short facilitated summary",
        ),
        generation_instructions=(
            (
                "Provide a 3-part facilitated discussion transcript (open, contributions, "
                "summary) and ask the learner to label each part."
            ),
            (
                "Generate audio of someone facilitating a short discussion. Ask retell of "
                "invitations and summary."
            ),
            (
                "Ask the learner to write an email summarising a discussion with next steps."
            ),
            (
                "Ask the learner to deliver a 45-second spoken summary after a facilitated "
                "discussion scenario."
            ),
        ),
    ),
]
for i, spec in enumerate(_COMM_SPECS):
    DAY_SPECS[(14, i)] = spec

# Vocabulary week 15 (mirror week 11)
_VOCAB_TOPICS = [
    (
        "Science & Research - Hypothesis, Data & Experiment",
        "science and research (hypothesis, experiment, data, evidence, peer review)",
        "hypothesis, experiment, data, evidence, peer review",
        "science and research",
        "science_research",
        "a lab or research setting",
        "hypothesis, data, evidence",
        "research lab with scientists reviewing data on screens",
    ),
    (
        "Arts & Creativity - Exhibition, Medium & Inspiration",
        "arts and creativity (exhibition, medium, inspiration, curator, portfolio)",
        "exhibition, medium, inspiration, curator, portfolio",
        "arts and creativity",
        "arts_creativity",
        "a gallery or studio",
        "exhibition, medium, inspiration",
        "art gallery with paintings and a sculptor at work",
    ),
    (
        "Ethics & Global Issues - Justice, Rights & Responsibility",
        "ethics and global issues (justice, rights, inequality, responsibility, campaign)",
        "justice, rights, inequality, responsibility, campaign",
        "ethics and global issues",
        "ethics_global",
        "a community or policy context",
        "justice, rights, responsibility",
        "community meeting about a social campaign poster",
    ),
    (
        "Business & Economics - Revenue, Market & Investment",
        "business and economics (revenue, market, investment, budget, profit)",
        "revenue, market, investment, budget, profit",
        "business and economics",
        "business_economics",
        "a business or market scene",
        "revenue, market, investment",
        "office dashboard showing market trends and budget charts",
    ),
    (
        "Media Literacy - Source, Bias & Fact-check",
        "media literacy (source, bias, fact-check, headline, credible)",
        "source, bias, fact-check, headline, credible",
        "media literacy",
        "media_literacy",
        "news and online media",
        "source, bias, credible",
        "person comparing two news headlines on a laptop",
    ),
    (
        "Leadership & Influence - Vision, Delegate & Motivate",
        "leadership and influence (vision, delegate, motivate, stakeholder, initiative)",
        "vision, delegate, motivate, stakeholder, initiative",
        "leadership and influence",
        "leadership_influence",
        "a team leadership moment",
        "vision, delegate, motivate",
        "team leader motivating colleagues around a shared goal board",
    ),
    (
        "Review & Word Building - Consolidate the week's vocab",
        "the week's B1+ vocabulary across science, arts, ethics, business, media, and leadership",
        "review words from the week",
        "review and word building",
        "review_w15",
        "mixed professional contexts",
        "review, prefix, suffix",
        "collage of work, lab, gallery, and news scenes",
    ),
]

def _vocab_day_spec(
    title: str,
    domain_desc: str,
    word_list: str,
    topic_short: str,
    slug: str,
    scene: str,
    sample_words: str,
    image_alt: str,
    *,
    day_index: int,
) -> DaySpec:
    """Build vocab day spec; activity layout mirrors week 11 same day."""
    w11 = _week_days(11)[day_index]
    old_slugs = ["environment", "education", "culture", "work", "news", "values", "review_w11"]
    old = old_slugs[day_index]
    id_templates = tuple(a.id.replace(old, slug) for a in w11.activities)

    open_instr = (
        f"Welcome the learner to vocabulary week. Explain in two sentences that we "
        f"use words like {word_list.split(',')[0].strip()} and "
        f"{word_list.split(',')[1].strip() if ',' in word_list else 'related terms'} "
        f"to talk about {topic_short}. Ask them to use one of today's words in a sentence."
    )
    if day_index > 0:
        open_instr = (
            f"Greet the learner. Explain in two sentences that {topic_short} vocabulary "
            f"includes {word_list}. Ask them what they have read or heard recently about "
            f"{topic_short}."
        )

    return DaySpec(
        title=title,
        description=(
            f"Learners build vocabulary for {domain_desc} and use the words in "
            f"reading, listening, writing, and speaking tasks at B1+ level."
        ),
        focus=f"Vocabulary for {domain_desc}.",
        lesson_goal=f"Teach {topic_short} vocabulary.",
        steps=(
            ("open", f"Introduce {topic_short} words.", open_instr),
            (
                "more_words",
                f"Practise more {topic_short} words.",
                (
                    f"Confirm strong words. Ask what another key word means, then preview "
                    f"today's reading, listening, writing, and speaking tasks about "
                    f"{topic_short}."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "If the learner has used a target word correctly, ask only: "
                    "Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=id_templates,
        topic_overrides=(
            f"{title.split(' - ')[0]} Vocabulary",
            f"A talk about {topic_short}",
            f"{topic_short} vocabulary in writing",
            f"Describe {scene}",
        ),
        generation_instructions=(
            (
                f"Ask the learner to match {topic_short} words ({sample_words}) to short "
                f"definitions or context clues."
            ),
            (
                f"Generate a short scenario where someone discusses {topic_short}, using "
                f"at least three target words. Ask comprehension questions."
            ),
            (
                f"Give wordy descriptions of {topic_short} ideas and ask the learner to "
                f"rewrite each using precise vocabulary ({sample_words})."
            ),
            (
                f"Ask the learner to describe a photo of {image_alt} aloud using "
                f"{topic_short} vocabulary naturally."
            ),
        ),
    )


for i, topic in enumerate(_VOCAB_TOPICS):
    DAY_SPECS[(15, i)] = _vocab_day_spec(*topic, day_index=i)

# Confidence week 16 (mirror week 12)
_CONF_SPECS = [
    (
        "Facilitating Difficult Conversations",
        "facilitate difficult conversations calmly: set ground rules, name the issue, and invite respectful turns",
        "difficult_conversations",
        "read_comp_mcq_difficult_conv",
        "listen_shadow_difficult_conv",
        "write_sent_trans_difficult_conv",
        "speak_read_aloud_difficult_conv",
    ),
    (
        "Counterarguments & Rebuttals",
        "respond to counterarguments with calm rebuttals: acknowledge, refute with evidence, and restate your point",
        "counterarguments",
        "read_tone_id_counterarguments",
        "listen_mcq_counterarguments",
        "write_timed_counterarguments",
        "speak_timed_counterarguments",
    ),
    (
        "Vision & Long-Term Narrative",
        "share a vision and long-term narrative with clear future focus and realistic trade-offs",
        "vision_narrative",
        "read_comp_mcq_vision",
        "listen_tone_vision",
        "write_sent_trans_vision",
        "speak_pic_desc_vision",
    ),
    (
        "Giving & Receiving Critical Feedback",
        "give and receive critical feedback without defensiveness: listen, clarify, and respond constructively",
        "critical_feedback",
        "read_tone_id_critical_feedback",
        "listen_shadow_critical_feedback",
        "write_timed_critical_feedback",
        "speak_smalltalk_critical_feedback",
    ),
    (
        "Strong Close & Call to Action",
        "close talks with a strong summary and call to action that tells the audience what to do next",
        "strong_close",
        "read_comp_mcq_strong_close",
        "listen_mcq_strong_close",
        "write_sent_trans_strong_close",
        "speak_pic_desc_strong_close",
    ),
    (
        "Presentation with Brief Q&A",
        "deliver a short presentation and handle brief Q&A with calm, structured answers",
        "presentation_qa",
        "read_tone_id_presentation_qa",
        "listen_tone_presentation_qa",
        "write_timed_presentation_qa",
        "speak_present_presentation_qa",
    ),
    (
        "Full Confidence Showcase (B1+)",
        "integrate B1+ confidence skills in one showcase: clear argument, calm rebuttal, vision, and strong close",
        "showcase_w16",
        "read_comp_mcq_showcase_w16",
        "listen_shadow_showcase_w16",
        "write_timed_showcase_w16",
        "speak_debate_showcase_w16",
    ),
]

for i, (title, focus_desc, slug, *act_ids) in enumerate(_CONF_SPECS):
    w12 = _week_days(12)[i]
    DAY_SPECS[(16, i)] = DaySpec(
        title=title,
        description=(
            f"Learners build confidence to {focus_desc}, using the same "
            f"read-listen-write-speak sequence as earlier confidence days at B1+ level."
        ),
        focus=focus_desc.capitalize() + ".",
        lesson_goal=f"Build confidence to {focus_desc.split(':')[0]}.",
        steps=(
            (
                "open",
                "Frame the skill as small steps.",
                (
                    "Welcome the learner to confidence week. Explain in two sentences that "
                    f"{focus_desc.split(':')[0]} becomes easier with preparation and small "
                    "steps. Ask them to name one situation where they want more confidence."
                ),
            ),
            (
                "preview",
                "Preview the day and reassure.",
                (
                    "Affirm their answer warmly. Preview today's read, listen, write, and "
                    "speak tasks that practise this skill in a supportive way."
                ),
            ),
            (
                "wrap_up",
                "Move to practice.",
                (
                    "Once the learner sounds ready, ask only: Ready to try the practice task?"
                ),
            ),
        ),
        activity_ids=tuple(act_ids),
        topic_overrides=tuple(a.task.topic_override for a in w12.activities),
        generation_instructions=tuple(
            a.task.generation_instructions.replace("B1", "B1+")
            .replace("leading a discussion", title.lower())
            .replace("Leading a group discussion", title)
            .replace("confidence showcase", "B1+ confidence showcase")
            for a in w12.activities
        ),
    )
    # Override topic_overrides and generation with tailored text for showcase
    if i == 0:
        DAY_SPECS[(16, 0)] = dataclasses.replace(
            DAY_SPECS[(16, 0)],
            topic_overrides=(
                "Difficult conversation story",
                "Calm facilitation shadowing",
                "Reframe avoidance into facilitation language",
                "Read a facilitation passage aloud",
            ),
            generation_instructions=(
                (
                    "Write a short story about someone facilitating a tense conversation: "
                    "they set ground rules, name the issue, and invite respectful turns. "
                    "Then comprehension questions."
                ),
                (
                    "Generate a warm 15-second clip inviting respectful turns in a difficult "
                    "conversation for shadowing."
                ),
                (
                    "Give 3 avoidance statements and ask the learner to reframe each into "
                    "calm facilitation language."
                ),
                (
                    "Give a 55-70 word passage about facilitating a difficult conversation "
                    "to read aloud."
                ),
            ),
        )
    elif i == 6:
        DAY_SPECS[(16, 6)] = dataclasses.replace(
            DAY_SPECS[(16, 6)],
            title="Full Confidence Showcase (B1+)",
            topic_overrides=(
                "B1+ confidence integration story",
                "Showcase shadowing clip",
                "Timed integrated confidence writing",
                "Debate-style showcase speaking",
            ),
            generation_instructions=(
                (
                    "Write an encouraging story where the speaker handles a counterargument, "
                    "states a vision, and closes with a call to action. Then MCQ comprehension."
                ),
                (
                    "Generate a confident 20-second clip mixing summary and call to action "
                    "for shadowing."
                ),
                (
                    "Ask for a timed paragraph integrating argument, rebuttal, and a strong close."
                ),
                (
                    "Set up a short debate-style speaking task where the learner rebuts one "
                    "point and ends with a call to action."
                ),
            ),
        )

# Fix confidence days 1-5 generation instructions properly
_CONF_GEN = [
    (
        ("Tone in a rebuttal", "Rebuttal listening", "Timed rebuttal writing", "Timed rebuttal speaking"),
        (
            "Provide two short arguments with counterpoints; ask which rebuttal is respectful and evidence-based.",
            "Generate audio with a claim and counterargument; ask inference questions.",
            "Ask for a timed paragraph acknowledging a counterargument then rebutting with one reason.",
            "Three timed speaking prompts to rebut calmly with evidence.",
        ),
    ),
    (
        ("Vision narrative comprehension", "Tone in a vision talk", "Vision sentence transforms", "Vision picture description"),
        (
            "Write a story about someone explaining a long-term vision with trade-offs; comprehension MCQs.",
            "Audio of a leader sharing vision; tone and detail questions.",
            "Transform vague future sentences into a clear vision statement with signposting.",
            "Describe a photo of a team planning a long-term goal using vision vocabulary.",
        ),
    ),
    (
        ("Critical feedback tone", "Receiving feedback shadow", "Timed critical feedback writing", "Critical feedback small talk"),
        (
            "Two feedback messages; identify which balances honesty and support.",
            "Short clip of receiving criticism calmly for shadowing.",
            "Timed response to critical feedback that clarifies and commits to one action.",
            "Small talk practicing thanking someone for direct feedback.",
        ),
    ),
    (
        ("Strong close comprehension", "Listening for call to action", "Closing sentence transforms", "Closing with call to action"),
        (
            "Short talk text; questions about summary and call to action.",
            "Audio ending with summary and clear next step; MCQs.",
            "Rewrite weak endings into strong closes with calls to action.",
            "Describe persuading an audience to take one specific next step.",
        ),
    ),
    (
        ("Presentation with Q&A tone", "Q&A tone listening", "Timed presentation writing", "Presentation with Q&A"),
        (
            "Identify formal presentation and Q&A tone in two excerpts.",
            "Audio of presentation plus one question; tone and content MCQs.",
            "Timed mini presentation paragraph with intro, two points, conclusion.",
            "45-second presentation excerpt plus brief answer to one audience question.",
        ),
    ),
]
for idx, (topics, gens) in enumerate(_CONF_GEN, start=1):
    spec = DAY_SPECS[(16, idx)]
    DAY_SPECS[(16, idx)] = dataclasses.replace(
        spec, topic_overrides=topics, generation_instructions=gens
    )


def build_week(week: int) -> WeekSource:
    shell = _find_band_week(week)
    days = []
    for d in range(7):
        mirror = _week_days(week - 4)[d]
        spec = DAY_SPECS[(week, d)]
        days.append(_build_day(mirror, spec))
    return dataclasses.replace(shell, week_number=_band_week(week), days=tuple(days))


def emit_cycle4() -> str:
    lines = [
        "    # ── Cycle 4 — Expanding (B2) — band weeks 5-8 ───────────────",
    ]
    for week in (13, 14, 15, 16):
        w = build_week(week)
        lines.append("    WeekSource(")
        lines.append(f"        week_number={w.week_number},")
        lines.append(f'        theme_type="{w.theme_type}",')
        lines.append(f'        cefr_level="{w.cefr_level}",')
        lines.append(
            f"        sub_level_min={w.sub_level_min}, sub_level_max={w.sub_level_max},"
        )
        lines.append("        days=(")
        for day in w.days:
            lines.extend(_emit_day(day, "            "))
        lines.append("        ),")
        lines.append("    ),")
    return "\n".join(lines)


def patch_source_file() -> None:
    path = Path(__file__).resolve().parents[1] / "app/modules/curriculum/data/source_L_B1B2.py"
    text = path.read_text()
    start = text.index("    # ── Cycle 4 —")
    end = text.index("    # ── Cycle 5 —")
    new_block = emit_cycle4() + "\n\n"
    path.write_text(text[:start] + new_block + text[end:])
    print(f"Patched {path} (weeks 13-16)")


if __name__ == "__main__":
    patch_source_file()
