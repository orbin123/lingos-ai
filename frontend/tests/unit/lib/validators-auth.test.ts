import { describe, expect, it } from "vitest";

import {
  loginSchema,
  registerSchema,
  resetPasswordSchema,
  verifyEmailSchema,
} from "@/lib/validators/auth";

/** Collect all issue messages from a failed parse for easy assertions. */
function messages(result: { success: boolean; error?: { issues: { message: string }[] } }) {
  return result.success ? [] : (result.error?.issues.map((i) => i.message) ?? []);
}

describe("loginSchema", () => {
  it("accepts a valid email + password", () => {
    expect(
      loginSchema.safeParse({ email: "a@b.com", password: "x" }).success,
    ).toBe(true);
  });

  it("rejects a malformed email", () => {
    const r = loginSchema.safeParse({ email: "not-an-email", password: "x" });
    expect(r.success).toBe(false);
    expect(messages(r)).toContain("Please enter a valid email");
  });

  it("rejects an empty password", () => {
    const r = loginSchema.safeParse({ email: "a@b.com", password: "" });
    expect(r.success).toBe(false);
    expect(messages(r)).toContain("Password is required");
  });
});

describe("registerSchema", () => {
  const base = {
    name: "Ada",
    email: "ada@example.com",
    password: "longenough",
    confirmPassword: "longenough",
  };

  it("accepts a complete, matching registration", () => {
    expect(registerSchema.safeParse(base).success).toBe(true);
  });

  it("enforces the 8-char minimum password", () => {
    const r = registerSchema.safeParse({ ...base, password: "short", confirmPassword: "short" });
    expect(r.success).toBe(false);
    expect(messages(r)).toContain("Password must be at least 8 characters");
  });

  it("flags mismatched passwords on the confirmPassword path", () => {
    const r = registerSchema.safeParse({ ...base, confirmPassword: "different1" });
    expect(r.success).toBe(false);
    expect(messages(r)).toContain("Passwords do not match");
    if (!r.success) {
      expect(r.error.issues.some((i) => i.path.includes("confirmPassword"))).toBe(true);
    }
  });
});

describe("verifyEmailSchema", () => {
  it("accepts exactly 6 digits", () => {
    expect(verifyEmailSchema.safeParse({ code: "123456" }).success).toBe(true);
  });

  it("rejects non-6-digit codes", () => {
    expect(verifyEmailSchema.safeParse({ code: "12ab56" }).success).toBe(false);
    expect(verifyEmailSchema.safeParse({ code: "12345" }).success).toBe(false);
  });
});

describe("resetPasswordSchema", () => {
  it("requires the code, an 8-char password, and a match", () => {
    expect(
      resetPasswordSchema.safeParse({
        code: "000000",
        newPassword: "longenough",
        confirmPassword: "longenough",
      }).success,
    ).toBe(true);

    const mismatch = resetPasswordSchema.safeParse({
      code: "000000",
      newPassword: "longenough",
      confirmPassword: "nope",
    });
    expect(mismatch.success).toBe(false);
    expect(messages(mismatch)).toContain("Passwords do not match");
  });
});
