"""Helpers for evaluating speak-and-record submissions in the v2 sessions flow."""

from __future__ import annotations


def prompt_id(index: int) -> str:
    return f"prompt_{index}"


def recordings_by_id(user_response: dict) -> dict[str, dict]:
    """Map speak-and-record clips to item_id or turn_id keys."""
    recordings = user_response.get("recordings") or []
    if not isinstance(recordings, list):
        return {}

    by_id: dict[str, dict] = {}
    for idx, recording in enumerate(recordings, 1):
        if not isinstance(recording, dict):
            continue
        key = str(
            recording.get("item_id") or recording.get("turn_id") or prompt_id(idx)
        )
        by_id[key] = recording
    return by_id


def has_any_transcript(user_response: dict) -> bool:
    return any(
        str(recording.get("transcript") or "").strip()
        for recording in recordings_by_id(user_response).values()
    )


def build_speaking_eval_items(
    *,
    task_content: dict,
    user_response: dict,
) -> list[dict]:
    """Align task prompts with learner transcripts for evaluator prompts."""
    recordings = recordings_by_id(user_response)
    prompts = task_content.get("speaking_prompts") or []
    samples = task_content.get("sample_responses") or []
    turns = task_content.get("turns") or []

    if prompts:
        items: list[dict] = []
        for idx, prompt in enumerate(prompts, 1):
            item_id = prompt_id(idx)
            recording = recordings.get(item_id, {})
            items.append(
                {
                    "item_id": item_id,
                    "prompt": prompt,
                    "sample_response": samples[idx - 1]
                    if idx - 1 < len(samples)
                    else "",
                    "learner_transcript": str(
                        recording.get("transcript") or ""
                    ).strip(),
                    "duration_seconds": recording.get("duration_seconds"),
                }
            )
        return items

    if turns:
        user_turns = [
            t for t in turns if isinstance(t, dict) and t.get("speaker") == "user"
        ]
        sample_user = task_content.get("sample_user_responses") or []
        items = []
        for idx, turn in enumerate(user_turns, 1):
            turn_id = str(turn.get("turn_id") or prompt_id(idx))
            recording = recordings.get(turn_id, {})
            items.append(
                {
                    "turn_id": turn_id,
                    "prompt": turn.get("ai_line") or "Your reply",
                    "sample_response": sample_user[idx - 1]
                    if idx - 1 < len(sample_user)
                    else "",
                    "learner_transcript": str(
                        recording.get("transcript") or ""
                    ).strip(),
                    "duration_seconds": recording.get("duration_seconds"),
                }
            )
        return items

    # Single-prompt / read-aloud / retell modes.
    single_prompt = (
        task_content.get("speaking_prompt")
        or task_content.get("text_to_read_aloud")
        or task_content.get("passage")
        or task_content.get("retelling_prompt")
        or "Speak your response."
    )
    sample = task_content.get("sample_response") or ""
    for key in ("prompt_1", "read_aloud", "retell"):
        recording = recordings.get(key)
        if recording is not None:
            return [
                {
                    "item_id": key,
                    "prompt": single_prompt,
                    "sample_response": sample,
                    "learner_transcript": str(
                        recording.get("transcript") or ""
                    ).strip(),
                    "duration_seconds": recording.get("duration_seconds"),
                }
            ]

    # Fallback: preserve raw recordings in prompt order.
    return [
        {
            "item_id": str(
                recording.get("item_id") or recording.get("turn_id") or prompt_id(idx)
            ),
            "prompt": single_prompt,
            "sample_response": sample,
            "learner_transcript": str(recording.get("transcript") or "").strip(),
            "duration_seconds": recording.get("duration_seconds"),
        }
        for idx, recording in enumerate(recordings.values(), 1)
    ]
