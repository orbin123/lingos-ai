"use client";

/**
 * Start-a-new-session page (Phase 6).
 *
 * Minimal form that POSTs `/api/sessions/start` and redirects to the
 * session shell. For Phase 6 the form is hand-driven — Phase 7+ wires it
 * to the dashboard CTA + enrollment-aware defaults so users don't see this
 * page directly.
 */

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useStartSession } from "@/hooks/useSessionsFlow";
import { isSessionsFlowEnabled, type CourseLength } from "@/lib/sessions-api";


export default function StartSessionPage() {
  const router = useRouter();
  useRequireAuth();

  const [dayId, setDayId] = useState("day_24_01_01");
  const [courseLength, setCourseLength] = useState<CourseLength>("24w");
  const [tasksPerDay, setTasksPerDay] = useState<2 | 3 | 4>(2);

  const start = useStartSession();

  if (!isSessionsFlowEnabled()) {
    return (
      <main style={pageStyle}>
        <p>
          The new sessions flow is currently disabled. Set
          <code> NEXT_PUBLIC_USE_NEW_SESSION_FLOW=true</code> in your
          frontend env and the backend&rsquo;s
          <code> use_new_session_flow=true</code> to enable it.
        </p>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <h1 style={{ margin: 0, fontSize: 22, fontWeight: 800 }}>Start a session</h1>
      <p style={{ margin: "4px 0 0", fontSize: 14, color: "oklch(40% 0.07 240)" }}>
        Phase 6 manual entry point. Use a seeded <code>day_id</code> from
        the curriculum_v2 tables.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          start.mutate(
            {
              day_id: dayId.trim(),
              course_length: courseLength,
              tasks_per_day: tasksPerDay,
            },
            {
              onSuccess: (session) => {
                router.push(`/sessions/${session.session_id}`);
              },
            },
          );
        }}
        style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 24 }}
      >
        <label style={labelStyle}>
          Day ID
          <input
            value={dayId}
            onChange={(e) => setDayId(e.target.value)}
            style={inputStyle}
            placeholder="day_24_01_01"
          />
        </label>

        <label style={labelStyle}>
          Course length
          <select
            value={courseLength}
            onChange={(e) => setCourseLength(e.target.value as CourseLength)}
            style={inputStyle}
          >
            <option value="24w">24 weeks</option>
            <option value="48w">48 weeks</option>
          </select>
        </label>

        <label style={labelStyle}>
          Tasks per day
          <select
            value={tasksPerDay}
            onChange={(e) => setTasksPerDay(Number(e.target.value) as 2 | 3 | 4)}
            style={inputStyle}
          >
            <option value={2}>2</option>
            <option value={3}>3</option>
            <option value={4}>4</option>
          </select>
        </label>

        <button
          type="submit"
          disabled={start.isPending}
          style={{
            background: "oklch(52% 0.18 240)",
            color: "white",
            fontWeight: 600,
            padding: "12px 18px",
            borderRadius: 8,
            border: "none",
            cursor: start.isPending ? "default" : "pointer",
            marginTop: 8,
            alignSelf: "flex-start",
          }}
        >
          {start.isPending ? "Starting…" : "Start session"}
        </button>

        {start.error && (
          <p
            style={{
              background: "oklch(96% 0.04 25)",
              color: "oklch(35% 0.18 25)",
              padding: 12,
              borderRadius: 8,
              fontSize: 14,
            }}
          >
            {(start.error as Error).message}
          </p>
        )}
      </form>
    </main>
  );
}


const pageStyle: React.CSSProperties = {
  maxWidth: 520,
  margin: "32px auto",
  padding: "0 24px",
  fontFamily: "'Plus Jakarta Sans', sans-serif",
};

const labelStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
  fontSize: 13,
  fontWeight: 600,
  color: "oklch(40% 0.07 240)",
};

const inputStyle: React.CSSProperties = {
  fontSize: 14,
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid oklch(85% 0.04 245)",
  background: "white",
};
