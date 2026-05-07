"use client";

import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";
import { useForm } from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AxiosError } from "axios";
import { Check, Lock, Play, RotateCw } from "lucide-react";

import type { EnrollmentRead } from "@/lib/courses-api";
import { getApiErrorMessage } from "@/lib/errors";
import { tasksApi, isGeneratedTaskType } from "@/lib/tasks-api";
import type {
  GeneratedTaskContent,
  ResponseGraded,
  SeededTaskContent,
  UserTask,
} from "@/lib/tasks-api";
import { useNextTask } from "@/hooks/useNextTask";
import {
  defaultValuesFor,
  GeneratedTaskRenderer,
  TaskRenderer,
} from "@/components/task/TaskRenderer";

type FormValues = Record<string, string>;

interface DailyTaskPanelProps {
  enrollment: EnrollmentRead;
}

const panelStyle: CSSProperties = {
  background:
    "linear-gradient(135deg, oklch(93% 0.04 240) 0%, oklch(95% 0.02 245) 100%)",
  borderRadius: 18,
  border: "1px solid rgba(80,120,200,0.12)",
  padding: "28px 26px 24px",
  boxShadow:
    "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
  animation: "fadeSlideUp 0.4s ease 0.15s both",
};

const actionButtonStyle: CSSProperties = {
  width: "100%",
  padding: "13px 0",
  borderRadius: 12,
  border: "none",
  background: "oklch(52% 0.18 240)",
  color: "white",
  fontSize: 15,
  fontWeight: 700,
  cursor: "pointer",
};

