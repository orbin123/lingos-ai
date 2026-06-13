"use client";

// Admin list + analytics for app reviews submitted by users through the
// in-app feedback prompt. Reads /admin/app-reviews (with optional rating
// filter) and /admin/reviews/stats.

import { useState, type CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";
import { Star } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import {
  adminApi,
  type AppReviewItem,
  type ReviewStats,
} from "@/lib/admin-api";

export default function AdminUserReviewsPage() {
  const [ratingFilter, setRatingFilter] = useState<number | null>(null);

  const statsQuery = useQuery({
    queryKey: ["admin", "review-stats"],
    queryFn: adminApi.reviewStats,
  });
  const reviewsQuery = useQuery({
    queryKey: ["admin", "app-reviews", ratingFilter],
    queryFn: () => adminApi.appReviews(ratingFilter ?? undefined),
  });

  const reviews = reviewsQuery.data ?? [];
  const stats = statsQuery.data;

  return (
    <AdminLayout title="User Reviews" eyebrow="Product feedback">
      <StatsPanel stats={stats} />

      <div style={filterRowStyle}>
        <span style={filterLabelStyle}>Filter by rating</span>
        <button
          onClick={() => setRatingFilter(null)}
          style={chipStyle(ratingFilter === null)}
          type="button"
        >
          All
        </button>
        {[5, 4, 3, 2, 1].map((n) => (
          <button
            key={n}
            onClick={() => setRatingFilter(n)}
            style={chipStyle(ratingFilter === n)}
            type="button"
          >
            {n}★
          </button>
        ))}
      </div>

      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Rating</th>
              <th style={thStyle}>Feedback</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Date</th>
            </tr>
          </thead>
          <tbody>
            {reviews.map((review) => (
              <ReviewRow key={review.id} review={review} />
            ))}
            {reviews.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={5}>
                  {reviewsQuery.isLoading
                    ? "Loading…"
                    : ratingFilter
                      ? `No ${ratingFilter}★ reviews.`
                      : "No reviews submitted yet."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function StatsPanel({ stats }: { stats: ReviewStats | undefined }) {
  const submissionRate =
    stats?.submission_rate != null
      ? `${Math.round(stats.submission_rate * 100)}%`
      : "—";
  const avg =
    stats?.average_rating != null ? stats.average_rating.toFixed(1) : "—";

  return (
    <>
      <div style={statRowStyle}>
        <StatCard label="Total reviews" value={String(stats?.total_reviews ?? "—")} />
        <StatCard
          label="Average rating"
          value={avg}
          suffix={stats?.average_rating != null ? "/5" : undefined}
        />
        <StatCard label="Submission rate" value={submissionRate} />
        <StatCard
          label="Prompts shown"
          value={String(stats?.prompts_shown ?? "—")}
        />
      </div>

      {stats && (
        <div style={breakdownRowStyle}>
          <RatingDistribution
            distribution={stats.rating_distribution}
            total={stats.total_reviews}
          />
          <ThemeList title="Top improvement themes" items={stats.top_improvements} />
          <ThemeList title="Top bug themes" items={stats.top_bugs} />
          <TrendList trend={stats.trend} />
        </div>
      )}
    </>
  );
}

function RatingDistribution({
  distribution,
  total,
}: {
  distribution: Record<string, number>;
  total: number;
}) {
  return (
    <div style={breakdownCardStyle}>
      <div style={breakdownTitleStyle}>Rating distribution</div>
      {[5, 4, 3, 2, 1].map((n) => {
        const count = distribution[String(n)] ?? 0;
        const pct = total > 0 ? (count / total) * 100 : 0;
        return (
          <div key={n} style={distRowStyle}>
            <span style={distLabelStyle}>{n}★</span>
            <div style={distTrackStyle}>
              <div style={{ ...distFillStyle, width: `${pct}%` }} />
            </div>
            <span style={distCountStyle}>{count}</span>
          </div>
        );
      })}
    </div>
  );
}

function ThemeList({
  title,
  items,
}: {
  title: string;
  items: { text: string; count: number }[];
}) {
  return (
    <div style={breakdownCardStyle}>
      <div style={breakdownTitleStyle}>{title}</div>
      {items.length === 0 && <div style={mutedTextStyle}>No data yet.</div>}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
        {items.map((item) => (
          <span key={item.text} style={tagStyle}>
            {item.text}
            <span style={tagCountStyle}>{item.count}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function TrendList({
  trend,
}: {
  trend: { date: string; count: number; average_rating: number }[];
}) {
  const recent = trend.slice(-7);
  return (
    <div style={breakdownCardStyle}>
      <div style={breakdownTitleStyle}>Trend (last 30 days)</div>
      {recent.length === 0 && <div style={mutedTextStyle}>No data yet.</div>}
      {recent.map((p) => (
        <div key={p.date} style={trendRowStyle}>
          <span style={mutedTextStyle}>{formatAdminDate(p.date)}</span>
          <span style={{ fontWeight: 750 }}>
            {p.count} · {p.average_rating.toFixed(1)}★
          </span>
        </div>
      ))}
    </div>
  );
}

function ReviewRow({ review }: { review: AppReviewItem }) {
  const hasStructured =
    review.positive_feedback || review.improvement_feedback || review.bug_report;
  return (
    <tr>
      <td style={tdStyle}>
        {review.user ? (
          <>
            <div style={strongTextStyle}>{review.user.name}</div>
            <div style={mutedTextStyle}>{review.user.email}</div>
          </>
        ) : (
          <span style={mutedTextStyle}>Deleted user</span>
        )}
      </td>
      <td style={tdStyle}>
        <Stars rating={review.rating} />
      </td>
      <td style={tdStyle}>
        {hasStructured ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 6, maxWidth: 460 }}>
            {review.positive_feedback && (
              <Section label="Likes" tone="positive" text={review.positive_feedback} />
            )}
            {review.improvement_feedback && (
              <Section
                label="Improve"
                tone="improve"
                text={review.improvement_feedback}
              />
            )}
            {review.bug_report && (
              <Section label="Bug" tone="bug" text={review.bug_report} />
            )}
          </div>
        ) : review.title || review.body ? (
          <div style={{ maxWidth: 460 }}>
            {review.title && <div style={strongTextStyle}>{review.title}</div>}
            {review.body && <div style={bodyStyle}>{review.body}</div>}
          </div>
        ) : (
          <span style={mutedTextStyle}>—</span>
        )}
      </td>
      <td style={tdStyle}>
        <span style={statusPillStyle}>{review.status}</span>
      </td>
      <td style={tdStyle}>{formatAdminDate(review.created_at)}</td>
    </tr>
  );
}

function Section({
  label,
  tone,
  text,
}: {
  label: string;
  tone: "positive" | "improve" | "bug";
  text: string;
}) {
  return (
    <div>
      <span style={{ ...sectionLabelStyle, ...sectionToneStyle[tone] }}>{label}</span>
      <span style={sectionTextStyle}>{text}</span>
    </div>
  );
}

function Stars({ rating }: { rating: number }) {
  return (
    <div style={{ display: "flex", gap: 2 }} aria-label={`${rating} out of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Star
          key={n}
          size={15}
          fill={n <= rating ? "oklch(75% 0.15 80)" : "none"}
          color={n <= rating ? "oklch(70% 0.15 80)" : "oklch(82% 0.02 245)"}
        />
      ))}
    </div>
  );
}

function StatCard({
  label,
  value,
  suffix,
}: {
  label: string;
  value: string;
  suffix?: string;
}) {
  return (
    <div style={statCardStyle}>
      <div style={statLabelStyle}>{label}</div>
      <div style={statValueStyle}>
        {value}
        {suffix && (
          <span style={{ fontSize: 16, color: "oklch(55% 0.04 245)" }}>{suffix}</span>
        )}
      </div>
    </div>
  );
}

const statRowStyle: CSSProperties = {
  display: "flex",
  gap: 14,
  marginBottom: 14,
  flexWrap: "wrap",
};

const statCardStyle: CSSProperties = {
  minWidth: 160,
  flex: "1 1 160px",
  padding: "14px 18px",
  borderRadius: 12,
  border: "1px solid oklch(90% 0.014 245)",
  background: "white",
};

const statLabelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 800,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
};

const statValueStyle: CSSProperties = {
  marginTop: 6,
  color: "oklch(18% 0.055 245)",
  fontSize: 26,
  fontWeight: 850,
};

const breakdownRowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: 14,
  marginBottom: 20,
};

const breakdownCardStyle: CSSProperties = {
  padding: "14px 16px",
  borderRadius: 12,
  border: "1px solid oklch(90% 0.014 245)",
  background: "white",
};

const breakdownTitleStyle: CSSProperties = {
  color: "oklch(30% 0.05 245)",
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: "0.03em",
  textTransform: "uppercase",
  marginBottom: 10,
};

const distRowStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 6,
};

const distLabelStyle: CSSProperties = {
  width: 24,
  fontSize: 12,
  fontWeight: 750,
  color: "oklch(40% 0.05 245)",
};

const distTrackStyle: CSSProperties = {
  flex: 1,
  height: 8,
  borderRadius: 999,
  background: "oklch(94% 0.01 245)",
  overflow: "hidden",
};

const distFillStyle: CSSProperties = {
  height: "100%",
  borderRadius: 999,
  background: "oklch(70% 0.15 80)",
};

const distCountStyle: CSSProperties = {
  width: 28,
  textAlign: "right",
  fontSize: 12,
  fontWeight: 700,
  color: "oklch(35% 0.04 245)",
};

const trendRowStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  fontSize: 12,
  padding: "3px 0",
  color: "oklch(30% 0.04 245)",
};

const tagStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "3px 8px",
  borderRadius: 999,
  background: "oklch(95% 0.02 245)",
  color: "oklch(32% 0.05 245)",
  fontSize: 12,
  fontWeight: 650,
};

const tagCountStyle: CSSProperties = {
  fontSize: 11,
  fontWeight: 800,
  color: "oklch(50% 0.04 245)",
};

const filterRowStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
  marginBottom: 14,
  flexWrap: "wrap",
};

const filterLabelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 750,
  marginRight: 4,
};

const chipStyle = (active: boolean): CSSProperties => ({
  padding: "5px 12px",
  borderRadius: 999,
  border: active
    ? "1px solid oklch(52% 0.18 240)"
    : "1px solid oklch(88% 0.02 245)",
  background: active ? "oklch(52% 0.18 240)" : "white",
  color: active ? "white" : "oklch(35% 0.05 245)",
  fontSize: 12,
  fontWeight: 750,
  cursor: "pointer",
});

const strongTextStyle: CSSProperties = {
  color: "oklch(18% 0.055 245)",
  fontWeight: 800,
};

const mutedTextStyle: CSSProperties = {
  marginTop: 3,
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 650,
};

const bodyStyle: CSSProperties = {
  marginTop: 4,
  color: "oklch(35% 0.04 245)",
  fontSize: 13,
  fontWeight: 500,
  maxWidth: 420,
};

const sectionLabelStyle: CSSProperties = {
  display: "inline-block",
  marginRight: 8,
  padding: "1px 7px",
  borderRadius: 6,
  fontSize: 10.5,
  fontWeight: 800,
  letterSpacing: "0.03em",
  textTransform: "uppercase",
  verticalAlign: "middle",
};

const sectionToneStyle: Record<string, CSSProperties> = {
  positive: { background: "oklch(94% 0.05 150)", color: "oklch(38% 0.12 150)" },
  improve: { background: "oklch(95% 0.06 250)", color: "oklch(42% 0.14 250)" },
  bug: { background: "oklch(95% 0.06 28)", color: "oklch(48% 0.16 28)" },
};

const sectionTextStyle: CSSProperties = {
  color: "oklch(32% 0.04 245)",
  fontSize: 13,
  fontWeight: 500,
};

const statusPillStyle: CSSProperties = {
  display: "inline-block",
  padding: "3px 10px",
  borderRadius: 999,
  background: "oklch(94% 0.04 150)",
  color: "oklch(40% 0.12 150)",
  fontSize: 12,
  fontWeight: 750,
  textTransform: "capitalize",
};
