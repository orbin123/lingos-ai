"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { authApi } from "@/lib/auth-api";
import { useAuthStore } from "@/store/authStore";

export default function ChallengesPage() {
  const router = useRouter();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
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
        background:
          "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
        position: "relative",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />

      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          pointerEvents: "none",
          backgroundImage:
            "radial-gradient(circle, rgba(90,130,210,0.18) 1px, transparent 1px)",
          backgroundSize: "22px 22px",
          zIndex: 0,
        }}
      />

      <div style={{ position: "relative", zIndex: 1 }}>
        <DashboardLayout
          user={user}
          onSignOut={handleLogout}
          mainStyle={{
            maxWidth: 780,
            margin: "0 auto",
            padding: "56px 20px 80px",
          }}
        >
          <section
            style={{
              minHeight: 360,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              background: "rgba(255,255,255,0.86)",
              backdropFilter: "blur(20px)",
              WebkitBackdropFilter: "blur(20px)",
              border: "1px solid rgba(255,255,255,0.9)",
              borderRadius: 8,
              boxShadow:
                "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
              padding: "48px 28px",
            }}
          >
            {isLoading ? (
              <p style={{ margin: 0, color: "oklch(45% 0.07 240)", fontSize: 15 }}>
                Loading challenges...
              </p>
            ) : (
              <>
                <p
                  style={{
                    margin: "0 0 10px",
                    color: "oklch(48% 0.14 240)",
                    fontSize: 13,
                    fontWeight: 700,
                    letterSpacing: 1,
                    textTransform: "uppercase",
                  }}
                >
                  Challenges
                </p>
                <h1
                  style={{
                    margin: 0,
                    color: "oklch(15% 0.09 245)",
                    fontSize: 32,
                    fontWeight: 800,
                    letterSpacing: "-0.02em",
                  }}
                >
                  Coming soon
                </h1>
              </>
            )}
          </section>
        </DashboardLayout>
      </div>
    </div>
  );
}
