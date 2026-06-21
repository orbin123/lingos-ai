"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { useDiagnosisStore } from "@/store/diagnosisStore";
import { SKILL_LABEL_FALLBACK } from "@/lib/skill-labels";
import { LandingNavbar } from "@/components/layout/LandingNavbar";

/* ----------------------------------------------------------------------------
 * Skill scores are shown raw on their native 0–4 scale — no rescaling.
 * Bars fill proportionally to SCORE_MAX; colour thresholds are on the 0–4 scale.
 * -------------------------------------------------------------------------- */
const SCORE_MAX = 4;

const stateOf = (s: number) => (s < 2 ? "red" : s < 3 ? "amber" : "green");
const labelOf = (s: number) =>
  s < 2 ? "Critical Focus" : s < 3 ? "Developing" : "Strong Foundation";

const titleCase = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
const skillLabel = (name: string) => SKILL_LABEL_FALLBACK[name] ?? titleCase(name);

/* ------------------------------ Icons -------------------------------------- */
const I = {
  warn: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M8 1.5L15 14H1L8 1.5z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M8 6.5v3M8 11.5v.01" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  ),
  star: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 1.5l1.9 4.1 4.5.5-3.3 3 .9 4.4L8 11.4l-4 2.1.9-4.4-3.3-3 4.5-.5L8 1.5z" />
    </svg>
  ),
  target: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="8" cy="8" r="1" fill="currentColor" />
    </svg>
  ),
  level: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <path d="M2 13h2v-4H2v4zm5 0h2V5H7v8zm5 0h2V8h-2v5z" fill="currentColor" />
    </svg>
  ),
  arrow: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  mic: (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
      <rect x="6" y="2" width="4" height="8" rx="2" stroke="currentColor" strokeWidth="1.5" />
      <path d="M3.5 8a4.5 4.5 0 0 0 9 0M8 12.5v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  ),
};

function Dial({ score, label, desc }: { score: number; label: string; desc: string }) {
  const r = 32;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;
  const color = score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444";

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "10px" }}>
      <div style={{ position: "relative", width: "70px", height: "70px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <svg width="70" height="70" style={{ transform: "rotate(-90deg)", position: "absolute", inset: 0 }}>
          <circle cx="35" cy="35" r={r} fill="transparent" stroke="rgba(255,255,255,0.15)" strokeWidth="5" />
          <circle cx="35" cy="35" r={r} fill="transparent" stroke={color} strokeWidth="5" strokeDasharray={c} strokeDashoffset={offset} strokeLinecap="round" style={{ transition: "stroke-dashoffset 1s ease-out" }} />
        </svg>
        <span style={{ fontSize: "16px", fontWeight: 800, position: "relative", zIndex: 1 }}>{score}<span style={{ fontSize: "11px", opacity: 0.7 }}>%</span></span>
      </div>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: "12px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", opacity: 0.9 }}>{label}</div>
        <div style={{ fontSize: "11px", opacity: 0.6, marginTop: "3px" }}>{desc}</div>
      </div>
    </div>
  );
}

