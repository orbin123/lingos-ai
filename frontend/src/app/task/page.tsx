"use client";

import { useEffect, useMemo, useState, useCallback } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";

import { useRequireAuth } from "@/hooks/useRequireAuth";
import { authApi } from "@/lib/auth-api";
import { useNextTask } from "@/hooks/useNextTask";
import { getApiErrorMessage } from "@/lib/errors";
import { tasksApi, isGeneratedTaskType } from "@/lib/tasks-api";
import type {
  UserTask,
  ResponseGraded,
  GeneratedTaskContent,
  SeededTaskContent,
  EvaluationQuestionResult,
} from "@/lib/tasks-api";
import {
  TaskRenderer,
  GeneratedTaskRenderer,
  defaultValuesFor,
} from "@/components/task/TaskRenderer";

// Form shape: one string answer per question key (Q1, Q2, ...)
type FormValues = Record<string, string>;

// ════════════════════════════════════════════════════════════════════
// MAIN PAGE
// ════════════════════════════════════════════════════════════════════

export default function TaskPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isReady, isSuperUser } = useRequireAuth();

  // ─── Superuser jump override ───────────────────────────────
  // When the dev panel calls superuser-jump, it stashes the returned
  // bundle in sessionStorage so we can render it immediately without
  // an extra /tasks/next call.
  const [overrideBundle, setOverrideBundle] = useState<UserTask[] | null>(null);
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("superuser_jump_bundle");
      if (raw) {
        sessionStorage.removeItem("superuser_jump_bundle");
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setOverrideBundle(JSON.parse(raw) as UserTask[]);
      }
    } catch { /* ignore parse errors */ }
  }, []);

  // Force diagnosis-first: if not done, send them there
  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });
  const me = meQuery.data;
  useEffect(() => {
    if (me && !me.diagnosis_completed && !isSuperUser) router.replace("/diagnosis");
  }, [me, isSuperUser, router]);

  // ─── Data ──────────────────────────────────────────────────
  // Skip the normal fetch when we already have a jump override
  const taskQuery = useNextTask(
    !overrideBundle && isReady && !!me?.diagnosis_completed && !!me?.enrollment,
  );

  const bundle: UserTask[] = overrideBundle ?? taskQuery.data ?? [];
  const totalTasks = bundle.length;
  const isSuperUserJumpBundle = overrideBundle !== null;

  // ─── Step state ────────────────────────────────────────────
  const [currentStep, setCurrentStep] = useState(0);
  const [results, setResults] = useState<(ResponseGraded | null)[]>([]);
  const [prefetchedResults, setPrefetchedResults] = useState<Record<number, ResponseGraded>>({});
  const [reviewResult, setReviewResult] = useState<ResponseGraded | null>(null);
  const [dayComplete, setDayComplete] = useState(false);

  // Reset step when bundle changes — jump to first incomplete task,
  // or show day-complete immediately if all are already done.
  useEffect(() => {
    if (bundle.length > 0) {
      const firstPending = bundle.findIndex((t) => t.status !== "completed");
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setResults(new Array(bundle.length).fill(null));
      setReviewResult(null);
      if (firstPending === -1) {
        // All tasks already completed (returning after reload)
        setCurrentStep(0);
        setDayComplete(true);
      } else {
        setCurrentStep(firstPending);
        setDayComplete(false);
      }
    }
  }, [bundle.length]);

  // Pre-fetch results for completed tasks so DayCompleteScreen can show scores.
  useEffect(() => {
    const completedTasks = bundle.filter((t) => t.status === "completed");
    if (completedTasks.length === 0) return;
    let cancelled = false;
    Promise.all(
      completedTasks.map((t) =>
        tasksApi
          .getTaskResult(t.id)
          .then((r) => ({ id: t.id, result: r }))
          .catch(() => null),
      ),
    ).then((items) => {
      if (cancelled) return;
      const record: Record<number, ResponseGraded> = {};
      for (const item of items) {
        if (item) record[item.id] = item.result;
      }
      setPrefetchedResults(record);
    });
    return () => { cancelled = true; };
  }, [bundle]);

  const currentTask = bundle[currentStep] ?? null;
  const isLastTask = currentStep === totalTasks - 1;

  // ─── Detect task kind ────────────────────────────────────────
  const taskType = currentTask?.task.task_type ?? "";
  const isGenerated = isGeneratedTaskType(taskType);

  // ─── Seeded task form (only used for old tasks) ────────────
  const activity = useMemo(() => {
    if (!currentTask || isGenerated) return null;
    const c = currentTask.task.content as SeededTaskContent;
    return c.activities?.[0] ?? null;
  }, [currentTask, isGenerated]);

  const defaultValues: FormValues = useMemo(
    () => (activity ? defaultValuesFor(activity) : {}),
    [activity],
  );

  const {
    register,
    setValue,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ defaultValues });

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  // ─── Submit mutation ───────────────────────────────────────
  const submitMutation = useMutation({
    mutationFn: (payload: {
      user_task_id: number;
      content: Record<string, unknown>;
      raw_text?: string;
    }) => tasksApi.submitResponse(payload),
    onSuccess: (graded) => {
      setResults((prev) => {
        const next = [...prev];
        next[currentStep] = graded;
        return next;
      });
      setReviewResult(graded);
    },
  });

  // ─── Handlers ──────────────────────────────────────────────

  // Seeded task submit (through react-hook-form)
  const onSeededSubmit = (values: FormValues) => {
    if (!currentTask) return;
    submitMutation.mutate({
      user_task_id: currentTask.id,
      content: values,
    });
  };

  // Generated task submit (from the component's own onSubmit).
  // Content is Record<string,unknown> so speaking tasks can pass
  // {transcript, duration_seconds, audio_url} alongside the usual string values.
  const onGeneratedSubmit = useCallback(
    (answers: Record<string, unknown>) => {
      if (!currentTask) return;
      submitMutation.mutate({
        user_task_id: currentTask.id,
        content: answers,
        // raw_text for embedding: use transcript for speaking tasks, otherwise undefined
        raw_text: typeof answers["transcript"] === "string"
          ? answers["transcript"]
          : undefined,
      });
    },
    [currentTask, submitMutation],
  );

  const continueAfterReview = () => {
    setReviewResult(null);
    if (isLastTask) {
      setDayComplete(true);
    } else {
      setCurrentStep((s) => s + 1);
    }
  };

  // Complete day
  const completeDayMutation = useMutation({
    mutationFn: tasksApi.completeDay,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["task", "next"] });
      queryClient.invalidateQueries({ queryKey: ["me"] });
      router.push("/dashboard");
    },
  });

  const finishDayOrJump = () => {
    if (isSuperUserJumpBundle) {
      queryClient.invalidateQueries({ queryKey: ["task", "next"] });
      router.push("/dashboard");
      return;
    }
    completeDayMutation.mutate();
  };

  // ─── Render states ─────────────────────────────────────────
  if (!isReady) return null;

  if (meQuery.isLoading) {
    return (
      <PageShell>
        <LoadingState message="Loading your account…" />
      </PageShell>
    );
  }

  if (me && !me.enrollment) {
    return (
      <PageShell>
        <NoEnrollmentCard onDashboard={() => router.push("/dashboard")} onCourses={() => router.push("/courses")} />
      </PageShell>
    );
  }

  if (taskQuery.isLoading) {
    return (
      <PageShell>
        <LoadingState message="Loading today's tasks…" />
      </PageShell>
    );
  }

  if (taskQuery.isError) {
    const status = (taskQuery.error as AxiosError)?.response?.status;
    const message = getApiErrorMessage(taskQuery.error);
    return (
      <PageShell>
        <ErrorCard
          status={status}
          message={message}
          onRetry={() => taskQuery.refetch()}
          onDashboard={() => router.push("/dashboard")}
          onCourses={() => router.push("/courses")}
        />
      </PageShell>
    );
  }

  if (totalTasks === 0) {
    return (
      <PageShell>
        <div style={{ textAlign: "center", padding: "40px 0" }}>
          <p style={{ fontSize: 15, color: "oklch(45% 0.07 240)" }}>
            No tasks available for today. Check back later!
          </p>
          <button
            onClick={() => router.push("/dashboard")}
            style={{
              marginTop: 16,
              padding: "10px 24px",
              borderRadius: 10,
              border: "1px solid rgba(80,120,200,0.15)",
              background: "rgba(255,255,255,0.85)",
              color: "oklch(30% 0.08 240)",
              fontSize: 14,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Back to dashboard
          </button>
        </div>
      </PageShell>
    );
  }

  // ─── Day complete screen ───────────────────────────────────
  if (dayComplete) {
    const enrollment = me?.enrollment;
    const dayNum = enrollment
      ? (enrollment.current_week - 1) * 7 + enrollment.current_day_in_week
      : 0;

    // Merge in-session results with pre-fetched results for tasks already
    // completed before this session (e.g. user returned after reload).
    const effectiveResults = bundle.map(
      (task, i) => results[i] ?? prefetchedResults[task.id] ?? null,
    );

    return (
      <PageShell>
        <DayCompleteScreen
          dayNum={dayNum}
          results={effectiveResults}
          bundle={bundle}
          isCompleting={completeDayMutation.isPending}
          onFinish={finishDayOrJump}
        />
      </PageShell>
    );
  }

  // ─── Active task view ──────────────────────────────────────
  const content = currentTask.task.content;
  const isSeeded = !isGenerated;

  if (reviewResult) {
    return (
      <PageShell>
        <ProgressBar current={currentStep} total={totalTasks} />
        <TaskResultScreen
          result={reviewResult}
          task={currentTask}
          currentStep={currentStep}
          totalTasks={totalTasks}
          isLastTask={isLastTask}
          onContinue={continueAfterReview}
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      {/* Progress indicator */}
      <ProgressBar current={currentStep} total={totalTasks} />

      {/* Task header */}
      <div style={{ marginBottom: 20 }}>
        <p
          style={{
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "oklch(52% 0.18 240)",
            margin: "0 0 6px",
          }}
        >
          Task {currentStep + 1} of {totalTasks} · {currentTask.task.task_type.replace(/_/g, " ")}
        </p>
        <h1
          style={{
            fontSize: 22,
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          {currentTask.task.title}
        </h1>
      </div>

      {/* Generated task — self-contained, no form wrapper needed */}
      {isGenerated && (
        <GeneratedTaskRenderer
          key={currentTask.id}
          taskType={taskType as import("@/lib/tasks-api").GeneratedTaskType}
          content={content as GeneratedTaskContent}
          onSubmit={onGeneratedSubmit}
          isPending={submitMutation.isPending}
        />
      )}

      {/* Seeded task — uses react-hook-form */}
      {isSeeded && activity && (
        <>
          <section style={{ display: "flex", flexDirection: "column", gap: 12, marginBottom: 20 }}>
            <p style={{ fontSize: 14, color: "oklch(40% 0.07 240)", lineHeight: 1.6, margin: 0 }}>
              {(content as SeededTaskContent).instruction}
            </p>
            <blockquote
              style={{
                margin: 0,
                padding: "14px 18px",
                borderRadius: 10,
                background: "oklch(96% 0.015 240)",
                borderLeft: "3px solid oklch(52% 0.18 240)",
                fontSize: 14,
                fontStyle: "italic",
                color: "oklch(25% 0.07 240)",
                lineHeight: 1.7,
              }}
            >
              {(content as SeededTaskContent).source.text}
            </blockquote>
          </section>

          <form onSubmit={handleSubmit(onSeededSubmit)} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <TaskRenderer
              activity={activity}
              register={register}
              setValue={setValue}
              errors={errors}
            />

            {submitMutation.error && (
              <p
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  background: "oklch(95% 0.04 15)",
                  fontSize: 13,
                  color: "oklch(40% 0.15 15)",
                }}
              >
                {getApiErrorMessage(submitMutation.error)}
              </p>
            )}

            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                style={{
                  padding: "10px 20px",
                  borderRadius: 10,
                  border: "1px solid rgba(80,120,200,0.15)",
                  background: "rgba(255,255,255,0.85)",
                  color: "oklch(30% 0.08 240)",
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                Back to dashboard
              </button>
              <button
                type="submit"
                disabled={submitMutation.isPending}
                style={{
                  padding: "10px 24px",
                  borderRadius: 10,
                  border: "none",
                  background: "oklch(52% 0.18 240)",
                  color: "white",
                  fontSize: 14,
                  fontWeight: 700,
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                  opacity: submitMutation.isPending ? 0.6 : 1,
                }}
              >
                {submitMutation.isPending
                  ? "Submitting…"
                  : isLastTask
                    ? "Submit & Finish Day"
                    : "Submit & Next →"}
              </button>
            </div>
          </form>
        </>
      )}

      {/* Error from generated task submit */}
      {isGenerated && submitMutation.error && (
        <p
          style={{
            marginTop: 12,
            padding: "8px 12px",
            borderRadius: 8,
            background: "oklch(95% 0.04 15)",
            fontSize: 13,
            color: "oklch(40% 0.15 15)",
          }}
        >
          {getApiErrorMessage(submitMutation.error)}
        </p>
      )}
    </PageShell>
  );
}

// ════════════════════════════════════════════════════════════════════
// SUB-COMPONENTS
// ════════════════════════════════════════════════════════════════════

function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background:
          "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />

      {/* Dotted pattern overlay */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.18) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          maxWidth: 680,
          margin: "0 auto",
          padding: "40px 20px 80px",
        }}
      >
        {/* Glass card container */}
        <div
          style={{
            background: "rgba(255,255,255,0.85)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            borderRadius: 18,
            border: "1px solid rgba(255,255,255,0.9)",
            padding: "28px 28px 24px",
            boxShadow:
              "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
            animation: "fadeSlideUp 0.4s ease both",
          }}
        >
          {children}
        </div>
      </div>

      {/* Animations */}
      <style>{`
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(16px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse-soft {
          0%, 100% { opacity: 1; }
          50%      { opacity: 0.7; }
        }
      `}</style>
    </div>
  );
}

