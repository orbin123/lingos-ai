"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";

import { registerSchema, type RegisterInput } from "@/lib/validators/auth";
import { useRegister } from "@/hooks/useRegister";
import { useRedirectIfAuthed } from "@/hooks/useRedirectIfAuthed";
import { getApiErrorMessage } from "@/lib/errors";

import { AuthCard } from "@/components/auth/AuthCard";
import { FormField } from "@/components/auth/FormField";
import { SubmitButton } from "@/components/auth/SubmitButton";
import { ServerErrorBanner } from "@/components/auth/ServerErrorBanner";
import {
  SocialDivider,
  GoogleButton,
} from "@/components/auth/SocialDivider";

export default function RegisterPage() {
  const {
    register: field,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
  });

  const [agreedTerms, setAgreedTerms] = useState(false);
  const [agreedPrivacy, setAgreedPrivacy] = useState(false);

  const registerUser = useRegister();
  useRedirectIfAuthed();

  const onSubmit = (data: RegisterInput) => registerUser.mutate(data);

  const serverError = registerUser.error ? getApiErrorMessage(registerUser.error) : null;

  return (
    <AuthCard
      title="Create your account"
      subtitle="Start your personalized English coaching today"
      footer={
        <>
          Already have an account?{" "}
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
          label="Name"
          type="text"
          autoComplete="name"
          placeholder="Your full name"
          error={errors.name?.message}
          {...field("name")}
        />

        <FormField
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...field("email")}
        />

        <FormField
          label="Password"
          type="password"
          autoComplete="new-password"
          placeholder="Create a password"
          error={errors.password?.message}
          {...field("password")}
        />

        <FormField
          label="Confirm Password"
          type="password"
          autoComplete="new-password"
          placeholder="Confirm your password"
          error={errors.confirmPassword?.message}
          {...field("confirmPassword")}
        />

        <div className="mt-4 flex flex-col gap-2.5">
          <label
            className="flex items-start gap-2 text-[13px] font-medium cursor-pointer select-none"
            style={{ color: "oklch(35% 0.07 240)" }}
          >
            <input
              type="checkbox"
              className="mt-0.5 h-3.5 w-3.5 accent-blue-600 cursor-pointer"
              checked={agreedTerms}
              onChange={(e) => setAgreedTerms(e.target.checked)}
            />
            <span>
              I have read and agree to the{" "}
              <Link
                href="/terms?from=signup"
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold hover:underline"
                style={{ color: "oklch(52% 0.18 240)" }}
              >
                Terms of Service
              </Link>
              .
            </span>
          </label>

          <label
            className="flex items-start gap-2 text-[13px] font-medium cursor-pointer select-none"
            style={{ color: "oklch(35% 0.07 240)" }}
          >
            <input
              type="checkbox"
              className="mt-0.5 h-3.5 w-3.5 accent-blue-600 cursor-pointer"
              checked={agreedPrivacy}
              onChange={(e) => setAgreedPrivacy(e.target.checked)}
            />
            <span>
              I have read and agree to the{" "}
              <Link
                href="/privacy?from=signup"
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold hover:underline"
                style={{ color: "oklch(52% 0.18 240)" }}
              >
                Privacy Policy
              </Link>
              .
            </span>
          </label>
        </div>

        <div className="mt-4">
          <SubmitButton
            loading={registerUser.isPending}
            disabled={!agreedTerms || !agreedPrivacy}
            loadingText="Creating account..."
          >
            Create account
          </SubmitButton>
        </div>

        <SocialDivider />
        <GoogleButton />
      </form>
    </AuthCard>
  );
}