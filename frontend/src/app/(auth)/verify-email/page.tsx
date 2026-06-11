"use client";

import { Suspense, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { verifyEmailSchema, type VerifyEmailInput } from "@/lib/validators/auth";
import { useVerifyEmail } from "@/hooks/useVerifyEmail";
import { authApi } from "@/lib/auth-api";
import { getApiErrorMessage } from "@/lib/errors";
import {
  getPendingEmail,
  getResendCooldownLeft,
  markOtpSentNow,
} from "@/lib/pending-verification";

import { AuthCard } from "@/components/auth/AuthCard";
import { FormField } from "@/components/auth/FormField";
import { SubmitButton } from "@/components/auth/SubmitButton";
import { ServerErrorBanner } from "@/components/auth/ServerErrorBanner";

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailPageInner />
    </Suspense>
  );
}

function VerifyEmailPageInner() {
  const searchParams = useSearchParams();

  // Email source: URL param → sessionStorage → manual entry fallback.
  // Lazy initializers — this component only renders client-side (Suspense
  // CSR bailout), so both sources are available on first render.
  const [email, setEmail] = useState<string>(
    () => searchParams.get("email") || getPendingEmail() || "",
  );
  const [emailLocked] = useState(() => Boolean(email));

  const {
    register: field,
    handleSubmit,
    formState: { errors },
  } = useForm<VerifyEmailInput>({
    resolver: zodResolver(verifyEmailSchema),
  });

  const verify = useVerifyEmail();

  // Resend with countdown, seeded from the signup/login send time so the
  // button starts disabled right after arriving here.
  const [cooldown, setCooldown] = useState(() => getResendCooldownLeft());
  const [resendNotice, setResendNotice] = useState<string | null>(null);
  const [resendError, setResendError] = useState<string | null>(null);
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = window.setInterval(
      () => setCooldown((s) => Math.max(0, s - 1)),
      1000,
    );
    return () => window.clearInterval(timer);
  }, [cooldown]);

  const handleResend = async () => {
    if (!email || cooldown > 0) return;
    setResendNotice(null);
    setResendError(null);
    try {
      const res = await authApi.resendOtp({ email });
      markOtpSentNow();
      setCooldown(60);
      setResendNotice(res.message);
    } catch (err) {
      setResendError(getApiErrorMessage(err));
    }
  };

  const onSubmit = (data: VerifyEmailInput) => {
    if (!email) return;
    verify.mutate({ email, code: data.code });
  };

  const serverError = verify.error ? getApiErrorMessage(verify.error) : resendError;

  return (
    <AuthCard
      title="Check your email"
      subtitle={
        email
          ? `We sent a 6-digit code to ${email}`
          : "Enter your email and the 6-digit code we sent you"
      }
      footer={
        <>
          Wrong account?{" "}
          <Link
            href="/register"
            className="font-semibold hover:underline"
            style={{ color: "oklch(52% 0.18 240)" }}
          >
            Sign up again
          </Link>{" "}
          or{" "}
          <Link
            href="/login"
            className="font-semibold hover:underline"
            style={{ color: "oklch(52% 0.18 240)" }}
          >
            log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <ServerErrorBanner message={serverError} />

        {resendNotice && (
          <div
            role="status"
            className="mb-3 rounded-lg px-3.5 py-2.5 text-[13.5px] font-medium"
            style={{
              background: "oklch(95% 0.04 150)",
              color: "oklch(35% 0.1 150)",
              border: "1px solid oklch(85% 0.07 150)",
            }}
          >
            {resendNotice}
          </div>
        )}

        {!emailLocked && (
          <FormField
            label="Email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            name="email"
          />
        )}

        <FormField
          label="Verification code"
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
          placeholder="123456"
          style={{
            color: "oklch(18% 0.09 245)",
            letterSpacing: "0.45em",
            textAlign: "center",
            fontWeight: 700,
            fontSize: 18,
          }}
          error={errors.code?.message}
          {...field("code")}
        />

        <div className="mt-4">
          <SubmitButton loading={verify.isPending} loadingText="Verifying...">
            Verify email
          </SubmitButton>
        </div>

        <div className="mt-4 text-center text-[13.5px]" style={{ color: "oklch(45% 0.06 240)" }}>
          Didn&apos;t get the code?{" "}
          <button
            type="button"
            onClick={handleResend}
            disabled={cooldown > 0 || !email}
            className="font-semibold hover:underline disabled:no-underline disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ color: "oklch(52% 0.18 240)" }}
          >
            {cooldown > 0 ? `Resend in ${cooldown}s` : "Resend code"}
          </button>
        </div>
      </form>
    </AuthCard>
  );
}
