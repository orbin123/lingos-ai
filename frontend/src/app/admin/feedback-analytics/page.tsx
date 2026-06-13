"use client";

import type { CSSProperties } from "react";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  GraduationCap,
  ListChecks,
  ThumbsDown,
  ThumbsUp,
  MinusCircle,
} from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import { AdminPanel, formatAdminDateTime } from "@/components/admin/AdminPrimitives";
import {
  adminApi,
  type FeedbackAnalyticsItem,
  type FeedbackReactionType,
  type FeedbackReactionFilter,
} from "@/lib/admin-api";

type TypeFilter = "ALL" | FeedbackReactionType;
type ReactionFilter = "ALL" | FeedbackReactionFilter;

export default function AdminFeedbackAnalyticsPage() {
  // useSearchParams() must sit under a Suspense boundary in the App Router.
  return (
    <Suspense
      fallback={
        <AdminLayout title="Feedback Analytics" eyebrow="Quality signal">
          <p style={emptyStyle}>Loading…</p>
        </AdminLayout>
      }
    >
      <FeedbackAnalyticsContent />
    </Suspense>
  );
}

function FeedbackAnalyticsContent() {
  const searchParams = useSearchParams();

  // Deep-link target from /admin/ai-quality (?feedback_type=…&feedback_id=…).
  const targetType = searchParams.get("feedback_type");
  const targetIdParam = searchParams.get("feedback_id");
  const targetId = targetIdParam != null ? Number(targetIdParam) : null;
  const hasTarget =
    (targetType === "ACTIVITY_FEEDBACK" || targetType === "COACH_NOTE") &&
    targetId != null &&
    Number.isFinite(targetId);

  const [typeFilter, setTypeFilter] = useState<TypeFilter>(
    targetType === "ACTIVITY_FEEDBACK" || targetType === "COACH_NOTE"
      ? targetType
      : "ALL",
  );
  const [reactionFilter, setReactionFilter] = useState<ReactionFilter>("ALL");

  const statsQuery = useQuery({
    queryKey: ["admin", "feedback-analytics", "stats"],
    queryFn: adminApi.feedbackAnalyticsStats,
  });

  const listQuery = useQuery({
    queryKey: ["admin", "feedback-analytics", typeFilter, reactionFilter],
    queryFn: () =>
      adminApi.feedbackAnalytics({
        feedbackType: typeFilter === "ALL" ? undefined : typeFilter,
        reaction: reactionFilter === "ALL" ? undefined : reactionFilter,
      }),
  });

  const stats = statsQuery.data;
  const items = listQuery.data ?? [];

  const positiveRatePct = useMemo(() => {
    if (!stats || stats.positive_rate == null) return "—";
    return `${(stats.positive_rate * 100).toFixed(1)}%`;
  }, [stats]);

  return (
    <AdminLayout title="Feedback Analytics" eyebrow="Quality signal">
      {/* KPI cards */}
      <div style={kpiGridStyle}>
        <KpiCard label="Total feedback items" value={stats?.total_items ?? "—"} />
        <KpiCard label="Liked" value={stats?.liked ?? "—"} tone="like" />
        <KpiCard label="Disliked" value={stats?.disliked ?? "—"} tone="dislike" />
        <KpiCard label="No reaction" value={stats?.no_reaction ?? "—"} />
        <KpiCard label="Positive feedback rate" value={positiveRatePct} tone="rate" />
      </div>

      {/* Filters */}
      <div style={filterRowStyle}>
        <span style={filterLabelStyle}>Type</span>
        <FilterTab label="All" value="ALL" active={typeFilter} onClick={setTypeFilter} />
        <FilterTab
          label="Activity feedback"
          value="ACTIVITY_FEEDBACK"
          active={typeFilter}
          onClick={setTypeFilter}
        />
        <FilterTab
          label="Coach Notes"
          value="COACH_NOTE"
          active={typeFilter}
          onClick={setTypeFilter}
        />
      </div>
      <div style={filterRowStyle}>
        <span style={filterLabelStyle}>Reaction</span>
        <FilterTab label="All reactions" value="ALL" active={reactionFilter} onClick={setReactionFilter} />
        <FilterTab label="Liked" value="LIKE" active={reactionFilter} onClick={setReactionFilter} />
        <FilterTab label="Disliked" value="DISLIKE" active={reactionFilter} onClick={setReactionFilter} />
        <FilterTab label="No reaction" value="NONE" active={reactionFilter} onClick={setReactionFilter} />
      </div>

      <div style={listStyle}>
        {items.map((item) => (
          <FeedbackCard
            key={`${item.feedback_type}-${item.feedback_id}`}
            item={item}
            highlight={
              hasTarget &&
              item.feedback_type === targetType &&
              item.feedback_id === targetId
            }
          />
        ))}
        {items.length === 0 && (
          <AdminPanel style={{ padding: 20 }}>
            <p style={emptyStyle}>
              {listQuery.isLoading
                ? "Loading…"
                : "No feedback matches these filters."}
            </p>
          </AdminPanel>
        )}
      </div>
    </AdminLayout>
  );
}

function KpiCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: number | string;
  tone?: "like" | "dislike" | "rate";
}) {
  const accent =
    tone === "like"
      ? "oklch(45% 0.14 155)"
      : tone === "dislike"
        ? "oklch(48% 0.16 25)"
        : tone === "rate"
          ? "#00599e"
          : "oklch(18% 0.055 245)";
  return (
    <AdminPanel style={{ padding: "16px 18px" }}>
      <div style={kpiLabelStyle}>{label}</div>
      <div style={{ ...kpiValueStyle, color: accent }}>{value}</div>
    </AdminPanel>
  );
}

function FilterTab<T extends string>({
  label,
  value,
  active,
  onClick,
}: {
  label: string;
  value: T;
  active: T;
  onClick: (v: T) => void;
}) {
  const isActive = active === value;
  return (
    <button
      type="button"
      onClick={() => onClick(value)}
      style={{ ...tabStyle, ...(isActive ? tabActiveStyle : null) }}
    >
      {label}
    </button>
  );
}

function FeedbackCard({
  item,
  highlight = false,
}: {
  item: FeedbackAnalyticsItem;
  highlight?: boolean;
}) {
  const isCoachNote = item.feedback_type === "COACH_NOTE";
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (highlight && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [highlight]);

  return (
    <div
      ref={cardRef}
      style={{
        borderRadius: 14,
        ...(highlight
          ? {
              outline: "2px solid #0070C4",
              outlineOffset: 2,
              boxShadow: "0 0 0 4px oklch(94% 0.04 240)",
            }
          : null),
      }}
    >
      <AdminPanel style={{ padding: 20 }}>
        <div style={cardHeadStyle}>
          <div>
            <span style={typeBadgeStyle}>
              {isCoachNote ? <GraduationCap size={13} /> : <ListChecks size={13} />}
              {isCoachNote ? "Coach Note" : "Activity feedback"}
            </span>
            <h2 style={cardTitleStyle}>{item.context_label}</h2>
            <div style={metaStyle}>
              {item.user?.name ?? "Unknown learner"} ·{" "}
              {formatAdminDateTime(item.created_at)}
            </div>
          </div>
          {!isCoachNote && (
            <div style={scoreWrapStyle}>
              <div style={sectionLabelStyle}>Score</div>
              <div style={scoreStyle}>
                {item.score !== null ? `${item.score.toFixed(0)}/10` : "—"}
              </div>
            </div>
          )}
        </div>

        {isCoachNote ? (
          <section>
            <h3 style={sectionLabelStyle}>Coach Note</h3>
            <pre style={preStyle}>{item.mentor_note ?? "—"}</pre>
          </section>
        ) : (
          <div style={contentGridStyle}>
            <section>
              <h3 style={sectionLabelStyle}>Summary</h3>
              <pre style={preStyle}>{item.summary ?? "—"}</pre>
            </section>
            <section>
              <h3 style={sectionLabelStyle}>Mistakes &amp; tips</h3>
              <pre style={preStyle}>
                {JSON.stringify(
                  {
                    mistakes: item.mistakes,
                    did_well: item.did_well,
                    next_tip: item.next_tip,
                  },
                  null,
                  2,
                )}
              </pre>
            </section>
          </div>
        )}

        <div style={reactionRowStyle}>
          <span style={sectionLabelStyle}>User reaction</span>
          <ReactionBadge reaction={item.user_reaction} />
        </div>
      </AdminPanel>
    </div>
  );
}

