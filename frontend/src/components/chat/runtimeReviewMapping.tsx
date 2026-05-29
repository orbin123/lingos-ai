"use client";

import { EvaluationWidgetRenderer } from "./evaluation/evaluation_widgets/EvaluationWidgetRenderer";
import { FinalScorecardWidget } from "./evaluation/evaluation_widgets/FinalScorecardWidget";
import type {
  ActivityEvaluation,
  EvaluationTier,
  OverallScorecard,
} from "./evaluation/source";
import { FeedbackWidgetRenderer } from "./feedback/feedback_widgets/FeedbackWidgetRenderer";
import { RagFeedbackCard } from "./feedback/feedback_widgets/RagFeedbackCard";
import type { ActivityFeedback, RagFeedback } from "./feedback/source";
import type { AnswerView } from "./teaching/source";
import {
  buildRuntimeSessionTask,
  normalizeWidgetKey,
  type AnyTaskPayload,
} from "./runtimeMapping";

const RUNTIME_ANSWER_VIEW: AnswerView = "correct";

type RuntimeScorecardPayload = {
  overall_score?: number;
  topic?: string;
  skill_name?: string;
  widget?: string;
  total?: number;
  correct_count?: number;
  answered_count?: number;
  rubric_scores?: Record<string, number>;
  sub_skill_breakdown?: Record<string, number>;
  subskill_score?: number | null;
};

type RuntimeFeedbackPayload = {
  overall_message?: string;
  widget?: string;
  errors?: Array<{
    question_id?: string;
    user_answer?: string;
    correct_answer?: string;
    why_wrong?: string;
    rule?: string;
    memory_tip?: string;
  }>;
  summary?: string;
  did_well?: string[];
  mistakes?: Array<{
    issue?: string;
    user_wrote?: string | null;
    correction?: string | null;
    rule?: string | null;
  }>;
  score?: number;
  practice_suggestion?: string;
  next_tip?: string | null;
  sub_skill_breakdown?: Record<string, number>;
};

type RuntimeFinalScorecardPayload = {
  points_earned?: Record<string, number>;
  skill_labels?: Record<string, string>;
  activities?: Array<{
    sequence?: number;
    archetype_id?: string;
    raw_score?: number;
    base_reward?: number;
  }>;
};

type RuntimeRagFeedbackPayload = {
  mentor_note?: string | null;
};

export function RuntimeEvaluationCard({
  scorecard,
  taskPayload,
  taskAnswers,
}: {
  scorecard: RuntimeScorecardPayload;
  taskPayload: AnyTaskPayload | null;
  taskAnswers?: Record<string, unknown>;
}) {
  const task = buildRuntimeSessionTask(taskPayload ?? fallbackTaskPayload(scorecard));
  const evaluation = buildActivityEvaluation(scorecard, taskPayload, taskAnswers);

  return (
    <EvaluationWidgetRenderer
      task={task}
      evaluation={evaluation}
      answerView={RUNTIME_ANSWER_VIEW}
    />
  );
}

export function RuntimeFeedbackCard({
  feedback,
  taskPayload,
}: {
  feedback: RuntimeFeedbackPayload;
  taskPayload: AnyTaskPayload | null;
}) {
  const task = buildRuntimeSessionTask(taskPayload ?? fallbackTaskPayload(feedback));
  const activityFeedback = buildActivityFeedback(feedback);

  return (
    <FeedbackWidgetRenderer
      task={task}
      feedback={activityFeedback}
      answerView={RUNTIME_ANSWER_VIEW}
    />
  );
}

export function RuntimeFinalScorecard({
  payload,
}: {
  payload: RuntimeFinalScorecardPayload;
}) {
  return (
    <FinalScorecardWidget
      scorecard={buildOverallScorecard(payload)}
      answerView={RUNTIME_ANSWER_VIEW}
    />
  );
}

