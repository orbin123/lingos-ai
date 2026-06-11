"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";

import {
  forgotPasswordSchema,
  type ForgotPasswordInput,
} from "@/lib/validators/auth";
import { authApi } from "@/lib/auth-api";
import { getApiErrorMessage } from "@/lib/errors";
import { markOtpSentNow } from "@/lib/pending-verification";

import { AuthCard } from "@/components/auth/AuthCard";
import { FormField } from "@/components/auth/FormField";
import { SubmitButton } from "@/components/auth/SubmitButton";
import { ServerErrorBanner } from "@/components/auth/ServerErrorBanner";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const {
    register: field,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordInput>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const request = useMutation({
    mutationFn: (data: ForgotPasswordInput) =>
      authApi.requestPasswordReset(data),
    onSuccess: (_res, variables) => {
      markOtpSentNow();
      router.push(`/reset-password?email=${encodeURIComponent(variables.email)}`);
    },
  });

  const onSubmit = (data: ForgotPasswordInput) => request.mutate(data);
  const serverError = request.error ? getApiErrorMessage(request.error) : null;

  return (
    <AuthCard
      title="Forgot your password?"
      subtitle="Enter your email and we'll send you a 6-digit reset code"
      footer={
        <>
          Remembered it?{" "}
          <Link
            href="/login"
            className="font-semibold hover:underline"
            style={{ color: "oklch(52% 0.18 240)" }}
          >
            Log in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <ServerErrorBanner message={serverError} />

        <FormField
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...field("email")}
        />

        <div className="mt-4">
          <SubmitButton loading={request.isPending} loadingText="Sending code...">
            Send reset code
          </SubmitButton>
        </div>
      </form>
    </AuthCard>
  );
}
