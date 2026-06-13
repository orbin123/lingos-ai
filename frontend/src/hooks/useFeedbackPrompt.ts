"use client";

import { useEffect } from "react";

import { feedbackApi } from "@/lib/feedback-api";
import { useAuthStore } from "@/store/authStore";
import { useFeedbackStore } from "@/store/feedbackStore";

/**
 * Checks once per app session — on the first eligible navigation event
 * (dashboard / lesson / progress) — whether to surface the feedback prompt.
 *
 * The server owns eligibility, cooldown, and the 25% randomized display; the
 * client only relays the verdict. `source` is informational (for future
 * analytics / debugging).
 */
export function useFeedbackPrompt(source: string): void {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const hydrated = useAuthStore((s) => s._hydrated);
  const hasChecked = useFeedbackStore((s) => s.hasCheckedThisSession);
  const markChecked = useFeedbackStore((s) => s.markChecked);
  const open = useFeedbackStore((s) => s.open);

  useEffect(() => {
    if (!hydrated || !isAuthenticated || hasChecked) return;

    // Claim the single per-session check before the request resolves so a
    // simultaneous mount on another page can't double-fire.
    markChecked();

    feedbackApi
      .shouldShow()
      .then((res) => {
        if (res.show) {
          open(res.trigger_type);
        }
      })
      .catch(() => {
        // Silent — a failed prompt check should never disrupt the page.
      });
  }, [hydrated, isAuthenticated, hasChecked, markChecked, open, source]);
}
