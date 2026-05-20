"use client";

/**
 * Daily-session shell.
 *
 * Drives the activity-by-activity flow against /api/sessions/*:
 *   1. Fetch the next pending activity.
 *   2. Render the matching widget (via the sessions widget registry).
 *   3. On submit → run `useSubmitActivity` → show feedback inline.
 *   4. On "Continue" → re-fetch next-activity.
 *   5. When backend returns 409 (no pending), render the "Complete session"
 *      action which calls /complete and navigates to the scorecard.
 */

import { createElement, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { ActivityFeedbackCard } from "@/components/sessions/ActivityFeedbackCard";
import { SessionActivityNav } from "@/components/sessions/SessionActivityNav";
import { getSessionWidget } from "@/components/sessions/widgets/registry";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import {
  useCompleteSession,
  useNextActivity,
  useSubmitActivity,
} from "@/hooks/useSessionsFlow";
import { useSessionStore } from "@/store/sessionStore";


export default function SessionShellPage() {
  const params = useParams<{ sessionId: string }>();
  const sessionId = params.sessionId;
  const router = useRouter();
  useRequireAuth();

  const session = useSessionStore((s) => s.session);
  const lastFeedback = useSessionStore((s) => s.lastFeedback);

  const nextActivityQuery = useNextActivity(sessionId, {
    // While inline feedback is visible we pause the next-activity fetch
    // so the user can read before the UI advances.
    enabled: lastFeedback === null,
  });

  const submit = useSubmitActivity(sessionId);
  const complete = useCompleteSession(sessionId);

  const [submitError, setSubmitError] = useState<string | null>(null);

  const isNextLoading = nextActivityQuery.isLoading;
  const nextErr = nextActivityQuery.error as { response?: { status?: number } } | null;
  const sessionDone = nextErr?.response?.status === 409;

  function handleSubmit(response: Record<string, unknown>) {
    if (!nextActivityQuery.data) return;
    setSubmitError(null);
    submit.mutate(
      {
        sequence: nextActivityQuery.data.sequence,
        archetype_id: nextActivityQuery.data.archetype_id,
        payload: { user_response: response },
      },
      {
        onError: (err) => setSubmitError(err.message ?? "Submit failed"),
      },
    );
  }

  function handleContinue() {
    // Clearing the inline feedback re-enables `useNextActivity` (its
    // `enabled` depends on `lastFeedback === null`), which fetches the
    // next pending attempt — or yields 409 if there are none, flipping
    // the page into "complete session" mode.
    useSessionStore.setState({ lastFeedback: null });
  }

  function handleComplete() {
    complete.mutate(undefined, {
      onSuccess: () => router.push(`/sessions/${sessionId}/scorecard`),
    });
  }

  return (
    <main
      style={{
        maxWidth: 720,
        margin: "32px auto",
        padding: "0 24px",
        display: "flex",
        flexDirection: "column",
        gap: 24,
        fontFamily: "'Plus Jakarta Sans', sans-serif",
      }}
    >
      {session && (
        <header>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <h1 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>
              Today&rsquo;s session
            </h1>
            {session.is_first_attempt ? null : (
              <span
                style={{
                  fontSize: 12,
                  background: "oklch(94% 0.04 80)",
                  color: "oklch(40% 0.1 80)",
                  padding: "2px 8px",
                  borderRadius: 999,
                }}
                title="Replays don't add points to your dashboard"
              >
                Practice run
              </span>
            )}
          </div>
          <p style={{ margin: "4px 0 0", fontSize: 14, color: "oklch(40% 0.07 240)" }}>
            Day {session.day_id} · {session.course_length}
          </p>
          <div style={{ marginTop: 12 }}>
            <SessionActivityNav
              attempts={session.attempts}
              currentSequence={nextActivityQuery.data?.sequence ?? null}
            />
          </div>
        </header>
      )}

      {isNextLoading && !sessionDone && <p>Loading next activity&hellip;</p>}

      {sessionDone && !complete.data && (
        <section
          style={{
            background: "white",
            border: "1px solid oklch(88% 0.03 245)",
            borderRadius: 12,
            padding: 20,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
            All activities done
          </h2>
          <p style={{ margin: 0, fontSize: 14 }}>
            Calculate today&rsquo;s score and head to the scorecard.
          </p>
          <button
            type="button"
            onClick={handleComplete}
            disabled={complete.isPending}
            style={primaryButton}
          >
            {complete.isPending ? "Finalising&hellip;" : "Complete session"}
          </button>
          {complete.error && (
            <p style={errorStyle}>{(complete.error as Error).message}</p>
          )}
        </section>
      )}

      {nextActivityQuery.data && !lastFeedback && (
        <WidgetSlot
          taskContent={nextActivityQuery.data.task_content}
          uiWidget={nextActivityQuery.data.ui_widget}
          disabled={submit.isPending}
          onSubmit={handleSubmit}
        />
      )}

      {submitError && <p style={errorStyle}>{submitError}</p>}

      {lastFeedback && (
        <ActivityFeedbackCard
          feedback={lastFeedback.feedback}
          onContinue={handleContinue}
        />
      )}
    </main>
  );
}


function WidgetSlot({
  taskContent,
  uiWidget,
  disabled,
  onSubmit,
}: {
  taskContent: Record<string, unknown>;
  uiWidget: string;
  disabled: boolean;
  onSubmit: (response: Record<string, unknown>) => void;
}) {
  // The registry always returns the same module-level component reference
  // for a given `uiWidget`. We use `createElement` rather than JSX so the
  // react-hooks/static-components lint rule doesn't mistake the lookup
  // for an in-render component declaration.
  return (
    <section
      style={{
        background: "white",
        borderRadius: 12,
        padding: 20,
        border: "1px solid oklch(88% 0.03 245)",
      }}
    >
      {createElement(getSessionWidget(uiWidget), {
        taskContent,
        disabled,
        onSubmit,
      })}
    </section>
  );
}

const primaryButton: React.CSSProperties = {
  alignSelf: "flex-start",
  background: "oklch(52% 0.18 240)",
  color: "white",
  fontWeight: 600,
  padding: "10px 18px",
  borderRadius: 8,
  border: "none",
  cursor: "pointer",
};

const errorStyle: React.CSSProperties = {
  background: "oklch(96% 0.04 25)",
  color: "oklch(35% 0.18 25)",
  padding: 12,
  borderRadius: 8,
  fontSize: 14,
};
