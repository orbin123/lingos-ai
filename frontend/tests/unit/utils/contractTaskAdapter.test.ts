import { describe, expect, it } from "vitest";

import { resolveListenRetellModelAnswer } from "@/components/chat/contractTaskAdapter";
import type { AnyTaskPayload } from "@/components/chat/runtimeMapping";

// Migrated from tests/listen-retell-reference.test.mjs, which RE-IMPLEMENTED
// the resolver ("Mirrors … Keep in sync") — a guaranteed drift bug. We now
// import the real function, so the adapter's fallback order is verified, not
// duplicated.
const payload = (fields: Record<string, unknown>): AnyTaskPayload =>
  ({ widget: "listen_and_respond", ...fields }) as AnyTaskPayload;

describe("resolveListenRetellModelAnswer", () => {
  it("prefers passage_to_retell over everything else", () => {
    expect(
      resolveListenRetellModelAnswer(
        payload({
          passage_to_retell: "Park with fountain.",
          audio_script: "Audio monologue.",
          sample_response: "A sample.",
        }),
      ),
    ).toBe("Park with fountain.");
  });

  it("falls back to the first sample_responses entry", () => {
    expect(
      resolveListenRetellModelAnswer(
        payload({
          sample_responses: ["First sample.", "Second sample."],
          audio_script: "Audio.",
        }),
      ),
    ).toBe("First sample.");
  });

  it("accepts the sample_response singular alias", () => {
    expect(
      resolveListenRetellModelAnswer(
        payload({ sample_response: "Model from alias.", audio_script: "Audio." }),
      ),
    ).toBe("Model from alias.");
  });

  it("uses text_to_read_aloud when distinct from audio_script", () => {
    expect(
      resolveListenRetellModelAnswer(
        payload({
          text_to_read_aloud: "Summary text.",
          audio_script: "Different audio script.",
        }),
      ),
    ).toBe("Summary text.");
  });

  it("ignores text_to_read_aloud that merely echoes audio_script", () => {
    expect(
      resolveListenRetellModelAnswer(
        payload({
          text_to_read_aloud: "Same script.",
          audio_script: "Same script.",
        }),
      ),
    ).toBe("");
  });

  it("returns empty when only audio_script is present", () => {
    expect(
      resolveListenRetellModelAnswer(payload({ audio_script: "Only audio." })),
    ).toBe("");
  });
});
