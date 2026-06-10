"use client";

import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, ChevronRight, ExternalLink } from "lucide-react";
import { useRouter } from "next/navigation";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { authApi } from "@/lib/auth-api";
import {
  preferencesApi,
  type UserCoursePreferenceUpdate,
} from "@/lib/preferences-api";
import { subscriptionsApi } from "@/lib/subscriptions-api";
import type { NotificationSettings } from "@/lib/subscriptions-api";
import { useAuthStore } from "@/store/authStore";

const DEFAULT_NOTIFICATIONS: NotificationSettings = {
  daily_practice_reminder: true,
  streak_reminder: true,
  weekly_progress_email: false,
  feature_announcements: false,
};

type PracticeSettings = Required<
  Pick<
    UserCoursePreferenceUpdate,
    | "tasks_per_day"
    | "allow_read"
    | "allow_write"
    | "allow_listen"
    | "allow_speak"
    | "require_pass_to_advance"
    | "pass_threshold_pct"
  >
>;
type ActivitySettingKey =
  | "allow_read"
  | "allow_write"
  | "allow_listen"
  | "allow_speak";

const DEFAULT_PRACTICE_SETTINGS: PracticeSettings = {
  tasks_per_day: 2,
  allow_read: true,
  allow_write: true,
  allow_listen: true,
  allow_speak: true,
  require_pass_to_advance: false,
  pass_threshold_pct: 65,
};

type ModalKind =
  | "purchase-details"
  | "pause"
  | "delete-step-1"
  | "delete-step-2"
  | null;

const cardStyle: CSSProperties = {
  background: "rgba(255,255,255,0.88)",
  border: "1px solid rgba(255,255,255,0.92)",
  borderRadius: 8,
  boxShadow:
    "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
  padding: 28,
};

const buttonBase: CSSProperties = {
  borderRadius: 8,
  padding: "11px 15px",
  fontSize: 14,
  fontWeight: 700,
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  border: "1px solid transparent",
};

