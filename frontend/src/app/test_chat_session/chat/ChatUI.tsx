"use client";

import { useMemo, useState } from "react";
import { Check, ChevronLeft, Circle, X } from "lucide-react";
import {
  ChatGlobalStyles,
  ChatMain,
  ChatPageShell,
  LingosBrand,
  roundIconButton,
} from "@/components/chat/ChatChrome";
import { ChatSessionOrchestrator } from "./orchestrator";
import {
  COURSE_TRACK_OPTIONS,
  type CourseTrack,
  type SessionPreviewState,
} from "./teaching/source";

export default function TestChatSessionPage() {
  const [courseTrack, setCourseTrack] = useState<CourseTrack>("24w");
  const [week, setWeek] = useState(1);
  const [day, setDay] = useState(1);
  const [previewState, setPreviewState] = useState<SessionPreviewState>("default");

  const currentTrack = COURSE_TRACK_OPTIONS.find((option) => option.id === courseTrack) ?? COURSE_TRACK_OPTIONS[0];
  const weeks = useMemo(
    () => Array.from({ length: currentTrack.weekCount }, (_, index) => index + 1),
    [currentTrack.weekCount],
  );
  const days = useMemo(() => Array.from({ length: 7 }, (_, index) => index + 1), []);

  const changeTrack = (next: CourseTrack) => {
    const track = COURSE_TRACK_OPTIONS.find((option) => option.id === next) ?? COURSE_TRACK_OPTIONS[0];
    setCourseTrack(next);
    setWeek((current) => Math.min(current, track.weekCount));
  };

  return (
    <>
      <ChatGlobalStyles />
      <style>{`
        @media (max-width: 720px) {
          .test-chat-topbar-inner {
            flex-wrap: wrap;
          }
          .test-chat-controls {
            width: 100%;
            justify-content: space-between;
          }
        }
        @media (max-width: 560px) {
          .test-chat-select {
            min-width: 0 !important;
            flex: 1;
          }
        }
      `}</style>

      <ChatPageShell>
        <Topbar
          courseTrack={courseTrack}
          week={week}
          day={day}
          weeks={weeks}
          days={days}
          previewState={previewState}
          onCourseTrackChange={changeTrack}
          onWeekChange={setWeek}
          onDayChange={setDay}
          onPreviewStateChange={setPreviewState}
        />

        <ChatMain bottomPadding={120}>
          <ChatSessionOrchestrator
            courseTrack={courseTrack}
            week={week}
            day={day}
            previewState={previewState}
          />
          <div style={{ height: 48 }} />
        </ChatMain>

        <div
          style={{
            position: "fixed",
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 40,
            padding: "14px 20px 18px",
            background:
              "linear-gradient(to bottom, rgba(232,240,252,0) 0%, rgba(232,240,252,0.7) 50%, rgba(232,240,252,0.92) 100%)",
            backdropFilter: "blur(8px)",
          }}
        >
          <div
            style={{
              maxWidth: 720,
              margin: "0 auto",
              display: "flex",
              alignItems: "center",
              gap: 10,
              background: "rgba(255,255,255,0.96)",
              borderRadius: 22,
              padding: "8px 8px 8px 18px",
              border: "1.5px solid rgba(255,255,255,0.9)",
              boxShadow: "0 8px 28px rgba(80,110,180,0.18)",
            }}
          >
            <div
              style={{
                flex: 1,
                color: "oklch(45% 0.07 240)",
                fontSize: 14,
                lineHeight: 1.5,
                padding: "9px 0",
              }}
            >
              Completed frontend preview - backend disconnected
            </div>
            <button
              type="button"
              disabled
              aria-label="Preview is read only"
              title="Preview is read only"
              style={{
                width: 38,
                height: 38,
                borderRadius: "50%",
                background: "#0070C4",
                color: "white",
                border: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                opacity: 0.55,
              }}
            >
              <Check size={17} strokeWidth={2.8} />
            </button>
          </div>
        </div>
      </ChatPageShell>
    </>
  );
}