export default function DiagnosisResultPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { result, clear } = useDiagnosisStore();
  // Set when the user intentionally leaves for the dashboard. Without this,
  // clearing the store (below) nulls `result`, which would re-trigger the
  // guard effect and bounce the user back to the diagnosis form.
  const leavingRef = React.useRef(false);

  useEffect(() => {
    if (!result && !leavingRef.current) router.replace("/diagnosis");
  }, [result, router]);

  if (!result) return null;

  const { skill_scores, feedback, read_aloud_analysis, goal } = result;
  const skills = Object.entries(skill_scores);
  const ra = read_aloud_analysis ?? null;

  const continueToDashboard = () => {
    // Mark that we're navigating away so the guard effect doesn't redirect
    // back to /diagnosis when clear() nulls the result below.
    leavingRef.current = true;
    // Invalidate /me and the freshly-seeded skill scores only after the user
    // has seen the result, so the dashboard renders them on arrival.
    queryClient.invalidateQueries({ queryKey: ["me"] });
    queryClient.invalidateQueries({ queryKey: ["progress", "scores"] });
    clear();
    // Always land on the dashboard: verified users see the NoEnrollmentView
    // with plan cards there, letting them explore the UI before choosing.
    router.push("/dashboard");
  };

  return (
    <main
      className="relative min-h-screen w-full bg-gradient-to-b from-[#dbeafe] to-[#eff6ff]"
      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Source+Serif+4:ital@1&display=swap"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundImage: "radial-gradient(circle, rgba(37,99,235,0.10) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
        }}
      />

      <LandingNavbar variant="minimal" />

      <section className="relative z-10 mx-auto w-full max-w-[1120px] px-4 pb-20 pt-[68px] sm:px-6">
        <div className="rounded-3xl border border-white/90 bg-white/90 shadow-[0_8px_32px_rgba(15,23,42,0.06)] backdrop-blur-xl overflow-hidden text-[#0a1f44]">
          {/* ZONE 1 — HERO */}
          <section className="hero">
            <div className="hero-left fade-in d1">
              <div className="eyebrow">
                <span className="eyebrow-dot"></span>Your diagnosis is ready
              </div>
              <h1 className="h1">
                Your English<br />
                <span className="grad">Snapshot</span>
              </h1>
              <p className="hero-summary">{feedback.summary}</p>
              <div className="hero-meta">
                <span>
                  <b>4</b> exercises analysed
                </span>
                <span>·</span>
                <span>
                  <b>7</b> skills evaluated
                </span>
                <span>·</span>
                <span>
                  Personalized for <b>{titleCase(goal)}</b>
                </span>
              </div>
            </div>
          </section>

          {/* ZONE 2 — SKILL PROFILE */}
          <section className="zone2 fade-in d2">
            <div className="flex flex-col justify-center items-center w-full">
              <div className="stat-grid">
                <div className="stat red">
                  <div>
                    <div className="stat-head">
                      <span className="stat-ico">{I.warn}</span> Biggest weakness
                    </div>
                  </div>
                  <div>
                    <div className="stat-value">{skillLabel(feedback.biggest_weakness.skill_name)}</div>
                    <div className="stat-sub">{feedback.biggest_weakness.description}</div>
                  </div>
                </div>
                <div className="stat green">
                  <div>
                    <div className="stat-head">
                      <span className="stat-ico">{I.star}</span> Strongest skill
                    </div>
                  </div>
                  <div>
                    <div className="stat-value">{skillLabel(feedback.strongest_skill.skill_name)}</div>
                    <div className="stat-sub">{feedback.strongest_skill.description}</div>
                  </div>
                </div>
                <div className="stat blue">
                  <div>
                    <div className="stat-head">
                      <span className="stat-ico">{I.target}</span> First focus
                    </div>
                  </div>
                  <div>
                    <div className="stat-value">{feedback.first_focus.title}</div>
                    <div className="stat-sub">{feedback.first_focus.description}</div>
                  </div>
                </div>
                <div className="stat amber">
                  <div>
                    <div className="stat-head">
                      <span className="stat-ico">{I.level}</span> Level
                    </div>
                  </div>
                  <div>
                    <div className="stat-value">{feedback.estimated_level_label}</div>
                    <div className="stat-sub">{feedback.level_description}</div>
                  </div>
                </div>
              </div>
            </div>
            <div>
              <div className="zone-title">Your skill profile</div>
              <div className="zone-sub">Where you stand across the seven core communication skills.</div>
              <div className="skill-list">
                {skills.map(([name, score]) => {
                  const s = stateOf(score);
                  const lbl = labelOf(score);
                  return (
                    <div className="skill-row" key={name}>
                      <span className="skill-name">{skillLabel(name)}</span>
                      <div className="skill-bar">
                        <div
                          className={`skill-bar-fill bar-${s}`}
                          style={{ width: `${Math.min(100, (score / SCORE_MAX) * 100)}%` }}
                        />
                      </div>
                      <span className={`skill-tag tag-${s}`}>{lbl}</span>
                    </div>
                  );
                })}
              </div>
              <div className="legend">
                <span className="legend-item">
                  <span className="legend-dot" style={{ background: "#ef4444" }}></span>Critical focus
                </span>
                <span className="legend-item">
                  <span className="legend-dot" style={{ background: "#f59e0b" }}></span>Developing
                </span>
                <span className="legend-item">
                  <span className="legend-dot" style={{ background: "#22c55e" }}></span>Strong foundation
                </span>
              </div>
            </div>
          </section>

          {/* ZONE 3 — SPEAKING */}
          {ra && (
            <section className="zone3 fade-in d3" style={{ gridTemplateColumns: "1fr", maxWidth: "100%", margin: "0 auto" }}>
              <div>
                <div className="zone-title">Azure Speech Analysis</div>
                <div className="zone-sub">Detailed read-aloud evaluation powered by Azure AI.</div>
                <div className="speaking-card" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
                  <div className="speak-head">
                    <span className="speak-title">
                      {I.mic} &nbsp;Read-Aloud Scorecard
                    </span>
                    <span className="speak-pill">Azure AI</span>
                  </div>

                  <div style={{ display: "flex", justifyItems: "center", justifyContent: "space-around", flexWrap: "wrap", gap: "16px", padding: "10px 0" }}>
                    <Dial score={Math.round(ra.overall)} label="Overall" desc="Read-aloud score" />
                    <Dial score={Math.round(ra.accuracy)} label="Accuracy" desc="Phoneme precision" />
                    <Dial score={Math.round(ra.fluency)} label="Fluency" desc="Pacing and pauses" />
                    <Dial score={Math.round(ra.completeness)} label="Completeness" desc="Words spoken" />
                    <Dial score={Math.round(ra.prosody)} label="Prosody" desc="Stress and rhythm" />
                  </div>

                  {ra.words_to_improve.length > 0 && (
                    <div className="words-row" style={{ marginTop: "0", paddingTop: "16px", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
                      <span className="word-label">Words to improve</span>
                      {ra.words_to_improve.map((w) => (
                        <span key={w} className="word-chip">
                          &ldquo;{w}&rdquo;
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* ZONE 4 — CTA */}
          <section className="zone4 fade-in d4">
            <div className="cta-card">
              <div className="cta-content">
                <div className="cta-eyebrow">Ready when you are</div>
                <div className="cta-title">Start your personalized journey</div>
                <div className="cta-sub">30 minutes a day. Adapted lessons. Real progress in week one.</div>
              </div>
              <div className="cta-action">
                <button className="cta-btn" onClick={continueToDashboard}>
                  Start my journey {I.arrow}
                </button>
                <div className="cta-foot">
                  <div className="avatar-stack">
                    <div style={{ background: "#fca5a5" }}></div>
                    <div style={{ background: "#fcd34d" }}></div>
                    <div style={{ background: "#86efac" }}></div>
                  </div>
                  <span>Joining 12,400 learners this week</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </section>

      <style dangerouslySetInnerHTML={{ __html: `
        .eyebrow { display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 999px; background: white; border: 1px solid #dbeafe; font-size: 12px; font-weight: 600; color: #1e40af; box-shadow: 0 1px 3px rgba(15,23,42,0.04); }
        .eyebrow-dot { width: 6px; height: 6px; border-radius: 50%; background: #2563eb; animation: pulseDot 2s infinite; }
        @keyframes pulseDot { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.6; } }

        /* ZONE 1 — Hero */
        .hero { display: grid; grid-template-columns: 1.15fr 1fr; gap: 22px; padding: 28px 32px; }
        .hero-left .h1 { font-size: 36px; font-weight: 800; letter-spacing: -0.025em; color: #0a1f44; line-height: 1.05; margin: 12px 0 14px; }
        .hero-left .h1 .grad { background: linear-gradient(90deg, #2563eb 0%, #6366f1 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .hero-summary { font-size: 15px; line-height: 1.55; color: #334155; max-width: 460px; }
        .hero-meta { display: flex; gap: 16px; margin-top: 18px; font-size: 12.5px; color: #64748b; }
        .hero-meta b { color: #0a1f44; font-weight: 600; }

        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; width: 100%; margin: 0 auto; }
        .stat { background: white; border: 1px solid #eef2f7; border-radius: 20px; padding: 18px 16px; box-shadow: 0 4px 16px rgba(15,23,42,0.04); display: flex; flex-direction: column; justify-content: space-between; min-height: 165px; position: relative; overflow: hidden; transition: transform 0.2s ease, box-shadow 0.2s ease; }
        .stat:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(15,23,42,0.08); }
        .stat-head { display: flex; align-items: center; gap: 8px; font-size: 10.5px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
        .stat-ico { width: 24px; height: 24px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .stat-value { font-size: 20px; font-weight: 800; color: #0a1f44; letter-spacing: -0.01em; line-height: 1.15; margin-bottom: 4px; }
        .stat-sub { font-size: 13px; color: #64748b; line-height: 1.45; opacity: 0.75; }
        .stat.red { background: linear-gradient(180deg, #fff5f5 0%, white 100%); border-color: #fecaca; }
        .stat.red .stat-ico { background: #fee2e2; color: #dc2626; }
        .stat.green { background: linear-gradient(180deg, #f0fdf4 0%, white 100%); border-color: #bbf7d0; }
        .stat.green .stat-ico { background: #dcfce7; color: #16a34a; }
        .stat.blue { background: linear-gradient(180deg, #eff6ff 0%, white 100%); border-color: #bfdbfe; }
        .stat.blue .stat-ico { background: #dbeafe; color: #2563eb; }
        .stat.amber { background: linear-gradient(180deg, #fffbeb 0%, white 100%); border-color: #fde68a; }
        .stat.amber .stat-ico { background: #fef3c7; color: #d97706; }

        /* ZONE 2 — Skill Profile */
        .zone2 { display: grid; grid-template-columns: 1.05fr 1fr; gap: 22px; padding: 22px 32px; border-top: 1px solid rgba(226,232,240,0.7); }
        .skill-list { display: flex; flex-direction: column; gap: 8px; }
        .skill-row { display: grid; grid-template-columns: 105px 1fr 120px; align-items: center; gap: 12px; padding: 6px 0; }
        .skill-name { font-size: 13.5px; font-weight: 600; color: #0a1f44; text-transform: capitalize; }
        .skill-bar { position: relative; height: 8px; background: #eef2f7; border-radius: 999px; overflow: hidden; }
        .skill-bar-fill { position: absolute; top: 0; left: 0; height: 100%; border-radius: 999px; transition: width 0.9s cubic-bezier(.16,1,.3,1); }
        .skill-tag { font-size: 11px; font-weight: 700; text-align: right; letter-spacing: 0.02em; text-transform: uppercase; }
        .tag-red { color: #dc2626; } .bar-red { background: linear-gradient(90deg, #f87171 0%, #ef4444 100%); }
        .tag-amber { color: #d97706; } .bar-amber { background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%); }
        .tag-green { color: #16a34a; } .bar-green { background: linear-gradient(90deg, #4ade80 0%, #22c55e 100%); }

        .zone-title { font-size: 18px; font-weight: 700; letter-spacing: -0.015em; color: #0a1f44; margin-bottom: 4px; }
        .zone-sub { font-size: 12.5px; color: #64748b; margin-bottom: 14px; }
        .legend { display: flex; gap: 14px; margin-top: 14px; flex-wrap: wrap; }
        .legend-item { display: flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 600; color: #475569; }
        .legend-dot { width: 8px; height: 8px; border-radius: 50%; }

        /* ZONE 3 — Speaking */
        .zone3 { display: grid; gap: 22px; padding: 22px 32px; border-top: 1px solid rgba(226,232,240,0.7); }
        .speaking-card { background: linear-gradient(160deg, #0a0f1f 0%, #1e3a8a 100%); border-radius: 18px; padding: 18px; color: white; box-shadow: 0 10px 30px rgba(10,15,31,0.18); position: relative; overflow: hidden; }
        .speaking-card::before { content: ""; position: absolute; top: -40px; right: -40px; width: 140px; height: 140px; border-radius: 50%; background: radial-gradient(circle, rgba(96,165,250,0.3) 0%, transparent 70%); }
        .speak-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; position: relative; }
        .speak-title { font-size: 13px; font-weight: 700; letter-spacing: 0.02em; text-transform: uppercase; opacity: 0.85; display: flex; align-items: center; gap: 6px; }
        .speak-pill { font-size: 10.5px; font-weight: 700; padding: 3px 8px; border-radius: 999px; background: rgba(255,255,255,0.15); color: #bfdbfe; }
        .words-row { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; position: relative; }
        .word-chip { font-size: 11.5px; font-weight: 600; padding: 4px 10px; border-radius: 999px; background: rgba(248,113,113,0.18); color: #fca5a5; border: 1px solid rgba(248,113,113,0.25); font-family: 'Source Serif 4', serif; font-style: italic; }
        .word-label { font-size: 10.5px; font-weight: 700; opacity: 0.55; text-transform: uppercase; letter-spacing: 0.06em; margin-right: 4px; align-self: center; }

        /* ZONE 4 — CTA */
        .zone4 { padding: 40px 32px 50px; border-top: 1px solid rgba(226,232,240,0.7); display: flex; justify-content: center; }
        .cta-card { background: linear-gradient(135deg, #2563eb 0%, #1e40af 50%, #4338ca 100%); border-radius: 24px; padding: 44px 50px; color: white; box-shadow: 0 14px 40px rgba(37,99,235,0.25); position: relative; overflow: hidden; width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 40px; }
        .cta-card::before { content: ""; position: absolute; inset: 0; background: radial-gradient(100% 100% at 100% 0%, rgba(255,255,255,0.15) 0%, transparent 60%); pointer-events: none; }
        .cta-content { flex: 1; position: relative; z-index: 1; }
        .cta-eyebrow { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8; margin-bottom: 8px; }
        .cta-title { font-size: 28px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 12px; }
        .cta-sub { font-size: 15px; line-height: 1.5; opacity: 0.85; max-width: 440px; }
        .cta-action { position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; gap: 14px; min-width: 280px; }
        .cta-btn { width: 100%; display: inline-flex; align-items: center; justify-content: center; gap: 10px; background: white; color: #0a1f44; font-size: 16px; font-weight: 700; border: none; padding: 16px 24px; border-radius: 999px; box-shadow: 0 4px 14px rgba(0,0,0,0.15); transition: transform 0.15s; cursor: pointer; }
        .cta-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }
        .cta-foot { display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 12px; opacity: 0.85; }
        .avatar-stack { display: flex; }
        .avatar-stack div { width: 20px; height: 20px; border-radius: 50%; border: 2px solid #1e40af; margin-left: -8px; }
        .avatar-stack div:first-child { margin-left: 0; }

        @media (max-width: 960px) {
          .hero, .zone2 { grid-template-columns: 1fr; }
          .cta-card { flex-direction: column; text-align: center; padding: 36px 24px; gap: 28px; }
          .cta-sub { margin: 0 auto; }
          .cta-action { width: 100%; min-width: 0; }
        }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .fade-in { animation: fadeUp 0.5s cubic-bezier(.16,1,.3,1) both; }
        .fade-in.d1 { animation-delay: 0.05s; }
        .fade-in.d2 { animation-delay: 0.12s; }
        .fade-in.d3 { animation-delay: 0.2s; }
        .fade-in.d4 { animation-delay: 0.3s; }
      `}} />
    </main>
  );
}
