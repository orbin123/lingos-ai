"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ChevronRight, Clock, Layers, Timer, Trophy } from "lucide-react";
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
        fontFamily: "var(--font-geist-sans), Arial, sans-serif",
        background: "#eef4f8",
      }}
    >
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
                background: "#ffffff",
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
                  background: "#eef4f8",
                  display: "grid",
                  placeItems: "center",
                  color: "#0ea5e9",
                }}
              >
                <Timer size={24} strokeWidth={2} aria-hidden />
              </div>

              <div style={{ flex: 1 }}>
                <h2
                  style={{
                    margin: 0,
                    color: "#0f172a",
                    fontSize: 22,
                    fontWeight: 700,
                    lineHeight: 1.3,
                  }}
                >
                  {challenge.name}
                </h2>
                <p
                  style={{
                    margin: "8px 0 0",
                    color: "#64748b",
                    fontSize: 15,
                    lineHeight: 1.6,
                  }}
                >
                  {challenge.short_description}
                </p>
              </div>

              <div style={{ width: "100%", height: 1, borderTop: "2px dotted #e2e8f0" }} />

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
                    color: "#64748b",
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
                    color: "#0284c7",
                  }}
                >
                  View <ChevronRight size={16} aria-hidden />
                </span>
              </div>
            </button>
          ))}

          {/* Coming soon placeholder */}
          <div
            style={{
              background: "transparent",
              border: "2px dashed #cbd5e1",
              borderRadius: 24,
              padding: 32,
              display: "flex",
              flexDirection: "column",
              gap: 24,
            }}
          >
            <div
              style={{
                width: 52,
                height: 52,
                borderRadius: 16,
                background: "#f1f5f9",
                display: "grid",
                placeItems: "center",
                color: "#94a3b8",
              }}
            >
              <Timer size={24} strokeWidth={2} aria-hidden />
            </div>
            <div style={{ flex: 1 }}>
              <h2
                style={{
                  margin: 0,
                  color: "#64748b",
                  fontSize: 22,
                  fontWeight: 700,
                  lineHeight: 1.3,
                }}
              >
                More coming soon
              </h2>
              <p style={{ margin: "8px 0 0", color: "#94a3b8", fontSize: 15, lineHeight: 1.6 }}>
                New challenge types are on the way.
              </p>
            </div>
            
            <div style={{ width: "100%", height: 1, borderTop: "2px dotted #cbd5e1" }} />
            
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
                  color: "#94a3b8",
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
  );
}
