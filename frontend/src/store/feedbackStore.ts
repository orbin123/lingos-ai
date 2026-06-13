import { create } from "zustand";

/**
 * Client state for the in-app feedback prompt.
 *
 * `hasCheckedThisSession` guards against re-asking the server on every
 * navigation within a single app load — the first eligible navigation event
 * checks once, and the server (which owns eligibility, cooldown, and the 25%
 * randomization) decides whether the modal opens. A full page reload starts a
 * new session and allows another check.
 */
interface FeedbackState {
  isOpen: boolean;
  triggerType: string | null;
  hasCheckedThisSession: boolean;

  markChecked: () => void;
  open: (triggerType: string | null) => void;
  close: () => void;
  reset: () => void;
}

export const useFeedbackStore = create<FeedbackState>((set) => ({
  isOpen: false,
  triggerType: null,
  hasCheckedThisSession: false,

  markChecked: () => set({ hasCheckedThisSession: true }),
  open: (triggerType) => set({ isOpen: true, triggerType }),
  close: () => set({ isOpen: false }),
  reset: () => set({ isOpen: false, triggerType: null, hasCheckedThisSession: false }),
}));
