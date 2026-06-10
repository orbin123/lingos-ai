"use client";

import type { CSSProperties } from "react";
import { Suspense, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Flag, GraduationCap, ListChecks, ThumbsDown, ThumbsUp, Wrench } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminButton,
  AdminPanel,
  formatAdminDateTime,
} from "@/components/admin/AdminPrimitives";
import {
  adminApi,
  type FeedbackReviewItem,
  type FeedbackReviewUpdate,
} from "@/lib/admin-api";

type Filter = "all" | "specific" | "rag";

export default function AdminFeedbackReviewPage() {
  // useSearchParams() must sit under a Suspense boundary in the App Router.
  return (
    <Suspense
      fallback={
        <AdminLayout title="Feedback Review" eyebrow="Quality review">
          <p style={emptyStyle}>Loading…</p>
        </AdminLayout>
      }
    >
      <FeedbackReviewContent />
    </Suspense>
  );
}

function FeedbackReviewContent() {
  const queryClient = useQueryClient();
  const searchParams = useSearchParams();

  // Deep-link target from /admin/ai-quality (?feedback_type=…&feedback_id=…).
  const targetType = searchParams.get("feedback_type");
  const targetIdParam = searchParams.get("feedback_id");
  const targetId = targetIdParam != null ? Number(targetIdParam) : null;
  const hasTarget =
    (targetType === "specific" || targetType === "rag") &&
    targetId != null &&
    Number.isFinite(targetId);

  const [filter, setFilter] = useState<Filter>(
    targetType === "specific" || targetType === "rag" ? targetType : "all",
  );

  const reviewQuery = useQuery({
    queryKey: ["admin", "feedback-review"],
    queryFn: adminApi.feedbackReview,
  });
  const updateMutation = useMutation({
    mutationFn: ({
      item,
      data,
    }: {
      item: FeedbackReviewItem;
      data: FeedbackReviewUpdate;
    }) => adminApi.updateFeedbackReview(item.feedback_type, item.feedback_id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "feedback-review"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "summary"] });
    },
  });

  const items = reviewQuery.data ?? [];
  const filtered = useMemo(
    () => (filter === "all" ? items : items.filter((i) => i.feedback_type === filter)),
    [items, filter],
  );

  return (
    <AdminLayout title="Feedback Review" eyebrow="Quality review">
      <div style={tabsStyle}>
        <FilterTab label="All" value="all" active={filter} onClick={setFilter} />
        <FilterTab label="Activity feedback" value="specific" active={filter} onClick={setFilter} />
        <FilterTab label="Coach's Note (RAG)" value="rag" active={filter} onClick={setFilter} />
      </div>

      <div style={listStyle}>
        {filtered.map((item) => (
          <ReviewCard
            key={`${item.feedback_type}-${item.feedback_id}-${item.review_status}-${item.reviewed_at ?? "new"}`}
            item={item}
            isSaving={updateMutation.isPending}
            highlight={
              hasTarget &&
              item.feedback_type === targetType &&
              item.feedback_id === targetId
            }
            onUpdate={(data) => updateMutation.mutate({ item, data })}
          />
        ))}
        {filtered.length === 0 && (
          <AdminPanel style={{ padding: 20 }}>
            <p style={emptyStyle}>
              {reviewQuery.isLoading ? "Loading…" : "No feedback is waiting for review."}
            </p>
          </AdminPanel>
        )}
      </div>
    </AdminLayout>
  );
}

