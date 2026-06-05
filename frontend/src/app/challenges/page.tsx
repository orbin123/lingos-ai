"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ChevronRight, Clock, Gamepad2, Layers, Timer, Trophy } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { authApi } from "@/lib/auth-api";
import { challengesApi } from "@/lib/challenges-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

export default function ChallengesPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const { data: challenges, isLoading } = useQuery({
    queryKey: ["challenges"],
    queryFn: challengesApi.list,
    enabled: isReady && !!user?.diagnosis_completed,
  });

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background: "oklch(91% 0.04 245)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />

      {/* Dot grid overlay */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.13) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div style={{ position: "relative", zIndex: 1 }}>
        <DashboardLayout
        user={user}
        onSignOut={handleLogout}
        mainStyle={{
          maxWidth: 1080,
          margin: "0 auto",
          padding: "40px 20px 76px",
        }}
      >
        <div style={{ marginBottom: 40 }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              color: "#0f4a8a",
              backgroundColor: "#dbeafe",
              padding: "6px 14px",
              borderRadius: 9999,
              fontSize: 13,
              fontWeight: 700,
              marginBottom: 16,
            }}
          >
            <Trophy size={16} aria-hidden />
            Challenges
          </div>
          <h1
            style={{
              margin: 0,
              color: "#0f172a",
              fontSize: 32,
              fontWeight: 800,
              lineHeight: 1.2,
            }}
          >
            Pick a Challenge
          </h1>
          <p style={{ margin: "12px 0 0", color: "#64748b", fontSize: 16, lineHeight: 1.6 }}>
            Timed, exam-style tasks to test your real English skills.
          </p>
        </div>

        {isLoading && (
          <p style={{ color: "#64748b", fontSize: 15 }}>Loading challenges…</p>
        )}

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 420px), 1fr))",
            gap: 24,
          }}
        >
          {challenges?.map((challenge) => (
            <button
              key={challenge.id}
              type="button"
              onClick={() => router.push(`/challenges/${challenge.slug}`)}
              style={{
                textAlign: "left",
                background: challenge.name === "IELTS Sprint" ? "linear-gradient(to bottom, rgba(9, 14, 23, 0.65), rgba(9, 14, 23, 0.95)), url(/images/ielts_sprint_bg.png) center/cover no-repeat" : "#ffffff",
                border: "none",
                borderRadius: 24,
                padding: 32,
                cursor: "pointer",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.04)",
                transition: "box-shadow 0.2s, transform 0.2s",
                display: "flex",
                flexDirection: "column",
                gap: 24,
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.boxShadow =
                  "0 12px 32px rgba(0, 0, 0, 0.08)";
                (e.currentTarget as HTMLButtonElement).style.transform = "translateY(-4px)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.boxShadow =
                  "0 4px 20px rgba(0, 0, 0, 0.04)";
                (e.currentTarget as HTMLButtonElement).style.transform = "translateY(0)";
              }}
            >
              <div
                style={{
                  width: 52,
                  height: 52,
                  borderRadius: 16,
                  background: challenge.name === "IELTS Sprint" ? "rgba(255, 255, 255, 0.2)" : "#eef4f8",
                  display: "grid",
                  placeItems: "center",
                  color: challenge.name === "IELTS Sprint" ? "#fff" : "#0ea5e9",
                  backdropFilter: challenge.name === "IELTS Sprint" ? "blur(4px)" : "none",
                }}
              >
                <Timer size={24} strokeWidth={2} aria-hidden />
              </div>

              <div style={{ flex: 1 }}>
                <h2
                  style={{
                    margin: 0,
                    color: challenge.name === "IELTS Sprint" ? "#ffffff" : "#0f172a",
                    fontSize: 22,
                    fontWeight: 700,
                    lineHeight: 1.3,
                    textShadow: challenge.name === "IELTS Sprint" ? "0 2px 10px rgba(0,0,0,0.8), 0 1px 3px rgba(0,0,0,0.9)" : "none",
                  }}
                >
                  {challenge.name}
                </h2>
                <p
                  style={{
                    margin: "8px 0 0",
                    color: challenge.name === "IELTS Sprint" ? "#f8fafc" : "#64748b",
                    fontSize: 15,
                    lineHeight: 1.6,
                    textShadow: challenge.name === "IELTS Sprint" ? "0 2px 8px rgba(0,0,0,0.8), 0 1px 2px rgba(0,0,0,0.9)" : "none",
                  }}
                >
                  {challenge.short_description}
                </p>
              </div>

              <div style={{ width: "100%", height: 1, borderTop: challenge.name === "IELTS Sprint" ? "2px dotted rgba(255,255,255,0.3)" : "2px dotted #e2e8f0" }} />

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  width: "100%",
                }}
              >
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 8,
                    fontSize: 14,
                    fontWeight: 600,
                    color: challenge.name === "IELTS Sprint" ? "#f8fafc" : "#64748b",
                    textShadow: challenge.name === "IELTS Sprint" ? "0 2px 8px rgba(0,0,0,0.8)" : "none",
                  }}
                >
                  <Layers size={16} aria-hidden />
                  {challenge.level_count} levels
                </span>
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 4,
                    fontSize: 15,
                    fontWeight: 700,
                    color: challenge.name === "IELTS Sprint" ? "#ffffff" : "#0284c7",
                    textShadow: challenge.name === "IELTS Sprint" ? "0 2px 8px rgba(0,0,0,0.8)" : "none",
                  }}
                >
                  View <ChevronRight size={16} aria-hidden />
                </span>
              </div>
            </button>
          ))}

          {/* A2Z Challenge Placeholder */}
          <button
            type="button"
            onClick={() => router.push(`/challenges/a2z`)}
            style={{
              textAlign: "left",
              background: "linear-gradient(to bottom, rgba(9, 14, 23, 0.65), rgba(9, 14, 23, 0.95)), url(/images/a2z_game_bg.png) center/cover no-repeat",
              border: "none",
              borderRadius: 24,
              padding: 32,
              cursor: "pointer",
              boxShadow: "0 4px 20px rgba(0, 0, 0, 0.04)",
              transition: "box-shadow 0.2s, transform 0.2s",
              display: "flex",
              flexDirection: "column",
              gap: 24,
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.boxShadow =
                "0 12px 32px rgba(0, 0, 0, 0.08)";
              (e.currentTarget as HTMLButtonElement).style.transform = "translateY(-4px)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.boxShadow =
                "0 4px 20px rgba(0, 0, 0, 0.04)";
              (e.currentTarget as HTMLButtonElement).style.transform = "translateY(0)";
            }}
          >
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 16,
                background: "rgba(255, 255, 255, 0.2)",
                display: "grid",
                placeItems: "center",
                color: "#ffffff",
                fontWeight: "900",
                fontSize: 24,
                letterSpacing: "-0.05em",
                backdropFilter: "blur(4px)",
              }}
            >
              a2z
            </div>

            <div style={{ flex: 1 }}>
              <h2
                style={{
                  margin: 0,
                  color: "#ffffff",
                  fontSize: 22,
                  fontWeight: 700,
                  lineHeight: 1.3,
                  textShadow: "0 2px 10px rgba(0,0,0,0.8), 0 1px 3px rgba(0,0,0,0.9)",
                }}
              >
                a2z
              </h2>
              <p
                style={{
                  margin: "8px 0 0",
                  color: "#f8fafc",
                  fontSize: 15,
                  lineHeight: 1.6,
                  textShadow: "0 2px 8px rgba(0,0,0,0.8), 0 1px 2px rgba(0,0,0,0.9)",
                }}
              >
                Spin for a letter, then race the clock naming words that start with it.
              </p>
            </div>

            <div style={{ width: "100%", height: 1, borderTop: "2px dotted rgba(255,255,255,0.3)" }} />

            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
              }}
            >
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 14,
                  fontWeight: 600,
                  color: "#f8fafc",
                  textShadow: "0 2px 8px rgba(0,0,0,0.8)",
                }}
              >
                <Layers size={16} aria-hidden />
                3 levels
              </span>
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 4,
                  fontSize: 15,
                  fontWeight: 700,
                  color: "#ffffff",
                  textShadow: "0 2px 8px rgba(0,0,0,0.8)",
                }}
              >
                View <ChevronRight size={16} aria-hidden />
              </span>
            </div>
          </button>

          {/* Coming soon placeholder */}
          <div
            style={{
              background: "rgba(255, 255, 255, 0.3)",
              backdropFilter: "blur(18px)",
              border: "2.5px dashed rgba(148, 163, 184, 0.55)",
              borderRadius: 24,
              padding: 32,
              display: "flex",
              flexDirection: "column",
              gap: 24,
              boxShadow: "0 4px 24px rgba(80, 110, 180, 0.04)",
            }}
          >
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 16,
                background: "rgba(148, 163, 184, 0.15)",
                display: "grid",
                placeItems: "center",
                color: "#7c3aed",
                backdropFilter: "blur(4px)",
              }}
            >
              <Gamepad2 size={24} strokeWidth={2} aria-hidden />
            </div>
            <div style={{ flex: 1 }}>
              <h2
                style={{
                  margin: 0,
                  color: "#1e293b",
                  fontSize: 22,
                  fontWeight: 800,
                  lineHeight: 1.3,
                }}
              >
                More coming soon
              </h2>
              <p style={{ margin: "8px 0 0", color: "#475569", fontSize: 15, lineHeight: 1.6, fontWeight: 500 }}>
                New challenge types are on the way.
              </p>
            </div>
            
            <div style={{ width: "100%", height: 1, borderTop: "2px dotted rgba(148, 163, 184, 0.4)" }} />
            
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                width: "100%",
              }}
            >
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                  fontSize: 14,
                  fontWeight: 700,
                  color: "#475569",
                }}
              >
                <Clock size={16} aria-hidden />
                Coming soon
              </span>
            </div>
          </div>
        </div>
      </DashboardLayout>
      </div>
    </div>
  );
}
