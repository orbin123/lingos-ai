"use client";

import type { CSSProperties } from "react";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Flag, Wrench } from "lucide-react";

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

export default function AdminFeedbackReviewPage() {
  const queryClient = useQueryClient();
  const reviewQuery = useQuery({
    queryKey: ["admin", "feedback-review"],
    queryFn: adminApi.feedbackReview,
  });
  const updateMutation = useMutation({
    mutationFn: ({
      feedbackId,
      data,
    }: {
      feedbackId: number;
      data: FeedbackReviewUpdate;
    }) => adminApi.updateFeedbackReview(feedbackId, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "feedback-review"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "summary"] });
    },
  });

  const items = reviewQuery.data ?? [];

  return (
    <AdminLayout title="Feedback Review" eyebrow="Quality review">
      <div style={listStyle}>
        {items.map((item) => (
          <ReviewCard
            key={`${item.id}-${item.review_status}-${item.reviewed_at ?? "new"}`}
            item={item}
            isSaving={updateMutation.isPending}
            onUpdate={(data) => updateMutation.mutate({ feedbackId: item.id, data })}
          />
        ))}
        {items.length === 0 && (
          <AdminPanel style={{ padding: 20 }}>
            <p style={emptyStyle}>No feedback is waiting for review.</p>
          </AdminPanel>
        )}
      </div>
    </AdminLayout>
  );
}

function ReviewCard({
  item,
  isSaving,
  onUpdate,
}: {
  item: FeedbackReviewItem;
  isSaving: boolean;
  onUpdate: (data: FeedbackReviewUpdate) => void;
}) {
  const [adminNote, setAdminNote] = useState(item.admin_note ?? "");
  const feedbackMessage =
    typeof item.ai_feedback.overall_message === "string"
      ? item.ai_feedback.overall_message
      : null;

  return (
    <AdminPanel style={{ padding: 20 }}>
      <div style={cardHeadStyle}>
        <div>
          <h2 style={cardTitleStyle}>{item.task_title}</h2>
          <div style={metaStyle}>
            {item.user?.name ?? "Unknown learner"} - {formatAdminDateTime(item.created_at)}
          </div>
        </div>
        <ReviewStatusBadge status={item.review_status} />
      </div>

      <div style={contentGridStyle}>
        <section>
          <h3 style={sectionLabelStyle}>User response</h3>
          <pre style={preStyle}>
            {item.user_response_raw_text || JSON.stringify(item.user_response, null, 2)}
          </pre>
        </section>
        <section>
          <h3 style={sectionLabelStyle}>AI feedback</h3>
          <pre style={preStyle}>
            {feedbackMessage ?? JSON.stringify(item.ai_feedback, null, 2)}
          </pre>
        </section>
      </div>

      <div style={reviewBarStyle}>
        <div>
          <div style={sectionLabelStyle}>Score</div>
          <div style={scoreStyle}>{item.score.toFixed(1)}</div>
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
  minHeight: 124,
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
