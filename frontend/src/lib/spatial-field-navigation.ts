import type { KeyboardEvent } from "react";

/** Marks the task widget (or form) that groups navigable fields together. */
export const SPATIAL_NAV_ROOT_ATTR = "data-spatial-nav-root";

const FIELD_SELECTOR =
  "input.tw-blank-input:not(:disabled), textarea.tw-write-area:not(:disabled)";

type Direction = "down" | "up";

function fieldCenter(el: HTMLElement): { x: number; y: number } {
  const rect = el.getBoundingClientRect();
  return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
}

function listNavigableFields(root: ParentNode, current: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FIELD_SELECTOR)).filter(
    (el) => el !== current && !el.hasAttribute("disabled") && el.offsetParent !== null,
  );
}

function findBySpatialProximity(
  current: HTMLElement,
  direction: Direction,
  root: ParentNode,
): HTMLElement | null {
  const fields = listNavigableFields(root, current);
  if (fields.length === 0) return null;

  const cur = fieldCenter(current);
  const minVerticalGap = 6;

  let best: HTMLElement | null = null;
  let bestScore = Infinity;

  for (const field of fields) {
    const pos = fieldCenter(field);
    if (direction === "down") {
      if (pos.y < cur.y + minVerticalGap) continue;
    } else if (pos.y > cur.y - minVerticalGap) {
      continue;
    }
    const dy = Math.abs(pos.y - cur.y);
    const dx = Math.abs(pos.x - cur.x);
    const score = dy * 3 + dx;
    if (score < bestScore) {
      bestScore = score;
      best = field;
    }
  }

  return best;
}

function findByFieldIndex(
  current: HTMLElement,
  direction: Direction,
  root: ParentNode,
): HTMLElement | null {
  const rawIndex = current.dataset.spatialFieldIndex;
  if (rawIndex === undefined) return null;
  const currentIndex = Number(rawIndex);
  if (!Number.isFinite(currentIndex)) return null;

  const targetIndex = direction === "down" ? currentIndex + 1 : currentIndex - 1;
  return (
    listNavigableFields(root, current).find(
      (el) => Number(el.dataset.spatialFieldIndex) === targetIndex,
    ) ?? null
  );
}

function findAdjacentField(
  current: HTMLElement,
  direction: Direction,
  root: ParentNode,
): HTMLElement | null {
  return (
    findBySpatialProximity(current, direction, root) ??
    findByFieldIndex(current, direction, root)
  );
}

function shouldNavigateFromTextarea(
  element: HTMLTextAreaElement,
  key: "ArrowDown" | "ArrowUp",
): boolean {
  const { selectionStart, selectionEnd } = element;
  if (selectionStart === null || selectionEnd === null || selectionStart !== selectionEnd) {
    return false;
  }
  const value = element.value;
  if (key === "ArrowDown") {
    return !value.slice(selectionStart).includes("\n");
  }
  return !value.slice(0, selectionStart).includes("\n");
}

export function handleSpatialFieldKeyDown(
  event: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>,
): void {
  const key = event.key;
  if (key !== "ArrowDown" && key !== "ArrowUp") return;

  const current = event.currentTarget;
  if (current instanceof HTMLTextAreaElement && !shouldNavigateFromTextarea(current, key)) {
    return;
  }

  const root = current.closest(`[${SPATIAL_NAV_ROOT_ATTR}]`);
  if (!root) return;

  const direction: Direction = key === "ArrowDown" ? "down" : "up";
  const next = findAdjacentField(current, direction, root);
  if (!next) return;

  event.preventDefault();
  next.focus();
  if (next instanceof HTMLInputElement || next instanceof HTMLTextAreaElement) {
    const end = next.value.length;
    next.setSelectionRange(end, end);
  }
}

export function spatialFieldProps(fieldIndex: number): {
  "data-spatial-field-index": number;
  onKeyDown: typeof handleSpatialFieldKeyDown;
  "aria-keyshortcuts": string;
} {
  return {
    "data-spatial-field-index": fieldIndex,
    onKeyDown: handleSpatialFieldKeyDown,
    "aria-keyshortcuts": "ArrowDown ArrowUp",
  };
}
