"use client";

import { useState } from "react";

import { ACCENT_HUE, GlassCard } from "@/components/blog/BlogVisuals";
import { sendContactMessage } from "@/lib/contact-api";

type Field = "full_name" | "email" | "subject" | "message";

type Values = Record<Field, string>;
type Errors = Partial<Record<Field, string>>;

const EMPTY: Values = { full_name: "", email: "", subject: "", message: "" };

// Simple, permissive email shape — the backend (EmailStr) is the real check.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validate(values: Values): Errors {
  const errors: Errors = {};
  if (!values.full_name.trim()) errors.full_name = "Please enter your name.";
  if (!values.email.trim()) errors.email = "Please enter your email.";
  else if (!EMAIL_RE.test(values.email.trim()))
    errors.email = "Please enter a valid email address.";
  if (!values.subject.trim()) errors.subject = "Please add a subject.";
  if (!values.message.trim()) errors.message = "Please write a message.";
  return errors;
}

export function ContactForm() {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{ kind: "success" | "error"; text: string } | null>(
    null,
  );

  const update = (field: Field) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    setValues((v) => ({ ...v, [field]: e.target.value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const found = validate(values);
    if (Object.keys(found).length > 0) {
      setErrors(found);
      return;
    }
    setErrors({});
    setSubmitting(true);
    setToast(null);
    try {
      const res = await sendContactMessage({
        full_name: values.full_name.trim(),
        email: values.email.trim(),
        subject: values.subject.trim(),
        message: values.message.trim(),
      });
      setToast({ kind: "success", text: res.message });
      setValues(EMPTY);
    } catch (err) {
      setToast({
        kind: "error",
        text: err instanceof Error ? err.message : "Something went wrong.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <GlassCard style={{ padding: "32px 30px" }}>
      <style>{STYLES}</style>

      {toast && (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: "fixed",
            top: 88,
            left: "50%",
            transform: "translateX(-50%)",
            zIndex: 50,
            maxWidth: "90vw",
            background:
              toast.kind === "success"
                ? "oklch(28% 0.1 240)"
                : "oklch(45% 0.18 25)",
            color: "white",
            borderRadius: 10,
            padding: "12px 18px",
            fontSize: 14,
            fontWeight: 700,
            boxShadow: "0 14px 38px rgba(20,35,70,0.22)",
          }}
        >
          {toast.text}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <Row>
          <FieldGroup
            label="Full Name"
            htmlFor="contact-name"
            error={errors.full_name}
          >
            <input
              id="contact-name"
              className="contact-input"
              type="text"
              autoComplete="name"
              placeholder="Jane Doe"
              value={values.full_name}
              onChange={update("full_name")}
              aria-invalid={!!errors.full_name}
            />
          </FieldGroup>
          <FieldGroup label="Email" htmlFor="contact-email" error={errors.email}>
            <input
              id="contact-email"
              className="contact-input"
              type="email"
              autoComplete="email"
              placeholder="jane@example.com"
              value={values.email}
              onChange={update("email")}
              aria-invalid={!!errors.email}
            />
          </FieldGroup>
        </Row>

        <FieldGroup label="Subject" htmlFor="contact-subject" error={errors.subject}>
          <input
            id="contact-subject"
            className="contact-input"
            type="text"
            placeholder="How can we help?"
            value={values.subject}
            onChange={update("subject")}
            aria-invalid={!!errors.subject}
          />
        </FieldGroup>

        <FieldGroup label="Message" htmlFor="contact-message" error={errors.message}>
          <textarea
            id="contact-message"
            className="contact-input"
            rows={6}
            placeholder="Tell us a little about what you need…"
            value={values.message}
            onChange={update("message")}
            aria-invalid={!!errors.message}
            style={{ resize: "vertical", minHeight: 130 }}
          />
        </FieldGroup>

        <button
          type="submit"
          className="contact-submit"
          disabled={submitting}
          style={{
            width: "100%",
            marginTop: 8,
            padding: "15px 34px",
            borderRadius: 50,
            border: "none",
            cursor: submitting ? "not-allowed" : "pointer",
            background: `oklch(20% 0.09 ${ACCENT_HUE})`,
            color: "white",
            fontFamily: "inherit",
            fontSize: 16,
            fontWeight: 700,
            opacity: submitting ? 0.7 : 1,
            boxShadow: "0 8px 24px rgba(20,50,120,0.2)",
          }}
        >
          {submitting ? "Sending…" : "Send Message"}
        </button>
      </form>
    </GlassCard>
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return <div className="contact-row">{children}</div>;
}

function FieldGroup({
  label,
  htmlFor,
  error,
  children,
}: {
  label: string;
  htmlFor: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div style={{ marginBottom: 18, flex: 1 }}>
      <label
        htmlFor={htmlFor}
        style={{
          display: "block",
          fontSize: 13,
          fontWeight: 700,
          color: "oklch(28% 0.08 240)",
          marginBottom: 7,
        }}
      >
        {label}
      </label>
      {children}
      {error && (
        <p
          style={{
            margin: "6px 0 0",
            fontSize: 12.5,
            fontWeight: 600,
            color: "oklch(50% 0.18 25)",
          }}
        >
          {error}
        </p>
      )}
    </div>
  );
}

const STYLES = `
  .contact-row { display: flex; gap: 16px; }
  @media (max-width: 560px) { .contact-row { flex-direction: column; gap: 0; } }
  .contact-input {
    width: 100%;
    box-sizing: border-box;
    padding: 12px 14px;
    border-radius: 12px;
    border: 1.5px solid rgba(120,150,210,0.3);
    background: rgba(255,255,255,0.7);
    font-family: inherit;
    font-size: 15px;
    color: oklch(22% 0.05 240);
    outline: none;
    transition: border-color .15s ease, box-shadow .15s ease;
  }
  .contact-input::placeholder { color: oklch(62% 0.03 240); }
  .contact-input:focus {
    border-color: oklch(55% 0.16 240);
    box-shadow: 0 0 0 3px rgba(90,130,210,0.18);
  }
  .contact-input[aria-invalid="true"] { border-color: oklch(60% 0.18 25); }
  .contact-submit { transition: transform .15s ease, box-shadow .15s ease; }
  .contact-submit:not(:disabled):hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(20,50,120,0.28);
  }
`;
