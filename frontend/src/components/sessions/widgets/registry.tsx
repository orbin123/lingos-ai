/**
 * Widget registry for the sessions flow.
 *
 * Maps the backend's `ui_widget` string (from `task_archetypes.ui_widget`,
 * see backend/app/scoring/archetypes.py) to a React component. The session
 * shell calls `getSessionWidget(ui_widget)` and renders the result with
 * `(taskContent, disabled, onSubmit)`.
 *
 * Every archetype currently routes to `GenericResponseWidget`. Replace
 * individual entries with archetype-specific components as real task
 * content arrives.
 */

import { GenericResponseWidget } from "./GenericResponseWidget";
import type { SessionWidgetComponent } from "./types";


// Canonical mapping of archetype.ui_widget strings → component.
// Every value the backend can produce must appear here so the shell never
// renders a fallback unexpectedly.
const REGISTRY: Record<string, SessionWidgetComponent> = {
  // Reading
  MCQList: GenericResponseWidget,
  TrueFalseNotGiven: GenericResponseWidget,
  ErrorSpotting: GenericResponseWidget,
  FillInBlanks: GenericResponseWidget,
  OpenTextList: GenericResponseWidget,

  // Writing
  SentenceTransform: GenericResponseWidget,
  ErrorCorrection: GenericResponseWidget,
  StructuredEssay: GenericResponseWidget,
  PassageSummary: GenericResponseWidget,
  TimedWriting: GenericResponseWidget,

  // Speaking
  SpeakAndRecord: GenericResponseWidget,
  Storyboard: GenericResponseWidget,

  // Listening (composite "outer+inner" strings — backend ships them as one)
  "ListenAndAnswer+MCQList": GenericResponseWidget,
  "ListenAndAnswer+FillInBlanks": GenericResponseWidget,
  "ListenAndAnswer+OpenTextList": GenericResponseWidget,
  "ListenAndAnswer+SpeakAndRecord": GenericResponseWidget,
};


/**
 * Return the widget component for a backend ui_widget string. Falls back
 * to the generic widget for unknown values so the shell never crashes.
 */
export function getSessionWidget(uiWidget: string): SessionWidgetComponent {
  return REGISTRY[uiWidget] ?? GenericResponseWidget;
}


/** All registered ui_widget keys. Useful for tests and discovery. */
export function knownWidgetKeys(): readonly string[] {
  return Object.keys(REGISTRY);
}
