"use client";

import { useFeedbackPrompt } from "@/hooks/useFeedbackPrompt";

import { FeedbackModal } from "./FeedbackModal";

/**
 * Drop-in for navigation surfaces (dashboard / lesson / progress). Runs the
 * once-per-session eligibility check and renders the shared prompt modal.
 * The modal's open state is global, so only the mounted page's instance shows.
 */
export function FeedbackPrompt({ source }: { source: string }) {
  useFeedbackPrompt(source);
  return <FeedbackModal />;
}