// ─── Progress bar ────────────────────────────────────────────

function ProgressBar({ current, total }: { current: number; total: number }) {
  return (
    <div style={{ marginBottom: 24 }}>
      {/* Dots */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          marginBottom: 10,
        }}
      >
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            style={{
              width: i === current ? 32 : 10,
              height: 10,
              borderRadius: 5,
              background:
                i < current
                  ? "oklch(55% 0.18 155)" // completed — green
                  : i === current
                    ? "oklch(52% 0.18 240)" // active — blue
                    : "oklch(88% 0.03 240)", // upcoming — light
              transition: "all 0.3s ease",
            }}
          />
        ))}
      </div>

      {/* Bar */}
      <div
        style={{
          height: 4,
          borderRadius: 2,
          background: "oklch(92% 0.02 240)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${((current) / total) * 100}%`,
            borderRadius: 2,
            background:
              "linear-gradient(90deg, oklch(55% 0.18 155), oklch(52% 0.18 240))",
            transition: "width 0.4s ease",
          }}
        />
      </div>
    </div>
  );
}

// ─── Result / feedback screen ─────────────────────────────────

function TaskResultScreen({
  result,
  task,
  currentStep,
  totalTasks,
  isLastTask,
  onContinue,
}: {
  result: ResponseGraded;
  task: UserTask;
  currentStep: number;
  totalTasks: number;
  isLastTask: boolean;
  onContinue: () => void;
}) {
  const { evaluation, feedback, skill_scores } = result;
  const report = evaluation.report;
  const fb = feedback.body;
  const questions = report.questions ?? {};
  const questionEntries = Object.entries(questions);
  const percentage = Number(evaluation.percentage ?? fb.score ?? 0);
  const scoreColor =
    percentage >= 70
      ? "oklch(45% 0.18 155)"
      : percentage >= 50
        ? "oklch(50% 0.18 70)"
        : "oklch(50% 0.18 15)";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div>
        <p
          style={{
            fontSize: 11,
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "oklch(52% 0.18 240)",
            margin: "0 0 6px",
          }}
        >
          Result {currentStep + 1} of {totalTasks} · {task.task.task_type.replace(/_/g, " ")}
        </p>
        <h1
          style={{
            fontSize: 22,
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          {task.task.title}
        </h1>
      </div>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(120px, 0.45fr) 1fr",
          gap: 14,
        }}
      >
        <div
          style={{
            borderRadius: 12,
            background: "oklch(96% 0.015 240)",
            border: "1px solid rgba(80,120,200,0.12)",
            padding: 18,
          }}
        >
          <p
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "oklch(48% 0.08 240)",
              margin: "0 0 8px",
            }}
          >
            Score
          </p>
          <p
            style={{
              fontSize: 34,
              lineHeight: 1,
              fontWeight: 800,
              color: scoreColor,
              margin: 0,
            }}
          >
            {Math.round(percentage)}%
          </p>
          <p
            style={{
              fontSize: 12,
              color: "oklch(45% 0.06 240)",
              margin: "8px 0 0",
            }}
          >
            {evaluation.overall_score.toFixed(1)} / 10
          </p>
        </div>

        <div
          style={{
            borderRadius: 12,
            background: "rgba(255,255,255,0.82)",
            border: "1px solid rgba(80,120,200,0.12)",
            padding: 18,
          }}
        >
          <p
            style={{
              fontSize: 11,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "oklch(48% 0.08 240)",
              margin: "0 0 8px",
            }}
          >
            Feedback
          </p>
          <p
            style={{
              fontSize: 14,
              color: "oklch(24% 0.07 240)",
              lineHeight: 1.6,
              margin: 0,
            }}
          >
            {fb.overall_message}
          </p>
          <p
            style={{
              fontSize: 13,
              color: "oklch(40% 0.07 240)",
              lineHeight: 1.6,
              margin: "10px 0 0",
            }}
          >
            <strong>Practice next:</strong> {fb.practice_suggestion}
          </p>
        </div>
      </section>

      <section
        style={{
          borderRadius: 12,
          background: "oklch(98% 0.008 240)",
          border: "1px solid rgba(80,120,200,0.1)",
          padding: 16,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 12,
            alignItems: "center",
            marginBottom: 12,
          }}
        >
          <h2
            style={{
              fontSize: 15,
              fontWeight: 800,
              color: "oklch(18% 0.08 245)",
              margin: 0,
            }}
          >
            Evaluation
          </h2>
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              color: "oklch(45% 0.08 240)",
            }}
          >
            {report.correct_count ?? 0} / {report.total ?? questionEntries.length} full-score ·{" "}
            {Number(report.percentage ?? percentage).toFixed(1)}%
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {questionEntries.map(([id, question]) => (
            <EvaluationRow key={id} id={id} question={question} />
          ))}
        </div>
      </section>

      {fb.errors.length > 0 && (
        <section
          style={{
            borderRadius: 12,
            background: "oklch(98% 0.012 70)",
            border: "1px solid oklch(86% 0.08 70)",
            padding: 16,
          }}
        >
          <h2
            style={{
              fontSize: 15,
              fontWeight: 800,
              color: "oklch(30% 0.09 70)",
              margin: "0 0 12px",
            }}
          >
            What to fix
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {fb.errors.map((error) => (
              <div key={error.question_id}>
                <p
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: "oklch(25% 0.08 70)",
                    margin: "0 0 4px",
                  }}
                >
                  {error.question_id}: {error.user_answer || "(blank)"} → {error.correct_answer}
                </p>
                {error.correction && (
                  <p
                    style={{
                      fontSize: 13,
                      color: "oklch(32% 0.07 70)",
                      lineHeight: 1.55,
                      margin: "0 0 4px",
                    }}
                  >
                    <strong>Correction:</strong> {error.correction}
                  </p>
                )}
                <p
                  style={{
                    fontSize: 13,
                    color: "oklch(32% 0.07 70)",
                    lineHeight: 1.55,
                    margin: "0 0 4px",
                  }}
                >
                  {error.why_wrong}
                </p>
                <p
                  style={{
                    fontSize: 12,
                    color: "oklch(40% 0.07 70)",
                    lineHeight: 1.5,
                    margin: 0,
                  }}
                >
                  <strong>Rule:</strong> {error.rule} <strong>Tip:</strong> {error.memory_tip}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {skill_scores.length > 0 && (
        <section
          style={{
            borderRadius: 12,
            background: "rgba(255,255,255,0.82)",
            border: "1px solid rgba(80,120,200,0.12)",
            padding: 16,
          }}
        >
          <h2
            style={{
              fontSize: 15,
              fontWeight: 800,
              color: "oklch(18% 0.08 245)",
              margin: "0 0 12px",
            }}
          >
            Updated skill score
          </h2>
          {skill_scores.map((score) => (
            <div key={score.skill_id}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 13,
                  fontWeight: 700,
                  color: "oklch(25% 0.07 240)",
                  marginBottom: 6,
                }}
              >
                <span>{score.skill_name.replace(/_/g, " ")}</span>
                <span>{score.score.toFixed(1)} / 10</span>
              </div>
              <div
                style={{
                  height: 8,
                  borderRadius: 4,
                  background: "oklch(90% 0.02 240)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${Math.min(Math.max(score.score * 10, 0), 100)}%`,
                    borderRadius: 4,
                    background: "linear-gradient(90deg, oklch(55% 0.18 155), oklch(52% 0.18 240))",
                  }}
                />
              </div>
            </div>
          ))}
        </section>
      )}

      <button
        type="button"
        onClick={onContinue}
        style={{
          width: "100%",
          padding: "14px 0",
          borderRadius: 12,
          border: "none",
          background: "oklch(52% 0.18 240)",
          color: "white",
          fontSize: 15,
          fontWeight: 700,
          cursor: "pointer",
        }}
      >
        {isLastTask ? "Finish day →" : "Continue to next task →"}
      </button>
    </div>
  );
}

