import assert from "node:assert/strict";
import { describe, it } from "node:test";

/**
 * Mirrors resolveListenRetellModelAnswer in contractTaskAdapter.ts.
 * Keep in sync when changing adapter fallbacks.
 */
function resolveListenRetellModelAnswer(payload) {
  const audioScript = String(payload.audio_script ?? "").trim();
  const samplesRaw = payload.sample_responses ?? payload.sample_answers;
  const samples = Array.isArray(samplesRaw)
    ? samplesRaw.map((s) => String(s).trim()).filter(Boolean)
    : [];
  const fallbackSample = String(payload.sample_response ?? "").trim();
  const allSamples = samples.length > 0 ? samples : fallbackSample ? [fallbackSample] : [];
  const passage = String(payload.passage_to_retell ?? "").trim();
  const readAloud = String(payload.text_to_read_aloud ?? "").trim();
  const distinctReadAloud = readAloud && readAloud !== audioScript ? readAloud : "";
  return passage || allSamples[0] || distinctReadAloud || "";
}

describe("resolveListenRetellModelAnswer", () => {
  it("prefers passage_to_retell", () => {
    assert.equal(
      resolveListenRetellModelAnswer({
        passage_to_retell: "Park with fountain.",
        audio_script: "Audio monologue.",
      }),
      "Park with fountain.",
    );
  });

  it("falls back to sample_response alias", () => {
    assert.equal(
      resolveListenRetellModelAnswer({
        sample_response: "Model from alias.",
        audio_script: "Audio.",
      }),
      "Model from alias.",
    );
  });

  it("uses text_to_read_aloud when distinct from audio_script", () => {
    assert.equal(
      resolveListenRetellModelAnswer({
        text_to_read_aloud: "Summary text.",
        audio_script: "Different audio script.",
      }),
      "Summary text.",
    );
  });

  it("returns empty when only audio_script is present", () => {
    assert.equal(
      resolveListenRetellModelAnswer({ audio_script: "Only audio." }),
      "",
    );
  });
});
