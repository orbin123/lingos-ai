/**
 * Single source of truth for sub-skill display labels on the frontend.
 *
 * The backend ships `display_label` in API responses (see Phase 5 of the
 * restructure). When a component receives an API payload, prefer the
 * server-provided label and use `SKILL_LABEL_FALLBACK` only when the API
 * value is missing (e.g. older endpoints not yet updated).
 *
 * Keys are the LEGACY internal identifiers used by the backend:
 *   grammar / vocabulary / pronunciation / fluency /
 *   expression / comprehension / tone
 *
 * The friendlier wording (Thought Organization / Listening / Tone & Social)
 * lives in the values. Do not key data by these values — they are display
 * strings only.
 */
export const SKILL_LABEL_FALLBACK: Record<string, string> = {
  grammar: "Grammar",
  vocabulary: "Vocabulary",
  pronunciation: "Pronunciation",
  fluency: "Fluency",
  expression: "Thought Organization",
  comprehension: "Listening",
  tone: "Tone & Social",
};

/**
 * Resolve a label for a skill identifier.
 *
 * @param skillName  The backend identifier (e.g. "expression").
 * @param overrides  Optional API-provided `{ skill_name: display_label }`
 *                   map. Takes priority over the static fallback.
 */
export function getSkillLabel(
  skillName: string,
  overrides?: Record<string, string>,
): string {
  return (
    overrides?.[skillName] ??
    SKILL_LABEL_FALLBACK[skillName] ??
    skillName
  );
}

/**
 * The seven legacy sub-skill identifiers in their canonical display order.
 * Components that render every skill (e.g. the dashboard preview) iterate
 * over this list rather than `Object.keys(SKILL_LABEL_FALLBACK)` to keep
 * the order stable across refactors.
 */
export const SKILL_ORDER: ReadonlyArray<string> = [
  "grammar",
  "vocabulary",
  "pronunciation",
  "fluency",
  "expression",
  "comprehension",
  "tone",
];

/**
 * Alias resolver. Different parts of the system have shipped sub-skill
 * identifiers under three different vocabularies over time:
 *
 *   canonical (legacy DB):  expression / comprehension / tone
 *   doc / spec wording:     thought_org / listening / tone_social
 *   long-form legacy enum:  thought_organization / listening / tone
 *
 * `normalizeSkillKey` collapses all of them down to the canonical legacy
 * identifier so callers can keep ONE map for labels, colors, scores, etc.
 * Pass any string in; get the legacy identifier out (unknown inputs are
 * returned unchanged so the caller can decide).
 */
const _ALIASES: Record<string, string> = {
  // doc / spec wording
  thought_org: "expression",
  listening: "comprehension",
  tone_social: "tone",
  // long-form legacy enum (used by app/tasks/schemas/base.py SubSkill)
  thought_organization: "expression",
};

export function normalizeSkillKey(input: string): string {
  return _ALIASES[input] ?? input;
}

/**
 * Default per-skill score dict — every legacy key initialised to 0.0.
 * Components use this as the fallback when API data is missing so the
 * spider chart / progress bars still render with the right axis set.
 */
export function emptySkillScores(): Record<string, number> {
  return Object.fromEntries(SKILL_ORDER.map((k) => [k, 0]));
}
