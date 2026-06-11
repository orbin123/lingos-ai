"use client";

import { Suspense, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import {
  resetPasswordSchema,
  type ResetPasswordInput,
} from "@/lib/validators/auth";
import { authApi } from "@/lib/auth-api";
import { getApiErrorMessage } from "@/lib/errors";

import { AuthCard } from "@/components/auth/AuthCard";
import { FormField } from "@/components/auth/FormField";
import { SubmitButton } from "@/components/auth/SubmitButton";
import { ServerErrorBanner } from "@/components/auth/ServerErrorBanner";

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={null}>
      <ResetPasswordPageInner />
    </Suspense>
  );
}

function ResetPasswordPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Lazy initializers — this component only renders client-side (Suspense
  // CSR bailout), so the param is available on first render.
  const [email, setEmail] = useState(() => searchParams.get("email") || "");
  const [emailLocked] = useState(() => Boolean(email));

  const {
    register: field,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordInput>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const reset = useMutation({
    mutationFn: (data: ResetPasswordInput) =>
      authApi.confirmPasswordReset({
        email,
        code: data.code,
        new_password: data.newPassword,
      }),
    onSuccess: () => {
      router.push("/login?reset=success");
    },
  });

  const onSubmit = (data: ResetPasswordInput) => {
    if (!email) return;
    reset.mutate(data);
  };

  const serverError = reset.error ? getApiErrorMessage(reset.error) : null;

  return (
    <AuthCard
      title="Reset your password"
      subtitle={
        email
          ? `Enter the code we sent to ${email} and choose a new password`
          : "Enter your email, the reset code, and a new password"
      }
      footer={
        <>
          Need a code?{" "}
          <Link
            href="/forgot-password"
            className="font-semibold hover:underline"
            style={{ color: "oklch(52% 0.18 240)" }}
          >
            Request one
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <ServerErrorBanner message={serverError} />

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
          label="Reset code"
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

        <FormField
          label="New password"
          type="password"
          autoComplete="new-password"
          placeholder="Create a new password"
          error={errors.newPassword?.message}
          {...field("newPassword")}
        />

        <FormField
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          placeholder="Confirm your new password"
          error={errors.confirmPassword?.message}
          {...field("confirmPassword")}
        />

        <div className="mt-4">
          <SubmitButton loading={reset.isPending} loadingText="Resetting...">
            Reset password
          </SubmitButton>
        </div>
      </form>
    </AuthCard>
  );
}