export function RuntimeRagFeedback({
  payload,
}: {
  payload: RuntimeRagFeedbackPayload;
}) {
  return (
    <RagFeedbackCard
      ragFeedback={buildRagFeedback(payload)}
      answerView={RUNTIME_ANSWER_VIEW}
    />
  );
}

function buildActivityEvaluation(
  payload: RuntimeScorecardPayload,
  taskPayload: AnyTaskPayload | null,
  taskAnswers?: Record<string, unknown>,
): ActivityEvaluation {
  const rawScore = normalizeRawScore(payload.overall_score);
  const percentage = Math.round(rawScore * 10);
  const attendedLabel = buildAttendedLabel(payload, taskPayload, taskAnswers);

  return {
    taskId: taskId(taskPayload),
    evaluatorInput: {
      archetypeId: textValue(taskPayload?.archetype_id) || "runtime",
      widget: textValue(taskPayload?.task_widget) || taskPayload?.widget || "runtime",
      taskContentRef: "runtime.task_payload",
      userResponseRef: "runtime.task_answers",
    },
    outputs: {
      correct: {
        rawScore,
        percentage,
        tier: tierForScore(rawScore),
        attendedLabel,
        rubricScores: payload.rubric_scores ?? {},
        subSkillBreakdown:
          payload.sub_skill_breakdown ??
          (payload.subskill_score != null ? { grammar: Number(payload.subskill_score) } : {}),
      },
      wrong: {
        rawScore,
        percentage,
        tier: tierForScore(rawScore),
        attendedLabel,
        rubricScores: payload.rubric_scores ?? {},
        subSkillBreakdown: payload.sub_skill_breakdown ?? {},
      },
    },
  };
}

function buildActivityFeedback(payload: RuntimeFeedbackPayload): ActivityFeedback {
  const score = normalizeRawScore(payload.score);
  const mistakes = [
    ...(payload.mistakes ?? []).map((mistake) => ({
      issue: textValue(mistake.issue) || "Review this answer.",
      userWrote: nullableText(mistake.user_wrote),
      correction: nullableText(mistake.correction),
      rule: nullableText(mistake.rule),
    })),
    ...(payload.errors ?? []).map((error) => ({
      issue: textValue(error.why_wrong) || textValue(error.question_id) || "Review this answer.",
      userWrote: textValue(error.user_answer),
      correction: textValue(error.correct_answer),
      rule: textValue(error.rule) || textValue(error.memory_tip),
    })),
  ];

  return {
    taskId: "runtime-feedback",
    feedbackInput: {
      taskId: "runtime-feedback",
      evaluationRef: "runtime.scorecard",
      learnerResponseRef: "runtime.task_answers",
    },
    outputs: {
      correct: {
        score,
        summary:
          textValue(payload.summary) ||
          textValue(payload.overall_message) ||
          "Here is your activity feedback.",
        didWell: payload.did_well ?? [],
        mistakes,
        nextTip:
          nullableText(payload.next_tip) ||
          textValue(payload.practice_suggestion) ||
          "Keep practising this pattern in short answers.",
        subSkillBreakdown: payload.sub_skill_breakdown ?? {},
      },
      wrong: {
        score,
        summary:
          textValue(payload.summary) ||
          textValue(payload.overall_message) ||
          "Here is your activity feedback.",
        didWell: payload.did_well ?? [],
        mistakes,
        nextTip:
          nullableText(payload.next_tip) ||
          textValue(payload.practice_suggestion) ||
          "Keep practising this pattern in short answers.",
        subSkillBreakdown: payload.sub_skill_breakdown ?? {},
      },
    },
  };
}