function formatDate(value: string | null | undefined) {
  if (!value) return "Not recorded yet";
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function formatMoney(amount: number, currency = "INR") {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

function Toggle({
  checked,
  disabled,
  onClick,
}: {
  checked: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      aria-pressed={checked}
      disabled={disabled}
      onClick={onClick}
      style={{
        width: 48,
        height: 28,
        borderRadius: 999,
        border: "none",
        padding: 3,
        cursor: disabled ? "not-allowed" : "pointer",
        background: checked ? "oklch(52% 0.18 240)" : "oklch(82% 0.02 245)",
        transition: "background 0.2s ease",
        opacity: disabled ? 0.7 : 1,
      }}
    >
      <span
        style={{
          display: "block",
          width: 22,
          height: 22,
          borderRadius: "50%",
          background: "white",
          transform: checked ? "translateX(20px)" : "translateX(0)",
          transition: "transform 0.2s ease",
          boxShadow: "0 1px 4px rgba(20,35,70,0.22)",
        }}
      />
    </button>
  );
}

export default function SettingsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();
  const [modal, setModal] = useState<ModalKind>(null);
  const [deleteText, setDeleteText] = useState("");
  const [notificationOverride, setNotificationOverride] = useState<
    Partial<NotificationSettings>
  >({});
  const [practiceOverride, setPracticeOverride] = useState<
    Partial<PracticeSettings>
  >({});

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const purchaseQuery = useQuery({
    queryKey: ["purchase"],
    queryFn: subscriptionsApi.me,
    enabled: isReady,
  });

  useEffect(() => {
    if (user && !user.diagnosis_completed) router.replace("/diagnosis");
  }, [user, router]);

  const notifications = {
    ...(user?.notifications ?? DEFAULT_NOTIFICATIONS),
    ...notificationOverride,
  };
  const practiceSettings: PracticeSettings = {
    ...DEFAULT_PRACTICE_SETTINGS,
    ...(user?.preference
      ? {
          tasks_per_day: user.preference.tasks_per_day,
          allow_read: user.preference.allow_read,
          allow_write: user.preference.allow_write,
          allow_listen: user.preference.allow_listen,
          allow_speak: user.preference.allow_speak,
          require_pass_to_advance: user.preference.require_pass_to_advance,
          pass_threshold_pct: user.preference.pass_threshold_pct,
        }
      : {}),
    ...practiceOverride,
  };

  const pauseMutation = useMutation({
    mutationFn: subscriptionsApi.pause,
    onSuccess: async () => {
      setModal(null);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["me"] }),
        queryClient.invalidateQueries({ queryKey: ["purchase"] }),
      ]);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: subscriptionsApi.deleteAccount,
    onSuccess: () => {
      logout();
      router.replace("/login");
    },
  });

  const notificationMutation = useMutation({
    mutationFn: subscriptionsApi.updateNotifications,
    onError: () => {
      setNotificationOverride({});
    },
    onSuccess: (saved) => setNotificationOverride(saved),
  });

  const practiceMutation = useMutation({
    mutationFn: preferencesApi.update,
    onError: () => {
      setPracticeOverride({});
    },
    onSuccess: async (saved) => {
      setPracticeOverride({
        tasks_per_day: saved.tasks_per_day,
        allow_read: saved.allow_read,
        allow_write: saved.allow_write,
        allow_listen: saved.allow_listen,
        allow_speak: saved.allow_speak,
        require_pass_to_advance: saved.require_pass_to_advance,
        pass_threshold_pct: saved.pass_threshold_pct,
      });
      await queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const currentPlan = useMemo(() => {
    const purchase = purchaseQuery.data;
    if (purchase) return purchase;
    const courseLength = user?.preference?.course_length;
    return {
      id: 0,
      user_id: user?.id ?? 0,
      plan_id: courseLength === "48w" ? "beginner-48w" : "beginner-24w",
      plan_name: courseLength === "48w" ? "48-Week Plan" : "24-Week Foundation",
      amount_paid: courseLength === "48w" ? 1999 : 999,
      currency: "INR",
      status: "paid",
      created_at: "",
    };
  }, [purchaseQuery.data, user]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const toggleNotification = (key: keyof NotificationSettings) => {
    const next = { ...notifications, [key]: !notifications[key] };
    setNotificationOverride(next);
    notificationMutation.mutate({ [key]: next[key] });
  };

  const updatePractice = (patch: Partial<PracticeSettings>) => {
    if (!user?.preference) return;
    const next = { ...practiceSettings, ...patch };
    setPracticeOverride(next);
    practiceMutation.mutate(next);
  };

  const toggleActivity = (key: ActivitySettingKey) => {
    const activeCount = (
      [
        "allow_read",
        "allow_write",
        "allow_listen",
        "allow_speak",
      ] as ActivitySettingKey[]
    ).filter((activityKey) => practiceSettings[activityKey]).length;
    if (practiceSettings[key] && activeCount <= 2) return;
    updatePractice({ [key]: !practiceSettings[key] });
  };

  if (!isReady) return null;

  return (
    <div
      style={{
        minHeight: "100vh",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        background:
          "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
      }}
    >
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <DashboardLayout
        user={user}
        onSignOut={handleLogout}
        mainStyle={{ maxWidth: 860, margin: "0 auto", padding: "40px 20px 72px" }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <CourseCard
            planName={currentPlan.plan_name}
            amount={formatMoney(currentPlan.amount_paid, currentPlan.currency)}
            purchasedDate={formatDate(currentPlan.created_at)}
            status={currentPlan.status}
            onDetails={() => setModal("purchase-details")}
            onUpgrade={() => router.push("/pricing")}
          />
          {user?.preference && (
            <DailyPracticeCard
              settings={practiceSettings}
              isSaving={practiceMutation.isPending}
              onTasksPerDay={(tasksPerDay) =>
                updatePractice({ tasks_per_day: tasksPerDay })
              }
              onToggleActivity={toggleActivity}
              onTogglePass={() =>
                updatePractice({
                  require_pass_to_advance:
                    !practiceSettings.require_pass_to_advance,
                })
              }
              onThreshold={(value) =>
                updatePractice({ pass_threshold_pct: value })
              }
            />
          )}
          <NotificationsCard
            notifications={notifications}
            isSaving={notificationMutation.isPending}
            onToggle={toggleNotification}
          />
          <AboutCard />
          <AccountCard
            onSignOut={handleLogout}
            onPause={() => setModal("pause")}
            onDelete={() => setModal("delete-step-1")}
          />
        </div>
      </DashboardLayout>

      {modal === "purchase-details" && (
        <ConfirmModal
          title="Purchase details"
          body={`${currentPlan.plan_name} was purchased for ${formatMoney(
            currentPlan.amount_paid,
            currentPlan.currency,
          )}. Purchase date: ${formatDate(currentPlan.created_at)}. Status: ${
            currentPlan.status
          }.`}
          confirmLabel="Done"
          onCancel={() => setModal(null)}
          onConfirm={() => setModal(null)}
        />
      )}
      {modal === "pause" && (
        <ConfirmModal
          title="Pause course"
          body="Your purchase stays on your account. This only pauses your active learning schedule."
          confirmLabel="Pause course"
          tone="danger"
          isLoading={pauseMutation.isPending}
          onCancel={() => setModal(null)}
          onConfirm={() => pauseMutation.mutate()}
        />
      )}
      {modal === "delete-step-1" && (
        <ConfirmModal
          title="Are you sure?"
          body="This will permanently delete your account, progress, and all task history."
          confirmLabel="Continue"
          tone="danger"
          onCancel={() => setModal(null)}
          onConfirm={() => setModal("delete-step-2")}
        />
      )}
      {modal === "delete-step-2" && (
        <div style={overlayStyle}>
          <div style={modalStyle}>
            <h2 style={modalTitleStyle}>Type DELETE to confirm</h2>
            <p style={modalBodyStyle}>
              This action cannot be undone. Enter DELETE to enable account deletion.
            </p>
            <input
              autoFocus
              value={deleteText}
              onChange={(event) => setDeleteText(event.target.value)}
              style={{
                width: "100%",
                boxSizing: "border-box",
                border: "1px solid oklch(82% 0.03 245)",
                borderRadius: 8,
                padding: "12px 13px",
                fontSize: 14,
                marginTop: 14,
              }}
            />
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 22 }}>
              <button style={{ ...buttonBase, background: "white", borderColor: "oklch(82% 0.03 245)" }} onClick={() => setModal(null)}>
                Cancel
              </button>
              <button
                disabled={deleteText !== "DELETE" || deleteMutation.isPending}
                style={{
                  ...buttonBase,
                  background: "oklch(54% 0.2 28)",
                  color: "white",
                  opacity: deleteText === "DELETE" ? 1 : 0.45,
                }}
                onClick={() => deleteMutation.mutate()}
              >
                Delete account
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CourseCard({
  planName,
  amount,
  purchasedDate,
  status,
  onDetails,
  onUpgrade,
}: {
  planName: string;
  amount: string;
  purchasedDate: string;
  status: string;
  onDetails: () => void;
  onUpgrade: () => void;
}) {
  return (
    <section style={cardStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "center", marginBottom: 18 }}>
        <h1 style={{ margin: 0, fontSize: 22, color: "oklch(15% 0.09 245)", fontWeight: 800 }}>
          Course & purchase
        </h1>
        <span style={{ borderRadius: 999, background: "oklch(91% 0.07 145)", color: "oklch(38% 0.12 145)", padding: "5px 11px", fontSize: 12, fontWeight: 800 }}>
          {status === "paused" ? "Paused" : "Active"}
        </span>
      </div>
      <div style={{ background: "oklch(95% 0.035 240)", border: "1px solid oklch(89% 0.045 240)", borderRadius: 8, padding: 22, display: "grid", gridTemplateColumns: "1fr auto", gap: 18, alignItems: "center" }}>
        <div>
          <p style={{ margin: "0 0 8px", fontSize: 11, fontWeight: 800, letterSpacing: 1.1, color: "oklch(45% 0.09 240)" }}>
            CURRENT PLAN
          </p>
          <h2 style={{ margin: "0 0 8px", fontSize: 26, fontWeight: 800, color: "oklch(15% 0.09 245)" }}>
            {planName}
          </h2>
          <p style={{ margin: 0, color: "oklch(48% 0.06 240)", fontSize: 14 }}>
            {amount} &middot; billed once &middot; purchased {purchasedDate}
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
          <button onClick={onDetails} style={{ ...buttonBase, background: "white", borderColor: "rgba(80,120,200,0.28)", color: "oklch(30% 0.08 240)" }}>
            Purchase details
          </button>
          <button onClick={onUpgrade} style={{ ...buttonBase, background: "oklch(52% 0.18 240)", color: "white" }}>
            Upgrade plan <ArrowRight size={16} />
          </button>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 14 }}>
        <UsageTile label="Tasks completed this month" value="18" />
        <UsageTile label="Pronunciation minutes" value="42 / 120" />
        <UsageTile label="Purchase amount" value={amount} detail="Billed once" />
      </div>
    </section>
  );
}

function UsageTile({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div style={{ border: "1px solid oklch(88% 0.03 245)", borderRadius: 8, padding: 15, background: "rgba(255,255,255,0.72)" }}>
      <p style={{ margin: "0 0 8px", color: "oklch(50% 0.05 240)", fontSize: 12, lineHeight: 1.35 }}>{label}</p>
      <p style={{ margin: 0, color: "oklch(18% 0.09 245)", fontWeight: 800, fontSize: 18 }}>{value}</p>
      {detail && <p style={{ margin: "5px 0 0", color: "oklch(50% 0.05 240)", fontSize: 12 }}>{detail}</p>}
    </div>
  );
}

const PASS_THRESHOLD_PRESETS = [50, 65, 75, 85];

function DailyPracticeCard({
  settings,
  isSaving,
  onTasksPerDay,
  onToggleActivity,
  onTogglePass,
  onThreshold,
}: {
  settings: PracticeSettings;
  isSaving: boolean;
  onTasksPerDay: (value: number) => void;
  onToggleActivity: (key: ActivitySettingKey) => void;
  onTogglePass: () => void;
  onThreshold: (value: number) => void;
}) {
  const activities: Array<{
    key: ActivitySettingKey;
    label: string;
    detail: string;
  }> = [
    { key: "allow_read", label: "Read", detail: "Reading-based practice" },
    { key: "allow_write", label: "Write", detail: "Written answer practice" },
    { key: "allow_listen", label: "Listen", detail: "Listening comprehension" },
    { key: "allow_speak", label: "Speak", detail: "Recorded speaking tasks" },
  ];
  const activeCount = activities.filter((activity) => settings[activity.key]).length;

  return (
    <section style={cardStyle}>
      <h2 style={{ margin: "0 0 6px", fontSize: 21, color: "oklch(15% 0.09 245)", fontWeight: 800 }}>
        Daily practice
      </h2>
      <p style={{ margin: "0 0 16px", color: "oklch(48% 0.06 240)", fontSize: 14 }}>
        Set how many dashboard tasks unlock each day and which activity types can appear.
      </p>

      <div style={{ marginBottom: 20 }}>
        <p style={{ margin: "0 0 10px", color: "oklch(18% 0.08 245)", fontWeight: 800, fontSize: 14 }}>
          Tasks per day
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gap: 8,
            maxWidth: 360,
          }}
        >
          {[2, 3, 4].map((value) => {
            const selected = settings.tasks_per_day === value;
            return (
              <button
                key={value}
                type="button"
                disabled={isSaving}
                onClick={() => onTasksPerDay(value)}
                style={{
                  borderRadius: 8,
                  border: selected
                    ? "1px solid oklch(52% 0.18 240)"
                    : "1px solid oklch(86% 0.03 245)",
                  background: selected ? "oklch(93% 0.04 240)" : "white",
                  color: selected ? "oklch(34% 0.14 240)" : "oklch(30% 0.07 240)",
                  padding: "11px 0",
                  fontSize: 14,
                  fontWeight: 800,
                  cursor: isSaving ? "not-allowed" : "pointer",
                  opacity: isSaving ? 0.72 : 1,
                }}
              >
                {value}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline", marginBottom: 6 }}>
          <p style={{ margin: 0, color: "oklch(18% 0.08 245)", fontWeight: 800, fontSize: 14 }}>
            Core activities
          </p>
          <span style={{ color: "oklch(48% 0.06 240)", fontSize: 12, fontWeight: 700 }}>
            {activeCount} / 4 active
          </span>
        </div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          {activities.map((activity, index) => {
            const checked = settings[activity.key];
            const disableToggle = isSaving || (checked && activeCount <= 2);
            return (
              <div
                key={activity.key}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 18,
                  padding: "15px 0",
                  borderTop: index === 0 ? "none" : "1px solid oklch(90% 0.025 245)",
                }}
              >
                <div>
                  <p style={{ margin: 0, color: "oklch(18% 0.08 245)", fontWeight: 700, fontSize: 14 }}>
                    {activity.label}
                  </p>
                  <p style={{ margin: "4px 0 0", color: "oklch(50% 0.05 240)", fontSize: 13 }}>
                    {activity.detail}
                  </p>
                </div>
                <Toggle
                  checked={checked}
                  disabled={disableToggle}
                  onClick={() => onToggleActivity(activity.key)}
                />
              </div>
            );
          })}
        </div>
      </div>

      <div
        style={{
          marginTop: 22,
          paddingTop: 20,
          borderTop: "1px solid oklch(90% 0.025 245)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 18,
          }}
        >
          <div>
            <p style={{ margin: 0, color: "oklch(18% 0.08 245)", fontWeight: 800, fontSize: 14 }}>
              Require a passing score to advance
            </p>
            <p style={{ margin: "4px 0 0", color: "oklch(50% 0.05 240)", fontSize: 13 }}>
              Repeat an activity until you clear the threshold before moving on.
            </p>
          </div>
          <Toggle
            checked={settings.require_pass_to_advance}
            disabled={isSaving}
            onClick={onTogglePass}
          />
        </div>

        {settings.require_pass_to_advance && (
          <div style={{ marginTop: 16 }}>
            <p style={{ margin: "0 0 10px", color: "oklch(18% 0.08 245)", fontWeight: 800, fontSize: 14 }}>
              Passing threshold
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                gap: 8,
                maxWidth: 360,
              }}
            >
              {PASS_THRESHOLD_PRESETS.map((value) => {
                const selected = settings.pass_threshold_pct === value;
                return (
                  <button
                    key={value}
                    type="button"
                    disabled={isSaving}
                    onClick={() => onThreshold(value)}
                    style={{
                      borderRadius: 8,
                      border: selected
                        ? "1px solid oklch(52% 0.18 240)"
                        : "1px solid oklch(86% 0.03 245)",
                      background: selected ? "oklch(93% 0.04 240)" : "white",
                      color: selected ? "oklch(34% 0.14 240)" : "oklch(30% 0.07 240)",
                      padding: "11px 0",
                      fontSize: 14,
                      fontWeight: 800,
                      cursor: isSaving ? "not-allowed" : "pointer",
                      opacity: isSaving ? 0.72 : 1,
                    }}
                  >
                    {value}%
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

function NotificationsCard({
  notifications,
  isSaving,
  onToggle,
}: {
  notifications: NotificationSettings;
  isSaving: boolean;
  onToggle: (key: keyof NotificationSettings) => void;
}) {
  const rows: Array<{ key: keyof NotificationSettings; label: string; detail: string }> = [
    { key: "daily_practice_reminder", label: "Daily practice reminder", detail: "Nudge if no task by 7 PM" },
    { key: "streak_reminder", label: "Streak reminder", detail: "Alert 2h before midnight" },
    { key: "weekly_progress_email", label: "Weekly progress email", detail: "Sunday summary" },
    { key: "feature_announcements", label: "New feature announcements", detail: "Product updates" },
  ];

  return (
    <section style={cardStyle}>
      <h2 style={{ margin: "0 0 6px", fontSize: 21, color: "oklch(15% 0.09 245)", fontWeight: 800 }}>
        Notifications
      </h2>
      <p style={{ margin: "0 0 12px", color: "oklch(48% 0.06 240)", fontSize: 14 }}>
        Control when and how LingosAI contacts you.
      </p>
      {rows.map((row, index) => (
        <div
          key={row.key}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 18,
            padding: "15px 0",
            borderTop: index === 0 ? "none" : "1px solid oklch(90% 0.025 245)",
          }}
        >
          <div>
            <p style={{ margin: 0, color: "oklch(18% 0.08 245)", fontWeight: 700, fontSize: 14 }}>{row.label}</p>
            <p style={{ margin: "4px 0 0", color: "oklch(50% 0.05 240)", fontSize: 13 }}>{row.detail}</p>
          </div>
          <Toggle checked={notifications[row.key]} disabled={isSaving} onClick={() => onToggle(row.key)} />
        </div>
      ))}
    </section>
  );
}

function AboutCard() {
  const links = [
    { label: "About LingosAI", href: "/about" },
    { label: "How it works", href: "/how-it-works", external: true },
    { label: "Features", href: "/features", external: true },
    { label: "Privacy policy", href: "/privacy" },
    { label: "Terms of service", href: "/terms" },
    { label: "Contact support", href: "mailto:support@lingosai.com" },
  ];
  return (
    <section style={cardStyle}>
      <h2 style={{ margin: "0 0 16px", fontSize: 21, color: "oklch(15% 0.09 245)", fontWeight: 800 }}>
        About & help
      </h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
        {links.map((link) => (
          <a
            key={link.label}
            href={link.href}
            style={{
              border: "1px solid oklch(88% 0.03 245)",
              borderRadius: 8,
              padding: "14px 15px",
              color: "oklch(20% 0.08 245)",
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              fontSize: 14,
              fontWeight: 700,
              background: "rgba(255,255,255,0.52)",
            }}
            onMouseEnter={(event) => {
              event.currentTarget.style.background = "oklch(96% 0.03 240)";
            }}
            onMouseLeave={(event) => {
              event.currentTarget.style.background = "rgba(255,255,255,0.52)";
            }}
          >
            {link.label}
            {link.external ? <ExternalLink size={16} /> : <ChevronRight size={16} />}
          </a>
        ))}
      </div>
      <p style={{ margin: "18px 0 0", color: "oklch(52% 0.05 240)", fontSize: 13 }}>
        App version 0.1.0
      </p>
    </section>
  );
}

function AccountCard({
  onSignOut,
  onPause,
  onDelete,
}: {
  onSignOut: () => void;
  onPause: () => void;
  onDelete: () => void;
}) {
  return (
    <section style={{ ...cardStyle, border: "1px solid #f7c8c8" }}>
      <h2 style={{ margin: "0 0 6px", fontSize: 21, color: "oklch(46% 0.18 28)", fontWeight: 800 }}>
        Account
      </h2>
      <p style={{ margin: "0 0 18px", color: "oklch(48% 0.06 240)", fontSize: 14 }}>
        Permanent actions — please read before clicking.
      </p>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <button onClick={onSignOut} style={{ ...buttonBase, background: "white", borderColor: "oklch(84% 0.025 245)", color: "oklch(28% 0.06 245)" }}>
          Sign out
        </button>
        <button onClick={onPause} style={{ ...buttonBase, background: "oklch(96% 0.03 28)", color: "oklch(45% 0.16 28)", borderColor: "oklch(90% 0.05 28)" }}>
          Pause course
        </button>
        <button onClick={onDelete} style={{ ...buttonBase, background: "oklch(54% 0.2 28)", color: "white" }}>
          Delete account
        </button>
      </div>
    </section>
  );
}

const overlayStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  zIndex: 50,
  background: "rgba(10,18,35,0.42)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 20,
};

const modalStyle: CSSProperties = {
  width: "100%",
  maxWidth: 430,
  background: "white",
  borderRadius: 8,
  padding: 24,
  boxShadow: "0 24px 70px rgba(20,35,70,0.22)",
};

const modalTitleStyle: CSSProperties = {
  margin: "0 0 9px",
  fontSize: 21,
  color: "oklch(15% 0.09 245)",
  fontWeight: 800,
};

const modalBodyStyle: CSSProperties = {
  margin: 0,
  color: "oklch(42% 0.06 240)",
  fontSize: 14,
  lineHeight: 1.55,
};

function ConfirmModal({
  title,
  body,
  confirmLabel,
  tone,
  isLoading,
  onCancel,
  onConfirm,
}: {
  title: string;
  body: string;
  confirmLabel: string;
  tone?: "danger";
  isLoading?: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h2 style={modalTitleStyle}>{title}</h2>
        <p style={modalBodyStyle}>{body}</p>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 22 }}>
          <button style={{ ...buttonBase, background: "white", borderColor: "oklch(82% 0.03 245)" }} onClick={onCancel}>
            Cancel
          </button>
          <button
            disabled={isLoading}
            style={{
              ...buttonBase,
              background: tone === "danger" ? "oklch(54% 0.2 28)" : "oklch(52% 0.18 240)",
              color: "white",
              opacity: isLoading ? 0.7 : 1,
            }}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