function Topbar({
  courseTrack,
  week,
  day,
  weeks,
  days,
  previewState,
  onCourseTrackChange,
  onWeekChange,
  onDayChange,
  onPreviewStateChange,
}: {
  courseTrack: CourseTrack;
  week: number;
  day: number;
  weeks: number[];
  days: number[];
  previewState: SessionPreviewState;
  onCourseTrackChange: (courseTrack: CourseTrack) => void;
  onWeekChange: (week: number) => void;
  onDayChange: (day: number) => void;
  onPreviewStateChange: (previewState: SessionPreviewState) => void;
}) {
  return (
    <div
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        backdropFilter: "blur(24px)",
        background: "rgba(232,240,252,0.55)",
        borderBottom: "1px solid rgba(140,170,220,0.14)",
      }}
    >
      <div
        className="test-chat-topbar-inner"
        style={{
          maxWidth: 920,
          margin: "0 auto",
          padding: "14px 20px",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <button
          type="button"
          aria-label="Back"
          title="Back"
          style={{ ...roundIconButton, cursor: "default" }}
        >
          <ChevronLeft size={18} strokeWidth={2.4} />
        </button>

        <LingosBrand subtitle="Chat session preview" />

        <div style={{ flex: 1 }} />

        <div
          className="test-chat-controls"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            flexWrap: "wrap",
          }}
        >
          <select
            className="test-chat-select"
            value={courseTrack}
            onChange={(event) => onCourseTrackChange(event.target.value as CourseTrack)}
            aria-label="Course track"
            style={selectStyle}
          >
            {COURSE_TRACK_OPTIONS.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          <select
            className="test-chat-select"
            value={week}
            onChange={(event) => onWeekChange(Number(event.target.value))}
            aria-label="Week"
            style={selectStyle}
          >
            {weeks.map((value) => (
              <option key={value} value={value}>
                Week {value}
              </option>
            ))}
          </select>
          <select
            className="test-chat-select"
            value={day}
            onChange={(event) => onDayChange(Number(event.target.value))}
            aria-label="Day"
            style={selectStyle}
          >
            {days.map((value) => (
              <option key={value} value={value}>
                Day {value}
              </option>
            ))}
          </select>

          <div
            aria-label="Answer state"
            role="group"
            style={{
              display: "inline-flex",
              gap: 6,
              padding: 4,
              borderRadius: 999,
              background: "rgba(255,255,255,0.72)",
              border: "1px solid rgba(140,170,220,0.24)",
            }}
          >
            <button
              type="button"
              aria-label="Default before submission"
              title="Default before submission"
              onClick={() => onPreviewStateChange("default")}
              style={{
                ...stateButton,
                background: previewState === "default" ? "oklch(52% 0.18 240)" : "transparent",
                color: previewState === "default" ? "white" : "oklch(35% 0.07 240)",
              }}
            >
              <Circle size={15} strokeWidth={3} />
            </button>
            <button
              type="button"
              aria-label="All answers correct"
              title="All answers correct"
              onClick={() => onPreviewStateChange("correct")}
              style={{
                ...stateButton,
                background: previewState === "correct" ? "oklch(55% 0.16 155)" : "transparent",
                color: previewState === "correct" ? "white" : "oklch(35% 0.07 240)",
              }}
            >
              <Check size={16} strokeWidth={3} />
            </button>
            <button
              type="button"
              aria-label="One wrong answer in each activity"
              title="One wrong answer in each activity"
              onClick={() => onPreviewStateChange("wrong")}
              style={{
                ...stateButton,
                background: previewState === "wrong" ? "oklch(58% 0.2 25)" : "transparent",
                color: previewState === "wrong" ? "white" : "oklch(35% 0.07 240)",
              }}
            >
              <X size={16} strokeWidth={3} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const selectStyle: React.CSSProperties = {
  minWidth: 108,
  height: 36,
  borderRadius: 999,
  border: "1px solid rgba(255,255,255,0.14)",
  background: "rgba(255,255,255,0.95)",
  color: "oklch(20% 0.09 245)",
  padding: "0 12px",
  fontSize: 12.5,
  fontWeight: 800,
  fontFamily: "inherit",
  outline: "none",
};

const stateButton: React.CSSProperties = {
  width: 30,
  height: 30,
  borderRadius: "50%",
  border: "none",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  cursor: "pointer",
};