function buildOverallScorecard(payload: RuntimeFinalScorecardPayload): OverallScorecard {
  const activities = (payload.activities ?? []).map((activity, index) => {
    const rawScore = normalizeRawScore(activity.raw_score);
    return {
      taskId: `${activity.archetype_id ?? "activity"}-${activity.sequence ?? index + 1}`,
      sequence: activity.sequence ?? index + 1,
      archetypeId: activity.archetype_id ?? "ACTIVITY",
      label: activityLabel(activity.archetype_id, activity.sequence ?? index + 1),
      rawScore,
      tier: tierForScore(rawScore),
      baseReward: Math.round(Number(activity.base_reward ?? rawScore)),
    };
  });

  return {
    dayId: "runtime-session",
    pointsApplied: true,
    activities: {
      correct: activities,
      wrong: activities,
    },
    pointsEarned: {
      correct: payload.points_earned ?? {},
      wrong: payload.points_earned ?? {},
    },
    skillLabels: payload.skill_labels ?? {},
  };
}

function buildRagFeedback(payload: RuntimeRagFeedbackPayload): RagFeedback {
  const note =
    nullableText(payload.mentor_note) ||
    "Nice work today. Keep practising this pattern in short daily sentences.";

  return {
    dayId: "runtime-session",
    memoryInput: {
      scorecardRef: "runtime.final_scorecard",
      activityFeedbackRefs: [],
      learnerHistoryRef: "runtime.learner_history",
    },
    outputs: {
      correct: note,
      wrong: note,
    },
  };
}

function fallbackTaskPayload(payload: {
  widget?: unknown;
  topic?: unknown;
  skill_name?: unknown;
}): AnyTaskPayload {
  return {
    widget: normalizeWidgetKey(textValue(payload.widget) || "open_text"),
    task_widget: textValue(payload.widget),
    topic: textValue(payload.topic) || textValue(payload.skill_name) || "Activity",
    task_intro: "Activity result",
    instructions: "Review your score and feedback.",
  };
}

function buildAttendedLabel(
  scorecard: RuntimeScorecardPayload,
  taskPayload: AnyTaskPayload | null,
  taskAnswers?: Record<string, unknown>,
): string {
  if (taskPayload?.widget === "speak_and_record") {
    const recordings = taskAnswers?.recordings;
    const submitted = Array.isArray(recordings)
      ? recordings.filter((row) => {
          if (typeof row !== "object" || row === null) return false;
          const transcript = (row as { transcript?: string }).transcript;
          return typeof transcript === "string" && transcript.trim().length > 0;
        }).length
      : 0;
    if (submitted > 0) {
      return submitted === 1 ? "1 recording submitted" : `${submitted} recordings submitted`;
    }
  }

  const total = Number(scorecard.total ?? 0);
  const correct = Number(scorecard.correct_count ?? 0);
  const answered = Number(scorecard.answered_count ?? 0);
  if (total > 0 && correct > 0) return `${correct} of ${total} correct`;
  if (total > 0 && answered > 0) return `${answered} of ${total} attended`;
  if (total > 0) return `${total} ${total === 1 ? "question" : "questions"} attended`;
  return "Activity submitted";
}

function normalizeRawScore(score: unknown): number {
  const value = Number(score ?? 0);
  if (!Number.isFinite(value)) return 0;
  return value > 10 ? Math.max(0, Math.min(10, value / 10)) : Math.max(0, Math.min(10, value));
}

function tierForScore(score: number): EvaluationTier {
  if (score >= 9) return "excellent";
  if (score >= 7) return "good";
  if (score >= 5) return "average";
  return "needs_work";
}

function taskId(taskPayload: AnyTaskPayload | null): string {
  return (
    textValue(taskPayload?.activity_id) ||
    textValue(taskPayload?.attempt_id) ||
    textValue(taskPayload?.archetype_id) ||
    "runtime-task"
  );
}

function activityLabel(archetypeId: string | undefined, sequence: number): string {
  const raw = String(archetypeId || "").toUpperCase();
  if (raw.includes("LISTEN")) return "Listen";
  if (raw.includes("SPEAK")) return "Speak";
  if (raw.includes("WRITE")) return "Write";
  if (raw.includes("READ")) return "Read";
  return `Activity ${sequence}`;
}

function nullableText(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function textValue(value: unknown): string {
  return typeof value === "string" ? value : "";
}