function EvaluationRow({
  id,
  question,
}: {
  id: string;
  question: EvaluationQuestionResult;
}) {
  const isCorrect = question.correct === true;
  const isMissing = question.error_type === "missing_answer";
  const score = typeof question.score === "number" ? question.score : null;
  const classification = question.error_classification ?? question.error_type;
  const displayedSentence =
    question.speaking_prompt ||
    question.incorrect_sentence ||
    question.sentence ||
    question.original_sentence;

  return (
    <div
      style={{
        borderRadius: 10,
        background: isCorrect ? "oklch(97% 0.025 155)" : "white",
        border: isCorrect
          ? "1px solid oklch(88% 0.08 155)"
          : "1px solid rgba(80,120,200,0.1)",
        padding: "12px 14px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 10,
          alignItems: "center",
          marginBottom: displayedSentence ? 8 : 0,
        }}
      >
        <span
          style={{
            fontSize: 13,
            fontWeight: 800,
            color: "oklch(22% 0.08 245)",
          }}
        >
          {id}
        </span>
        <span
          style={{
            fontSize: 12,
            fontWeight: 800,
            color: isCorrect ? "oklch(42% 0.18 155)" : "oklch(50% 0.16 20)",
          }}
        >
          {score !== null ? `${score.toFixed(1)} / 1` : isCorrect ? "Correct" : isMissing ? "Missing" : "Review"}
        </span>
      </div>

      {displayedSentence && (
        <p
          style={{
            fontSize: 13,
            color: "oklch(28% 0.07 240)",
            lineHeight: 1.55,
            margin: "0 0 8px",
          }}
        >
          {displayedSentence}
        </p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 8,
          fontSize: 12,
          color: "oklch(40% 0.07 240)",
        }}
      >
        <span>
          Your answer: <strong>{question.user_answer || "(blank)"}</strong>
        </span>
        <span>
          Correct: <strong>{question.correct_answer ?? "—"}</strong>
        </span>
      </div>

      {(classification || question.incorrect_phrase || question.direction || question.common_mistake || question.transformation_target || question.expected_pattern || question.grammar_rule || question.item_error_type || question.target_tense || question.sentence_count !== undefined) && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            marginTop: 8,
            fontSize: 12,
            color: "oklch(42% 0.07 240)",
          }}
        >
          {classification && (
            <span>
              Classification: <strong>{classification.replace(/_/g, " ")}</strong>
            </span>
          )}
          {question.direction && (
            <span>
              Direction: <strong>{question.direction.replace(/_/g, " ")}</strong>
            </span>
          )}
          {question.grammar_rule && (
            <span>
              Rule: <strong>{question.grammar_rule.replace(/_/g, " ")}</strong>
            </span>
          )}
          {question.item_error_type && (
            <span>
              Error type: <strong>{(question.item_error_type as string).replace(/_/g, " ")}</strong>
            </span>
          )}
          {question.incorrect_phrase && (
            <span>
              Phrase: <strong>{question.incorrect_phrase}</strong>
            </span>
          )}
          {question.transformation_target && (
            <span>
              Target: <strong>{question.transformation_target.replace(/_/g, " ")}</strong>
            </span>
          )}
          {question.expected_pattern && (
            <span>
              Pattern: <strong>{question.expected_pattern}</strong>
            </span>
          )}
          {question.common_mistake && (
            <span>
              Common mistake: <strong>{question.common_mistake}</strong>
            </span>
          )}
          {question.target_tense && (
            <span>
              Tense: <strong>{(question.target_tense as string).replace(/_/g, " ")}</strong>
            </span>
          )}
          {question.sentence_count !== undefined && (
            <span>
              Sentences: <strong>{question.sentence_count as number}</strong>
              {question.minimum_sentences !== undefined && ` / ${question.minimum_sentences} min`}
            </span>
          )}
          {question.duration_seconds !== undefined && (
            <span>
              Duration: <strong>{question.duration_seconds as number}s</strong>
            </span>
          )}
          {question.grading_criteria && Array.isArray(question.grading_criteria) && (
            <span style={{ width: "100%" }}>
              Criteria:{" "}
              <strong>{(question.grading_criteria as string[]).join(" · ")}</strong>
            </span>
          )}
          {question.explanation && !question.sentence && (
            <span style={{ width: "100%" }}>
              Explanation: <strong>{question.explanation as string}</strong>
            </span>
          )}
        </div>
      )}

      {question.correction && (
        <div
          style={{
            marginTop: 8,
            paddingTop: 8,
            borderTop: "1px solid rgba(80,120,200,0.1)",
            fontSize: 12,
            color: "oklch(34% 0.07 240)",
            lineHeight: 1.5,
          }}
        >
          <p style={{ margin: 0 }}>
            <strong>Correction:</strong> {question.correction}
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Day complete screen ─────────────────────────────────────

function DayCompleteScreen({
  dayNum,
  results,
  bundle,
  isCompleting,
  onFinish,
}: {
  dayNum: number;
  results: (ResponseGraded | null)[];
  bundle: UserTask[];
  isCompleting: boolean;
  onFinish: () => void;
}) {
  return (
    <div
      style={{
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 24,
      }}
    >
      {/* Celebration icon */}
      <div
        style={{
          width: 72,
          height: 72,
          borderRadius: "50%",
          background:
            "linear-gradient(135deg, oklch(55% 0.18 155), oklch(52% 0.18 240))",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          animation: "fadeSlideUp 0.5s ease both",
        }}
      >
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
          <path
            d="M9 12l2 2 4-4"
            stroke="white"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle
            cx="12"
            cy="12"
            r="9"
            stroke="white"
            strokeWidth="2"
            fill="none"
          />
        </svg>
      </div>

      <div>
        <h2
          style={{
            fontSize: 24,
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            margin: "0 0 6px",
            letterSpacing: "-0.02em",
          }}
        >
          Day {dayNum} complete!
        </h2>
        <p
          style={{
            fontSize: 15,
            color: "oklch(45% 0.07 240)",
            margin: 0,
          }}
        >
          Great work! See you tomorrow for your next session.
        </p>
      </div>

      {/* Score badges */}
      <div
        style={{
          width: "100%",
          display: "flex",
          flexDirection: "column",
          gap: 10,
        }}
      >
        {bundle.map((task, i) => {
          const result = results[i];
          const score = result?.evaluation?.percentage;
          return (
            <div
              key={task.id}
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "14px 18px",
                borderRadius: 12,
                background: "oklch(96% 0.015 240)",
                border: "1px solid rgba(80,120,200,0.1)",
                animation: `fadeSlideUp 0.4s ease ${0.1 + i * 0.1}s both`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    background:
                      score != null && score >= 70
                        ? "oklch(55% 0.18 155)"
                        : score != null && score >= 50
                          ? "oklch(60% 0.18 70)"
                          : "oklch(55% 0.15 15)",
                    color: "white",
                    fontSize: 12,
                    fontWeight: 700,
                  }}
                >
                  {i + 1}
                </span>
                <div>
                  <p
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: "oklch(20% 0.07 240)",
                      margin: 0,
                    }}
                  >
                    {task.task.title}
                  </p>
                  <p
                    style={{
                      fontSize: 12,
                      color: "oklch(50% 0.06 240)",
                      margin: 0,
                    }}
                  >
                    {task.task.task_type.replace(/_/g, " ")}
                  </p>
                </div>
              </div>
              {score != null && (
                <span
                  style={{
                    fontSize: 16,
                    fontWeight: 800,
                    color:
                      score >= 70
                        ? "oklch(45% 0.18 155)"
                        : score >= 50
                          ? "oklch(50% 0.18 70)"
                          : "oklch(50% 0.18 15)",
                  }}
                >
                  {Math.round(score)}%
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Finish button */}
      <button
        onClick={onFinish}
        disabled={isCompleting}
        style={{
          width: "100%",
          padding: "14px 0",
          borderRadius: 12,
          border: "none",
          background: "oklch(52% 0.18 240)",
          color: "white",
          fontSize: 15,
          fontWeight: 700,
          cursor: isCompleting ? "not-allowed" : "pointer",
          transition: "all 0.2s ease",
          opacity: isCompleting ? 0.6 : 1,
          marginTop: 4,
        }}
      >
        {isCompleting ? "Completing…" : "Back to dashboard →"}
      </button>
    </div>
  );
}

// ─── Loading state ───────────────────────────────────────────

function LoadingState({ message }: { message: string }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: "48px 0",
      }}
    >
      {/* Spinner */}
      <div
        style={{
          width: 36,
          height: 36,
          border: "3px solid oklch(88% 0.03 240)",
          borderTopColor: "oklch(52% 0.18 240)",
          borderRadius: "50%",
          margin: "0 auto 16px",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <p style={{ fontSize: 14, color: "oklch(45% 0.07 240)" }}>
        {message}
      </p>
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// ─── No enrollment card ──────────────────────────────────────

function NoEnrollmentCard({
  onDashboard,
  onCourses,
}: {
  onDashboard: () => void;
  onCourses: () => void;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <span
        style={{
          display: "inline-block",
          fontSize: 12,
          fontWeight: 700,
          color: "oklch(45% 0.16 70)",
          background: "oklch(92% 0.06 80)",
          padding: "3px 10px",
          borderRadius: 20,
          width: "fit-content",
        }}
      >
        Action required
      </span>
      <h2
        style={{
          fontSize: 20,
          fontWeight: 800,
          color: "oklch(15% 0.09 245)",
          margin: 0,
          letterSpacing: "-0.02em",
        }}
      >
        Choose a course first
      </h2>
      <p
        style={{
          fontSize: 14,
          color: "oklch(45% 0.07 240)",
          margin: 0,
          lineHeight: 1.5,
        }}
      >
        Your diagnosis is ready, but you need to purchase a course before we
        can unlock today&apos;s tasks.
      </p>
      <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
        <button
          onClick={onDashboard}
          style={{
            flex: 1,
            padding: "10px 0",
            borderRadius: 10,
            border: "1px solid rgba(80,120,200,0.15)",
            background: "rgba(255,255,255,0.8)",
            color: "oklch(30% 0.08 240)",
            fontSize: 14,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Back to dashboard
        </button>
        <button
          onClick={onCourses}
          style={{
            flex: 1,
            padding: "10px 0",
            borderRadius: 10,
            border: "none",
            background: "oklch(52% 0.18 240)",
            color: "white",
            fontSize: 14,
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          View courses
        </button>
      </div>
    </div>
  );
}

// ─── Error card ──────────────────────────────────────────────

function ErrorCard({
  status,
  message,
  onRetry,
  onDashboard,
  onCourses,
}: {
  status?: number;
  message: string;
  onRetry: () => void;
  onDashboard: () => void;
  onCourses: () => void;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <h2
        style={{
          fontSize: 18,
          fontWeight: 700,
          color: "oklch(40% 0.18 15)",
          margin: 0,
        }}
      >
        We could not load your tasks
      </h2>
      <p style={{ fontSize: 14, color: "oklch(45% 0.12 15)", margin: 0 }}>
        {message}
      </p>
      {status === 404 && (
        <p style={{ fontSize: 14, color: "oklch(45% 0.12 15)", margin: 0 }}>
          You need an active course enrollment before we can assign daily
          tasks.
        </p>
      )}
      <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
        {status === 404 ? (
          <>
            <button
              onClick={onDashboard}
              style={{
                flex: 1,
                padding: "10px 0",
                borderRadius: 10,
                border: "1px solid oklch(85% 0.04 15)",
                background: "rgba(255,255,255,0.8)",
                color: "oklch(40% 0.12 15)",
                fontSize: 14,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Back to dashboard
            </button>
            <button
              onClick={onCourses}
              style={{
                flex: 1,
                padding: "10px 0",
                borderRadius: 10,
                border: "none",
                background: "oklch(55% 0.18 15)",
                color: "white",
                fontSize: 14,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              View courses
            </button>
          </>
        ) : (
          <button
            onClick={onRetry}
            style={{
              padding: "10px 24px",
              borderRadius: 10,
              border: "none",
              background: "oklch(55% 0.18 15)",
              color: "white",
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
