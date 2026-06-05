"use client";

// Read-only admin list of app reviews submitted by users. The user-facing
// submission UI (a dedicated in-app "review the application" surface) is a
// later task; the backend POST /api/reviews endpoint already exists.

import type { CSSProperties } from "react";
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
import { adminApi, type AppReviewItem } from "@/lib/admin-api";

export default function AdminUserReviewsPage() {
  const reviewsQuery = useQuery({
    queryKey: ["admin", "app-reviews"],
    queryFn: adminApi.appReviews,
  });

  const reviews = reviewsQuery.data ?? [];
  const average =
    reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
      : "—";

  return (
    <AdminLayout title="User Reviews" eyebrow="Product feedback">
      <div style={statRowStyle}>
        <div style={statCardStyle}>
          <div style={statLabelStyle}>Total reviews</div>
          <div style={statValueStyle}>{reviews.length}</div>
        </div>
        <div style={statCardStyle}>
          <div style={statLabelStyle}>Average rating</div>
          <div style={statValueStyle}>
            {average}
            {reviews.length > 0 && <span style={{ fontSize: 16, color: "oklch(55% 0.04 245)" }}>/5</span>}
          </div>
        </div>
      </div>

      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>User</th>
              <th style={thStyle}>Rating</th>
              <th style={thStyle}>Review</th>
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
                  {reviewsQuery.isLoading ? "Loading…" : "No reviews submitted yet."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

function ReviewRow({ review }: { review: AppReviewItem }) {
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
        {review.title && <div style={strongTextStyle}>{review.title}</div>}
        {review.body && <div style={bodyStyle}>{review.body}</div>}
        {!review.title && !review.body && <span style={mutedTextStyle}>—</span>}
      </td>
      <td style={tdStyle}>
        <span style={statusPillStyle}>{review.status}</span>
      </td>
      <td style={tdStyle}>{formatAdminDate(review.created_at)}</td>
    </tr>
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

const statRowStyle: CSSProperties = {
  display: "flex",
  gap: 14,
  marginBottom: 20,
};

const statCardStyle: CSSProperties = {
  minWidth: 160,
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
