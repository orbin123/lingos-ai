export function isAuthoringChatEnabled(
  value = process.env.NEXT_PUBLIC_AUTHORING_CHAT,
): boolean {
  return value === "true";
}

export function authoringStartPath(input?: { week?: number; day?: number }): string {
  const params = new URLSearchParams();
  if (input?.week) params.set("week", String(input.week));
  if (input?.day) params.set("day", String(input.day));
  const qs = params.toString();
  return `/api/dev/learning/sessions/start${qs ? `?${qs}` : ""}`;
}

export function learningRestartPath(sessionId: string, authoring: boolean): string {
  const encoded = encodeURIComponent(sessionId);
  return authoring
    ? `/api/dev/learning/sessions/${encoded}/restart`
    : `/api/learning/sessions/${encoded}/restart`;
}

export function learningWebSocketUrl(
  apiBase: string,
  sessionId: string,
  options: { authoring: boolean; token?: string | null },
): string {
  const wsBase = apiBase.replace(/^http/, "ws");
  if (options.authoring) {
    return `${wsBase}/dev/ws/learning/${sessionId}`;
  }
  return `${wsBase}/ws/learning/${sessionId}?token=${encodeURIComponent(
    options.token || "",
  )}`;
}
