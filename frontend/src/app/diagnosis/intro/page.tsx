"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { LandingNavbar } from "@/components/layout/LandingNavbar";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { authApi } from "@/lib/auth-api";

/* ──────────────────────────────────────────────────────────────────────────
 *  LingosAI — Diagnosis intro
 *  Shown right after email/OTP verification, before the placement test so the
 *  learner gets an acknowledgement and knows what's coming next.
 * ────────────────────────────────────────────────────────────────────────── */

/* ── Inline icons (kept local, matching diagnosis/page.tsx) ─────────────── */
function CheckIcon({ className = "" }: { className?: string }) {
  return (
    <svg className={className} width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden>
      <path d="M3 7.5L6 10.5L11 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function ArrowRightIcon({ className = "" }: { className?: string }) {
  return (
    <svg className={className} width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
      <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-blue-100 bg-white px-3 py-1 text-[12.5px] font-semibold text-blue-800 shadow-sm">
      <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
      {children}
    </div>
  );
}

/* ── What to expect rows ──────────────────────────────────────────────── */
const STEPS = [
  {
    title: "A few quick questions",
    body: "Your goals, level and how much time you can give each day.",
  },
  {
    title: "Grammar & writing",
    body: "Fill a few blanks and write a couple of sentences about your day.",
  },
  {
    title: "Read aloud",
    body: "Read a short passage so we can check your pronunciation.",
  },
] as const;

function StepRow({ index, title, body }: { index: number; title: string; body: string }) {
  return (
    <li className="flex items-start gap-3 rounded-2xl border border-slate-100 bg-white px-5 py-4 shadow-[0_2px_10px_rgba(15,23,42,0.04)]">
      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-600 text-[12.5px] font-bold text-white">
        {index}
      </div>
      <div className="flex-1">
        <div className="text-[14.5px] font-semibold text-[#0a1f44]">{title}</div>
        <div className="mt-0.5 text-[13px] text-slate-500">{body}</div>
      </div>
    </li>
  );
}

/* ── Page ─────────────────────────────────────────────────────────────── */
export default function DiagnosisIntroPage() {
  const router = useRouter();
  const { isReady, isSuperUser } = useRequireAuth();

  // If a verified learner who already finished the diagnosis lands here, send
  // them straight to the dashboard instead of re-onboarding (mirrors /diagnosis).
  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });
  useEffect(() => {
    if (me?.diagnosis_completed && !isSuperUser) router.replace("/dashboard");
  }, [me, isSuperUser, router]);

  if (!isReady) return null;

  return (
    <main
      className="relative min-h-screen w-full bg-gradient-to-b from-[#dbeafe] to-[#eff6ff]"
      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" />
      <div aria-hidden className="pointer-events-none absolute inset-0" style={{ backgroundImage: "radial-gradient(circle, rgba(37,99,235,0.10) 1px, transparent 1px)", backgroundSize: "22px 22px" }} />

      <LandingNavbar variant="minimal" />

      <section className="relative z-10 mx-auto w-full max-w-[640px] px-4 pb-20 pt-[68px] sm:px-6">
        <div className="animate-[fadeIn_0.4s_ease] rounded-3xl border border-white/90 bg-white/90 px-5 py-8 shadow-[0_8px_32px_rgba(15,23,42,0.06)] backdrop-blur-xl sm:px-10 sm:py-10" style={{ animationFillMode: "both" }}>
          {/* Status badges — stacked so the two pills don't visually fuse on one row */}
          <div className="mb-5 flex flex-col items-start gap-2.5">
            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3.5 py-1.5 text-[13px] font-semibold text-emerald-700">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-100">
                <CheckIcon className="text-emerald-600" />
              </span>
              Email verified
            </div>
            <Eyebrow>Next: a quick placement check</Eyebrow>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-[#0a1f44] sm:text-[28px]">
            You&apos;re in 🎉 Let&apos;s find your starting point
          </h1>
          <p className="mt-3 text-[15px] leading-relaxed text-slate-600">
            Your account is ready. Before your first lesson we&apos;ll run a short
            placement test — it takes about <span className="font-semibold text-[#0a1f44]">3 minutes</span>.
            Think of it as a quick get-to-know-you: it tells LingosAI your level
            today so we can personalize every lesson and show you the results
            you&apos;ll be working toward on your journey.
          </p>

          <ol className="mt-6 space-y-3">
            {STEPS.map((s, i) => (
              <StepRow key={s.title} index={i + 1} title={s.title} body={s.body} />
            ))}
          </ol>

          <div className="mt-8 flex justify-end border-t border-slate-100 pt-6">
            <button
              type="button"
              onClick={() => router.push("/diagnosis")}
              className="inline-flex items-center gap-2 rounded-full bg-[#0a0f1f] px-6 py-3 text-[14.5px] font-bold text-white shadow-[0_4px_18px_rgba(10,15,31,0.25)] transition-all hover:scale-[1.02] active:scale-[0.99]"
            >
              Start my diagnosis <ArrowRightIcon />
            </button>
          </div>
        </div>
        <p className="mt-5 text-center text-[12.5px] text-slate-500">
          Your answers are private and used only to personalize your coaching plan.
        </p>
      </section>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </main>
  );
}
