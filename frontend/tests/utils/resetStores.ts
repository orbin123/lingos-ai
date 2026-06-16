import { useAuthStore } from "@/store/authStore";
import { useSessionStore } from "@/store/sessionStore";
import { useTaskStore } from "@/store/taskStore";
import { useDiagnosisStore } from "@/store/diagnosisStore";
import { useFeedbackStore } from "@/store/feedbackStore";

// Capture pristine state ONCE at module import — before any test mutates a
// store — so we can restore it between tests. Snapshotting inside afterEach
// would capture already-dirtied state.
const initial = {
  auth: useAuthStore.getState(),
  session: useSessionStore.getState(),
  task: useTaskStore.getState(),
  diagnosis: useDiagnosisStore.getState(),
  feedback: useFeedbackStore.getState(),
};

/**
 * Reset every Zustand store to its initial state. The `true` second arg REPLACES
 * (not merges) so any keys a test added are dropped. Note: this does NOT clear
 * localStorage — vitest.setup.ts does that separately, because authStore's token
 * also lives in localStorage and is read by the axios interceptor on every call.
 */
export function resetAllStores(): void {
  useAuthStore.setState(initial.auth, true);
  useSessionStore.setState(initial.session, true);
  useTaskStore.setState(initial.task, true);
  useDiagnosisStore.setState(initial.diagnosis, true);
  useFeedbackStore.setState(initial.feedback, true);
}
