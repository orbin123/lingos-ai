/**
 * Widget contract for the new sessions flow.
 *
 * The session shell hands each widget:
 *   - `taskContent`  the JSONB blob from `activity_attempts.task_content`
 *   - `disabled`     true after submission (so the widget renders read-only)
 *   - `onSubmit`     callback the widget invokes with the user's response
 *
 * Phase 3 ships stub task content (`{phase: "stub", ...}`); widgets render
 * gracefully against the stub. Phase 4 replaces the stub with real
 * Task-Generator output and the widgets receive their archetype-specific
 * payload shapes.
 */

export interface SessionWidgetProps {
  taskContent: Record<string, unknown>;
  disabled: boolean;
  onSubmit: (response: Record<string, unknown>) => void;
}

export type SessionWidgetComponent = React.FC<SessionWidgetProps>;


// ── Helpers ────────────────────────────────────────────────────────

export function getStr(content: Record<string, unknown>, key: string): string {
  const v = content[key];
  return typeof v === "string" ? v : "";
}

export function isStubContent(content: Record<string, unknown>): boolean {
  return content.phase === "stub";
}
