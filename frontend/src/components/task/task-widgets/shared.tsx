"use client";

export type WidgetState = "before" | "after";

export const I = {
  check: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M4 8.5l2.5 2.5L12 5.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  spark: (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
      <path d="M7 1L8 5L12 6L8 7L7 11L6 7L2 6L6 5L7 1Z" fill="currentColor" />
    </svg>
  ),
  play: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
      <path d="M8 5v14l11-7L8 5z" />
    </svg>
  ),
  pause: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
      <rect x="7" y="5" width="3" height="14" />
      <rect x="14" y="5" width="3" height="14" />
    </svg>
  ),
  playMini: (
    <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
      <path d="M8 5v14l11-7L8 5z" />
    </svg>
  ),
  mic: (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
      <rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor" />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
  micSm: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
      <rect x="9" y="3" width="6" height="11" rx="3" fill="currentColor" />
      <path d="M5 11a7 7 0 0 0 14 0M12 18v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  ),
  arrowR: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  arrowL: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M13 8H3M7 4L3 8l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  replay: (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
      <path d="M11 4l1-2v3h-3M11.5 4.5A4.5 4.5 0 1 0 12 8.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  clock: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
      <path d="M8 5v3.5l2.5 1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  rule: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M4 2h6l2.5 2.5V14H4V2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M10 2v3h2.5M6 7h4M6 9.5h4M6 12h2.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  ),
  lock: (
    <svg width="11" height="11" viewBox="0 0 14 14" fill="none">
      <rect x="3" y="6" width="8" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M5 6V4.5a2 2 0 0 1 4 0V6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
  doc: (
    <svg width="11" height="11" viewBox="0 0 14 14" fill="none">
      <path d="M3 2h6l2 2v8H3V2z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M9 2v2h2" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  ),
  stop: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  ),
  send: (
    <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
      <path d="M1.5 7L13 2L8 13L7 8.5L1.5 7z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  ),
  ear: (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
      <path d="M5 12a3 3 0 0 1-1.5-5.5C3.5 4 5.5 2 8 2s4 1.5 4 3.5c0 1.5-.5 2-1.5 3s-1 1.5-1 2.5-1 1-2 1" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
};

interface TaskHeaderProps {
  topic: string;
  intro: { title: string; body: string };
  sub_skill: string;
  activity: string;
  time: number;
  target_words?: { word: string; used: boolean }[];
  concepts?: string[];
}

export function TaskHeader({ topic, intro, sub_skill, activity, time, target_words, concepts }: TaskHeaderProps) {
  return (
    <div className="tw-task-header">
      <div className="tw-task-topic">{topic}</div>
      <div className="tw-task-title">{intro.title}</div>
      <div className="tw-task-intro">{intro.body}</div>
      <div className="tw-task-pill-row">
        <span className="tw-task-pill">
          <span className="tw-dot" />
          {sub_skill}
        </span>
        <span className="tw-task-pill activity">
          <span className="tw-dot" />
          {activity}
        </span>
        <span className="tw-task-pill time">
          <span className="tw-dot" />
          {I.clock} {time} min
        </span>
      </div>
      {((target_words && target_words.length > 0) || (concepts && concepts.length > 0)) && (
        <div className="tw-target-chip-row">
          {target_words?.map((w) => (
            <span key={w.word} className={`tw-target-chip${w.used ? " used" : ""}`}>
              <span className={w.used ? "tw-strike" : ""}>{w.word}</span>
            </span>
          ))}
          {concepts?.map((c) => (
            <span key={c} className="tw-target-chip">
              {c}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