function ReactionBadge({ reaction }: { reaction: "LIKE" | "DISLIKE" | null }) {
  if (reaction === "LIKE") {
    return (
      <span
        style={{
          ...badgeStyle,
          background: "oklch(94% 0.06 155)",
          color: "oklch(34% 0.13 155)",
        }}
      >
        <ThumbsUp size={13} /> Liked
      </span>
    );
  }
  if (reaction === "DISLIKE") {
    return (
      <span
        style={{
          ...badgeStyle,
          background: "oklch(95% 0.05 25)",
          color: "oklch(42% 0.16 25)",
        }}
      >
        <ThumbsDown size={13} /> Disliked
      </span>
    );
  }
  return (
    <span
      style={{
        ...badgeStyle,
        background: "oklch(95% 0.01 245)",
        color: "oklch(48% 0.04 245)",
      }}
    >
      <MinusCircle size={13} /> No reaction
    </span>
  );
}

const kpiGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
  gap: 12,
  marginBottom: 20,
};

const kpiLabelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 800,
  letterSpacing: "0.04em",
  textTransform: "uppercase",
};

const kpiValueStyle: CSSProperties = {
  marginTop: 8,
  fontSize: 28,
  fontWeight: 850,
};

const filterRowStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 12,
  flexWrap: "wrap",
};

const filterLabelStyle: CSSProperties = {
  marginRight: 4,
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 850,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
  minWidth: 64,
};

const tabStyle: CSSProperties = {
  minHeight: 34,
  padding: "0 13px",
  borderRadius: 999,
  border: "1px solid oklch(88% 0.018 245)",
  background: "white",
  color: "oklch(40% 0.05 245)",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 12.5,
  fontWeight: 750,
};

const tabActiveStyle: CSSProperties = {
  background: "oklch(94% 0.04 240)",
  borderColor: "oklch(82% 0.05 240)",
  color: "#00599e",
};

const listStyle: CSSProperties = {
  display: "grid",
  gap: 16,
  marginTop: 8,
};

const cardHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: 16,
  marginBottom: 16,
};

const typeBadgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 5,
  padding: "3px 9px",
  borderRadius: 999,
  background: "oklch(95% 0.02 245)",
  color: "oklch(40% 0.06 245)",
  fontSize: 11.5,
  fontWeight: 800,
  textTransform: "uppercase",
  letterSpacing: "0.03em",
};

const cardTitleStyle: CSSProperties = {
  margin: "8px 0 0",
  color: "oklch(18% 0.055 245)",
  fontSize: 18,
  fontWeight: 850,
};

const metaStyle: CSSProperties = {
  marginTop: 5,
  color: "oklch(48% 0.045 245)",
  fontSize: 13,
  fontWeight: 650,
};

const scoreWrapStyle: CSSProperties = {
  textAlign: "right",
  flexShrink: 0,
};

const contentGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 14,
};

const sectionLabelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 850,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
};

const preStyle: CSSProperties = {
  minHeight: 80,
  maxHeight: 260,
  margin: "8px 0 0",
  padding: 14,
  overflow: "auto",
  borderRadius: 8,
  background: "oklch(97% 0.01 245)",
  color: "oklch(25% 0.06 245)",
  whiteSpace: "pre-wrap",
  overflowWrap: "anywhere",
  fontSize: 13,
  lineHeight: 1.5,
};

const scoreStyle: CSSProperties = {
  marginTop: 6,
  color: "oklch(18% 0.055 245)",
  fontSize: 26,
  fontWeight: 850,
};

const reactionRowStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  marginTop: 16,
  paddingTop: 14,
  borderTop: "1px solid oklch(92% 0.012 245)",
};

const badgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  minHeight: 28,
  borderRadius: 999,
  padding: "0 12px",
  fontSize: 12.5,
  fontWeight: 800,
};

const emptyStyle: CSSProperties = {
  margin: 0,
  color: "oklch(48% 0.045 245)",
  fontWeight: 700,
};