export function DailyTaskPanel({ enrollment }: DailyTaskPanelProps) {
  const queryClient = useQueryClient();
  const taskQuery = useNextTask(true);
  const bundle = taskQuery.data ?? [];
  const [resultsById, setResultsById] = useState<Record<number, ResponseGraded>>({});
  const [review, setReview] = useState<{
    result: ResponseGraded;
    task: UserTask;
    index: number;
  } | null>(null);
  const [localDayComplete, setLocalDayComplete] = useState(false);

  const isTaskComplete = useCallback(
    (task: UserTask) => task.status === "completed" || Boolean(resultsById[task.id]),
    [resultsById],
  );

  const activeIndex = bundle.findIndex((task) => !isTaskComplete(task));
  const allComplete = bundle.length > 0 && activeIndex === -1;
  const currentStep = activeIndex === -1 ? 0 : activeIndex;
  const currentTask = activeIndex === -1 ? null : bundle[currentStep];

  const taskType = currentTask?.task.task_type ?? "";
  const isGenerated = isGeneratedTaskType(taskType);

  const activity = useMemo(() => {
    if (!currentTask || isGenerated) return null;
    const content = currentTask.task.content as SeededTaskContent;
    return content.activities?.[0] ?? null;
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

  const completeDayMutation = useMutation({
    mutationFn: tasksApi.completeDay,
    onSuccess: async () => {
      setLocalDayComplete(true);
      queryClient.setQueryData(["task", "next"], []);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["me"] }),
        queryClient.invalidateQueries({ queryKey: ["task", "next"] }),
      ]);
    },
  });

  const submitMutation = useMutation({
    mutationFn: (payload: {
      user_task_id: number;
      content: Record<string, unknown>;
      raw_text?: string;
      task: UserTask;
      index: number;
    }) =>
      tasksApi.submitResponse({
        user_task_id: payload.user_task_id,
        content: payload.content,
        raw_text: payload.raw_text,
      }),
    onSuccess: (graded, variables) => {
      setResultsById((prev) => ({ ...prev, [variables.user_task_id]: graded }));
      setReview({
        result: graded,
        task: variables.task,
        index: variables.index,
      });
      queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const onSeededSubmit = (values: FormValues) => {
    if (!currentTask) return;
    submitMutation.mutate({
      user_task_id: currentTask.id,
      content: values,
      task: currentTask,
      index: currentStep,
    });
  };

  const onGeneratedSubmit = (answers: Record<string, unknown>) => {
    if (!currentTask) return;
    submitMutation.mutate({
      user_task_id: currentTask.id,
      content: answers,
      raw_text:
        typeof answers["transcript"] === "string"
          ? answers["transcript"]
          : undefined,
      task: currentTask,
      index: currentStep,
    });
  };

  const continueAfterReview = () => {
    const wasFinalTask = review ? review.index >= bundle.length - 1 : false;
    setReview(null);
    if (wasFinalTask) {
      completeDayMutation.mutate();
    }
  };

  if (taskQuery.isLoading) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <LoadingBlock message="Loading today's tasks..." />
      </section>
    );
  }

  if (taskQuery.isError) {
    const status = (taskQuery.error as AxiosError)?.response?.status;
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <StateBlock
          tone="danger"
          title="Today's tasks could not load"
          body={getApiErrorMessage(taskQuery.error)}
          actionLabel={status === 503 ? "Try again" : "Retry"}
          onAction={() => taskQuery.refetch()}
        />
      </section>
    );
  }

  if (localDayComplete || bundle.length === 0) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <CompletedTodayBlock />
      </section>
    );
  }

  if (review) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <TaskQueue
          bundle={bundle}
          activeIndex={review.index}
          isTaskComplete={(task) =>
            task.id === review.task.id || isTaskComplete(task)
          }
        />
        <TaskResultBlock
          result={review.result}
          task={review.task}
          index={review.index}
          total={bundle.length}
          isLastTask={review.index >= bundle.length - 1}
          isCompleting={completeDayMutation.isPending}
          onContinue={continueAfterReview}
        />
      </section>
    );
  }

  if (allComplete) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <TaskQueue
          bundle={bundle}
          activeIndex={bundle.length - 1}
          isTaskComplete={isTaskComplete}
        />
        <StateBlock
          tone="success"
          title="All tasks are done"
          body="Finish today's set to unlock your next course day tomorrow."
          actionLabel={
            completeDayMutation.isPending ? "Completing..." : "Complete today"
          }
          disabled={completeDayMutation.isPending}
          onAction={() => completeDayMutation.mutate()}
        />
      </section>
    );
  }

  if (!currentTask) {
    return (
      <section style={panelStyle}>
        <PanelHeading enrollment={enrollment} />
        <StateBlock
          title="No active task"
          body="Today's set is not ready yet."
          actionLabel="Refresh"
          onAction={() => taskQuery.refetch()}
        />
      </section>
    );
  }

  const content = currentTask.task.content;
  const isSeeded = !isGenerated;

  return (
    <section style={panelStyle}>
      <PanelHeading enrollment={enrollment} />
      <TaskQueue
        bundle={bundle}
        activeIndex={currentStep}
        isTaskComplete={isTaskComplete}
      />

      <div
        style={{
          marginTop: 22,
          paddingTop: 22,
          borderTop: "1px solid rgba(80,120,200,0.14)",
        }}
      >
        <p
          style={{
            fontSize: 11,
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "oklch(52% 0.18 240)",
            margin: "0 0 6px",
          }}
        >
          Task {currentStep + 1} of {bundle.length} ·{" "}
          {currentTask.task.task_type.replace(/_/g, " ")}
        </p>
        <h3
          style={{
            fontSize: 21,
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            margin: "0 0 18px",
            letterSpacing: "-0.02em",
          }}
        >
          {currentTask.task.title}
        </h3>

        {isGenerated && (
          <GeneratedTaskRenderer
            key={currentTask.id}
            taskType={taskType as import("@/lib/tasks-api").GeneratedTaskType}
            content={content as GeneratedTaskContent}
            onSubmit={onGeneratedSubmit}
            isPending={submitMutation.isPending}
          />
        )}

        {isSeeded && activity && (
          <>
            <section
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 12,
                marginBottom: 20,
              }}
            >
              <p
                style={{
                  fontSize: 14,
                  color: "oklch(40% 0.07 240)",
                  lineHeight: 1.6,
                  margin: 0,
                }}
              >
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

            <form
              onSubmit={handleSubmit(onSeededSubmit)}
              style={{ display: "flex", flexDirection: "column", gap: 16 }}
            >
              <TaskRenderer
                activity={activity}
                register={register}
                setValue={setValue}
                errors={errors}
              />

              <button
                type="submit"
                disabled={submitMutation.isPending}
                style={{
                  ...actionButtonStyle,
                  opacity: submitMutation.isPending ? 0.65 : 1,
                  cursor: submitMutation.isPending ? "not-allowed" : "pointer",
                }}
              >
                {submitMutation.isPending ? "Submitting..." : "Submit task"}
              </button>
            </form>
          </>
        )}

        {submitMutation.error && (
          <p
            style={{
              marginTop: 12,
              padding: "10px 12px",
              borderRadius: 8,
              background: "oklch(95% 0.04 15)",
              fontSize: 13,
              color: "oklch(40% 0.15 15)",
            }}
          >
            {getApiErrorMessage(submitMutation.error)}
          </p>
        )}
      </div>
    </section>
  );
}