function FilterTab({
  label,
  value,
  active,
  onClick,
}: {
  label: string;
  value: Filter;
  active: Filter;
  onClick: (v: Filter) => void;
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

function ReviewCard({
  item,
  isSaving,
  highlight = false,
  onUpdate,
}: {
  item: FeedbackReviewItem;
  isSaving: boolean;
  highlight?: boolean;
  onUpdate: (data: FeedbackReviewUpdate) => void;
}) {
  const [adminNote, setAdminNote] = useState(item.admin_note ?? "");
  const isRag = item.feedback_type === "rag";
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
          <div style={typeRowStyle}>
            <span style={typeBadgeStyle}>
              {isRag ? <GraduationCap size={13} /> : <ListChecks size={13} />}
              {isRag ? "Coach's Note" : "Activity feedback"}
            </span>
            {item.rating && <RatingBadge rating={item.rating} />}
          </div>
          <h2 style={cardTitleStyle}>{item.context_label}</h2>
          <div style={metaStyle}>
            {item.user?.name ?? "Unknown learner"} · {formatAdminDateTime(item.created_at)}
          </div>
        </div>
        <ReviewStatusBadge status={item.review_status} />
      </div>

      {isRag ? (
        <section>
          <h3 style={sectionLabelStyle}>Coach&apos;s Note</h3>
          <pre style={preStyle}>{item.mentor_note ?? "—"}</pre>
        </section>
      ) : (
        <div style={contentGridStyle}>
          <section>
            <h3 style={sectionLabelStyle}>Summary</h3>
            <pre style={preStyle}>{item.summary ?? "—"}</pre>
          </section>
          <section>
            <h3 style={sectionLabelStyle}>Mistakes & tip</h3>
            <pre style={preStyle}>
              {JSON.stringify(
                { mistakes: item.mistakes, did_well: item.did_well, next_tip: item.next_tip },
                null,
                2,
              )}
            </pre>
          </section>
        </div>
      )}

      <div style={reviewBarStyle}>
        <div>
          <div style={sectionLabelStyle}>Score</div>
          <div style={scoreStyle}>{item.score !== null ? item.score.toFixed(1) : "—"}</div>
        </div>
        <label style={noteFieldStyle}>
          <span style={sectionLabelStyle}>Admin note</span>
          <input
            value={adminNote}
            onChange={(event) => setAdminNote(event.target.value)}
            style={inputStyle}
          />
        </label>
        <div style={actionsStyle}>
          <AdminButton
            disabled={isSaving}
            onClick={() => onUpdate({ review_status: "approved", admin_note: adminNote })}
          >
            <Check size={16} />
            Approve
          </AdminButton>
          <AdminButton
            tone="danger"
            disabled={isSaving}
            onClick={() => onUpdate({ review_status: "flagged", admin_note: adminNote })}
          >
            <Flag size={16} />
            Flag
          </AdminButton>
          <AdminButton
            tone="secondary"
            disabled={isSaving}
            onClick={() => onUpdate({ review_status: "fixed", admin_note: adminNote })}
          >
            <Wrench size={16} />
            Mark fixed
          </AdminButton>
        </div>
      </div>
      </AdminPanel>
    </div>
  );
}

function RatingBadge({ rating }: { rating: "like" | "dislike" }) {
  const liked = rating === "like";
  return (
    <span
      style={{
        ...ratingBadgeStyle,
        background: liked ? "oklch(94% 0.06 155)" : "oklch(95% 0.05 25)",
        color: liked ? "oklch(34% 0.13 155)" : "oklch(42% 0.16 25)",
      }}
    >
      {liked ? <ThumbsUp size={12} /> : <ThumbsDown size={12} />}
      {liked ? "Liked" : "Disliked"}
    </span>
  );
}

function ReviewStatusBadge({ status }: { status: FeedbackReviewItem["review_status"] }) {
  const colors = {
    pending: ["oklch(96% 0.05 80)", "oklch(42% 0.12 70)"],
    approved: ["oklch(94% 0.06 155)", "oklch(34% 0.13 155)"],
    flagged: ["oklch(95% 0.04 25)", "oklch(42% 0.16 25)"],
    fixed: ["oklch(94% 0.04 240)", "#00599e"],
  } as const;
  const [background, color] = colors[status];
  return <span style={{ ...badgeStyle, background, color }}>{status}</span>;
}

const tabsStyle: CSSProperties = {
  display: "flex",
  gap: 8,
  marginBottom: 18,
};

const tabStyle: CSSProperties = {
  minHeight: 36,
  padding: "0 14px",
  borderRadius: 999,
  border: "1px solid oklch(88% 0.018 245)",
  background: "white",
  color: "oklch(40% 0.05 245)",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 13,
  fontWeight: 750,
};

const tabActiveStyle: CSSProperties = {
  background: "oklch(94% 0.04 240)",
  borderColor: "oklch(82% 0.05 240)",
  color: "#00599e",
};

const typeRowStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 8,
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

const ratingBadgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 5,
  padding: "3px 9px",
  borderRadius: 999,
  fontSize: 11.5,
  fontWeight: 800,
};

const listStyle: CSSProperties = {
  display: "grid",
  gap: 16,
};

const cardHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: 16,
  marginBottom: 16,
};

const cardTitleStyle: CSSProperties = {
  margin: 0,
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
  minHeight: 90,
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

const reviewBarStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "90px minmax(180px, 1fr) auto",
  gap: 14,
  alignItems: "end",
  marginTop: 16,
};

const scoreStyle: CSSProperties = {
  marginTop: 6,
  color: "oklch(18% 0.055 245)",
  fontSize: 28,
  fontWeight: 850,
};

const noteFieldStyle: CSSProperties = {
  display: "grid",
  gap: 7,
};

const inputStyle: CSSProperties = {
  width: "100%",
  minHeight: 40,
  borderRadius: 8,
  border: "1px solid oklch(86% 0.018 245)",
  padding: "0 11px",
  color: "oklch(18% 0.055 245)",
  fontSize: 14,
  fontWeight: 650,
  fontFamily: "inherit",
  background: "white",
};

const actionsStyle: CSSProperties = {
  display: "flex",
  gap: 8,
  flexWrap: "wrap",
  justifyContent: "flex-end",
};

const badgeStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  minHeight: 28,
  borderRadius: 999,
  padding: "0 10px",
  fontSize: 12,
  fontWeight: 800,
  textTransform: "capitalize",
};

const emptyStyle: CSSProperties = {
  margin: 0,
  color: "oklch(48% 0.045 245)",
  fontWeight: 700,
};