function PanelHeading({ enrollment }: { enrollment: EnrollmentRead }) {
  return (
    <div>
      <p
        style={{
          fontSize: 11,
          fontWeight: 800,
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          color: "oklch(52% 0.18 240)",
          margin: "0 0 8px",
        }}
      >
        Today&apos;s focus - {enrollment.course.title}
      </p>
      <h2
        style={{
          fontSize: 22,
          fontWeight: 800,
          color: "oklch(15% 0.09 245)",
          margin: "0 0 12px",
          letterSpacing: "-0.02em",
        }}
      >
        Today&apos;s task list
      </h2>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          flexWrap: "wrap",
          marginBottom: 18,
        }}
      >
        <MetaBadge>Day {enrollment.current_day_in_week}</MetaBadge>
        <MetaBadge>{enrollment.tasks_per_day} per day</MetaBadge>
        <MetaBadge>{enrollment.course.target_level}</MetaBadge>
      </div>
    </div>
  );
}

function MetaBadge({ children }: { children: React.ReactNode }) {
  return (
    <span
      style={{
        fontSize: 12,
        fontWeight: 700,
        color: "oklch(45% 0.07 240)",
        background: "rgba(255,255,255,0.72)",
        border: "1px solid rgba(80,120,200,0.1)",
        padding: "4px 10px",
        borderRadius: 6,
      }}
    >
      {children}
    </span>
  );
}

function TaskQueue({
  bundle,
  activeIndex,
  isTaskComplete,
}: {
  bundle: UserTask[];
  activeIndex: number;
  isTaskComplete: (task: UserTask) => boolean;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {bundle.map((task, index) => {
        const complete = isTaskComplete(task);
        const active = !complete && index === activeIndex;
        const locked = !complete && index > activeIndex;
        return (
          <div
            key={task.id}
            style={{
              display: "grid",
              gridTemplateColumns: "32px 1fr auto",
              gap: 12,
              alignItems: "center",
              padding: "13px 14px",
              borderRadius: 12,
              background: complete
                ? "oklch(96% 0.025 155)"
                : active
                  ? "white"
                  : "rgba(255,255,255,0.48)",
              border: complete
                ? "1px solid oklch(86% 0.08 155)"
                : active
                  ? "1px solid oklch(78% 0.09 240)"
                  : "1px dashed rgba(80,120,200,0.22)",
              opacity: locked ? 0.68 : 1,
            }}
          >
            <span
              style={{
                width: 32,
                height: 32,
                borderRadius: "50%",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                background: complete
                  ? "oklch(55% 0.18 155)"
                  : active
                    ? "oklch(52% 0.18 240)"
                    : "oklch(87% 0.025 240)",
                color: complete || active ? "white" : "oklch(45% 0.06 240)",
              }}
            >
              {complete ? (
                <Check size={17} />
              ) : active ? (
                <Play size={15} fill="currentColor" />
              ) : (
                <Lock size={15} />
              )}
            </span>
            <div style={{ minWidth: 0 }}>
              <p
                style={{
                  margin: 0,
                  color: "oklch(19% 0.08 245)",
                  fontSize: 14,
                  fontWeight: 800,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {task.task.title}
              </p>
              <p
                style={{
                  margin: "3px 0 0",
                  color: "oklch(48% 0.06 240)",
                  fontSize: 12,
                  textTransform: "capitalize",
                }}
              >
                {task.task.task_type.replace(/_/g, " ")}
              </p>
            </div>
            <span
              style={{
                fontSize: 12,
                fontWeight: 800,
                color: complete
                  ? "oklch(43% 0.16 155)"
                  : active
                    ? "oklch(42% 0.15 240)"
                    : "oklch(48% 0.05 240)",
              }}
            >
              {complete ? "Done" : active ? "Open" : "Locked"}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function TaskResultBlock({
  result,
  task,
  index,
  total,
  isLastTask,
  isCompleting,
  onContinue,
}: {
  result: ResponseGraded;
  task: UserTask;
  index: number;
  total: number;
  isLastTask: boolean;
  isCompleting: boolean;
  onContinue: () => void;
}) {
  const percentage = Number(result.evaluation.percentage ?? 0);
  const feedback = result.feedback.body;
  const scoreColor =
    percentage >= 70
      ? "oklch(45% 0.18 155)"
      : percentage >= 50
        ? "oklch(50% 0.18 70)"
        : "oklch(50% 0.18 15)";

  return (
    <div
      style={{
        marginTop: 22,
        paddingTop: 22,
        borderTop: "1px solid rgba(80,120,200,0.14)",
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <div>
        <p
          style={{
            fontSize: 11,
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "oklch(52% 0.18 240)",
            margin: "0 0 6px",
          }}
        >
          Result {index + 1} of {total} · {task.task.task_type.replace(/_/g, " ")}
        </p>
        <h3
          style={{
            fontSize: 21,
            fontWeight: 800,
            color: "oklch(15% 0.09 245)",
            margin: 0,
            letterSpacing: "-0.02em",
          }}
        >
          {task.task.title}
        </h3>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(112px, 0.38fr) 1fr",
          gap: 12,
        }}
      >
        <div
          style={{
            borderRadius: 12,
            background: "oklch(96% 0.015 240)",
            border: "1px solid rgba(80,120,200,0.12)",
            padding: 16,
          }}
        >
          <p
            style={{
              margin: "0 0 8px",
              color: "oklch(48% 0.08 240)",
              fontSize: 11,
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}
          >
            Score
          </p>
          <p
            style={{
              margin: 0,
              color: scoreColor,
              fontSize: 34,
              lineHeight: 1,
              fontWeight: 800,
            }}
          >
            {Math.round(percentage)}%
          </p>
        </div>
        <div
          style={{
            borderRadius: 12,
            background: "rgba(255,255,255,0.82)",
            border: "1px solid rgba(80,120,200,0.12)",
            padding: 16,
          }}
        >
          <p
            style={{
              margin: 0,
              color: "oklch(24% 0.07 240)",
              fontSize: 14,
              lineHeight: 1.6,
              fontWeight: 600,
            }}
          >
            {feedback.overall_message}
          </p>
          <p
            style={{
              margin: "10px 0 0",
              color: "oklch(40% 0.07 240)",
              fontSize: 13,
              lineHeight: 1.55,
            }}
          >
            <strong>Practice next:</strong> {feedback.practice_suggestion}
          </p>
        </div>
      </div>

      {feedback.errors.length > 0 && (
        <div
          style={{
            borderRadius: 12,
            background: "oklch(98% 0.012 70)",
            border: "1px solid oklch(86% 0.08 70)",
            padding: 15,
          }}
        >
          <p
            style={{
              margin: "0 0 10px",
              color: "oklch(30% 0.09 70)",
              fontSize: 14,
              fontWeight: 800,
            }}
          >
            What to fix
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {feedback.errors.slice(0, 3).map((error) => (
              <p
                key={error.question_id}
                style={{
                  margin: 0,
                  color: "oklch(32% 0.07 70)",
                  fontSize: 13,
                  lineHeight: 1.5,
                }}
              >
                <strong>{error.question_id}:</strong> {error.why_wrong}
              </p>
            ))}
          </div>
        </div>
      )}

      <button
        type="button"
        disabled={isCompleting}
        onClick={onContinue}
        style={{
          ...actionButtonStyle,
          opacity: isCompleting ? 0.65 : 1,
          cursor: isCompleting ? "not-allowed" : "pointer",
        }}
      >
        {isCompleting
          ? "Completing..."
          : isLastTask
            ? "Complete today"
            : "Unlock next task"}
      </button>
    </div>
  );
}

function CompletedTodayBlock() {
  return (
    <div
      style={{
        padding: "28px 18px 10px",
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 14,
      }}
    >
      <span
        style={{
          width: 58,
          height: 58,
          borderRadius: "50%",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          background: "oklch(55% 0.18 155)",
          color: "white",
        }}
      >
        <Check size={30} />
      </span>
      <div>
        <h3
          style={{
            margin: "0 0 6px",
            color: "oklch(15% 0.09 245)",
            fontSize: 22,
            fontWeight: 800,
          }}
        >
          Today&apos;s tasks are complete
        </h3>
        <p
          style={{
            margin: 0,
            color: "oklch(45% 0.07 240)",
            fontSize: 14,
            lineHeight: 1.6,
          }}
        >
          Your next set will unlock on the next calendar day.
        </p>
      </div>
    </div>
  );
}

function LoadingBlock({ message }: { message: string }) {
  return (
    <div style={{ padding: "26px 0", textAlign: "center" }}>
      <span
        style={{
          display: "inline-flex",
          width: 36,
          height: 36,
          borderRadius: "50%",
          border: "3px solid oklch(88% 0.03 240)",
          borderTopColor: "oklch(52% 0.18 240)",
          animation: "spin 0.8s linear infinite",
          marginBottom: 12,
        }}
      />
      <p style={{ margin: 0, color: "oklch(45% 0.07 240)", fontSize: 14 }}>
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

function StateBlock({
  title,
  body,
  actionLabel,
  onAction,
  disabled,
  tone = "neutral",
}: {
  title: string;
  body: string;
  actionLabel: string;
  onAction: () => void;
  disabled?: boolean;
  tone?: "neutral" | "success" | "danger";
}) {
  const iconColor =
    tone === "success"
      ? "oklch(55% 0.18 155)"
      : tone === "danger"
        ? "oklch(54% 0.2 28)"
        : "oklch(52% 0.18 240)";
  return (
    <div
      style={{
        padding: "24px 0 4px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        gap: 12,
      }}
    >
      <span
        style={{
          width: 48,
          height: 48,
          borderRadius: "50%",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          background: "rgba(255,255,255,0.72)",
          color: iconColor,
        }}
      >
        {tone === "success" ? <Check size={26} /> : <RotateCw size={23} />}
      </span>
      <div>
        <h3
          style={{
            margin: "0 0 6px",
            color: "oklch(15% 0.09 245)",
            fontSize: 20,
            fontWeight: 800,
          }}
        >
          {title}
        </h3>
        <p
          style={{
            margin: 0,
            color: "oklch(45% 0.07 240)",
            fontSize: 14,
            lineHeight: 1.6,
          }}
        >
          {body}
        </p>
      </div>
      <button
        type="button"
        disabled={disabled}
        onClick={onAction}
        style={{
          ...actionButtonStyle,
          maxWidth: 240,
          marginTop: 4,
          opacity: disabled ? 0.65 : 1,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        {actionLabel}
      </button>
    </div>
  );
}
