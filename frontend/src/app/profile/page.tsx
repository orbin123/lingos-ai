"use client";

import type { CSSProperties, ReactNode } from "react";
import { Suspense, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import {
  AlertTriangle,
  ArrowRight,
  ClipboardList,
  Globe2,
  Info,
  Languages,
  Sparkles,
  UserRound,
  X,
} from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { authApi, type UserOut, type UserUpdateInput } from "@/lib/auth-api";
import { progressApi, type SkillScoreSnapshot } from "@/lib/progress-api";
import { getSkillLabel, SKILL_ORDER } from "@/lib/skill-labels";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

type ProfileTab = "edit" | "personalisation" | "diagnosis";

const GOAL_OPTIONS = [
  "Job interviews",
  "Academic writing",
  "Daily conversation",
  "Business emails",
  "IELTS/TOEFL prep",
];

const COUNTRY_OPTIONS = ["India", "United States", "United Kingdom", "Canada", "Australia", "Germany", "Singapore"];
const LANGUAGE_OPTIONS = ["Hindi", "Tamil", "Malayalam", "Telugu", "Kannada", "English", "Spanish", "Arabic"];

function getInitials(name: string | undefined): string {
  if (!name) return "??";
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  return name.slice(0, 2).toUpperCase();
}

function displayGoal(goal: string | null | undefined) {
  if (!goal) return "Daily conversation";
  const map: Record<string, string> = {
    academic: "Academic writing",
    casual: "Daily conversation",
    professional: "Business emails",
  };
  return map[goal] ?? goal;
}

function cefrFromAverage(score: number) {
  if (score >= 8) return "C1";
  if (score >= 6.5) return "B2";
  if (score >= 4) return "B1";
  if (score >= 2.5) return "A2";
  return "A1";
}

function subLevelFromScores(scores: SkillScoreSnapshot[]) {
  if (!scores.length) return 4;
  const avg = scores.reduce((sum, score) => sum + score.score, 0) / scores.length;
  return Math.max(1, Math.min(10, Math.round(avg)));
}

function memberSince(createdAt: string | undefined) {
  if (!createdAt) return "Member since May 2026";
  const value = new Intl.DateTimeFormat("en", { month: "long", year: "numeric" }).format(new Date(createdAt));
  return `Member since ${value}`;
}

export default function ProfilePage() {
  return (
    <Suspense fallback={null}>
      <ProfilePageInner />
    </Suspense>
  );
}

function ProfilePageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();
  const { isReady } = useRequireAuth();
  const [activeTab, setActiveTab] = useState<ProfileTab>("edit");

  const userQuery = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  const statsQuery = useQuery({
    queryKey: ["progress-stats"],
    queryFn: () => progressApi.getStats(),
    enabled: isReady && !!userQuery.data?.diagnosis_completed,
  });

  const updateMutation = useMutation({
    mutationFn: authApi.updateMe,
    onSuccess: (user) => {
      queryClient.setQueryData(["me"], user);
    },
  });
  const googleRelinkMutation = useMutation({
    mutationFn: authApi.googleRelinkUrl,
    onSuccess: (result) => {
      window.location.href = result.auth_url;
    },
  });

  useEffect(() => {
    if (userQuery.data && !userQuery.data.diagnosis_completed) router.replace("/diagnosis");
  }, [userQuery.data, router]);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!isReady) return null;

  const user = userQuery.data;
  const oauthError = searchParams.get("error");
  const scores = statsQuery.data?.skill_scores ?? [];
  const subLevel = subLevelFromScores(scores);
  const avgScore = scores.length ? scores.reduce((sum, score) => sum + score.score, 0) / scores.length : 4;

  return (
    <div style={pageShellStyle}>
      <link
        rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"
      />
      <DashboardLayout
        user={user}
        onSignOut={handleLogout}
        mainStyle={{ maxWidth: 1120, margin: "0 auto", padding: "36px 20px 76px" }}
      >
        <div style={{ display: "grid", gridTemplateColumns: "240px minmax(0, 1fr)", gap: 28, alignItems: "start" }}>
          <ProfileSidebar
            activeTab={activeTab}
            cefr={cefrFromAverage(avgScore)}
            memberSince={memberSince(user?.created_at)}
            name={user?.name ?? "Your profile"}
            onTabChange={setActiveTab}
            subLevel={subLevel}
          />

          <section>
            {oauthError && <OAuthErrorBanner error={oauthError} />}
            {activeTab === "edit" && (
              <EditProfileSection
                key={
                  user
                    ? `edit-${user.id}-${user.email}-${user.display_name}-${user.phone_number}-${user.country}-${user.native_language}-${user.goal ?? ""}-${user.primary_goals.join("|")}`
                    : "edit-loading"
                }
                isSaving={updateMutation.isPending}
                isChangingEmail={updateMutation.isPending}
                isStartingGoogleRelink={googleRelinkMutation.isPending}
                onConfirmEmail={(payload) => updateMutation.mutateAsync(payload)}
                onSave={(payload) => updateMutation.mutate(payload)}
                onStartGoogleRelink={() => googleRelinkMutation.mutate()}
                user={user}
              />
            )}
            {activeTab === "personalisation" && (
              <PersonalisationSection
                key={user ? `personalisation-${user.id}-${user.personalisation_context}` : "personalisation-loading"}
                isSaving={updateMutation.isPending}
                onSave={(personalisation_context) => updateMutation.mutate({ personalisation_context })}
                user={user}
              />
            )}
            {activeTab === "diagnosis" && <DiagnosisSection scores={scores} />}
          </section>
        </div>
      </DashboardLayout>
    </div>
  );
}

function OAuthErrorBanner({ error }: { error: string }) {
  const message =
    error === "google_account_in_use"
      ? "That Google account is already connected to another LingosAI profile."
      : error === "email_in_use"
        ? "That email is already registered on another LingosAI profile."
        : "Google re-auth could not update your email. Please try again.";

  return (
    <div style={oauthErrorBannerStyle}>
      <AlertTriangle size={17} style={{ flexShrink: 0 }} />
      <span>{message}</span>
    </div>
  );
}

function ProfileSidebar({
  activeTab,
  cefr,
  memberSince,
  name,
  onTabChange,
  subLevel,
}: {
  activeTab: ProfileTab;
  cefr: string;
  memberSince: string;
  name: string;
  onTabChange: (tab: ProfileTab) => void;
  subLevel: number;
}) {
  const navItems = [
    { id: "edit" as const, label: "Edit Profile", icon: UserRound },
    { id: "personalisation" as const, label: "Personalisation", icon: Sparkles },
    { id: "diagnosis" as const, label: "Diagnosis", icon: ClipboardList },
  ];

  return (
    <aside style={sidebarStyle}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", textAlign: "center" }}>
        <div style={avatarStyle}>{getInitials(name)}</div>
        <h2 style={{ margin: "12px 0 8px", color: "oklch(15% 0.09 245)", fontSize: 18, fontWeight: 800 }}>
          {name}
        </h2>
        <span style={levelPillStyle}>Sub-level {subLevel} · {cefr}</span>
      </div>

      <Divider />

      <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onTabChange(item.id)}
              style={{
                ...sidebarNavStyle,
                background: active ? "oklch(92% 0.035 245)" : "transparent",
                color: active ? "oklch(42% 0.14 240)" : "oklch(35% 0.07 240)",
              }}
              onMouseEnter={(e) => {
                if (!active) e.currentTarget.style.background = "oklch(96% 0.01 245)";
              }}
              onMouseLeave={(e) => {
                if (!active) e.currentTarget.style.background = "transparent";
              }}
            >
              <Icon size={16} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <Divider />
      <p style={{ margin: 0, color: "oklch(55% 0.045 240)", fontSize: 12, lineHeight: 1.5 }}>{memberSince}</p>
    </aside>
  );
}

function EditProfileSection({
  isChangingEmail,
  isSaving,
  isStartingGoogleRelink,
  onConfirmEmail,
  onSave,
  onStartGoogleRelink,
  user,
}: {
  isChangingEmail: boolean;
  isSaving: boolean;
  isStartingGoogleRelink: boolean;
  onConfirmEmail: (payload: UserUpdateInput) => Promise<UserOut>;
  onSave: (payload: UserUpdateInput) => void;
  onStartGoogleRelink: () => void;
  user: UserOut | undefined;
}) {
  const [displayName, setDisplayName] = useState(user?.display_name ?? user?.name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [password, setPassword] = useState("");
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [oauthModalOpen, setOauthModalOpen] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [phone, setPhone] = useState(user?.phone_number ?? "");
  const [country, setCountry] = useState(user?.country ?? "");
  const [nativeLanguage, setNativeLanguage] = useState(user?.native_language ?? "");
  // Pre-select the goal chosen at signup (stored on `goal`) until the learner
  // edits their multi-select `primary_goals`. The three signup goals map onto
  // GOAL_OPTIONS pills, so the seeded goal renders highlighted.
  const seededGoals =
    user?.primary_goals && user.primary_goals.length > 0
      ? user.primary_goals
      : user?.goal
        ? [displayGoal(user.goal)]
        : [];
  const [goals, setGoals] = useState<string[]>(seededGoals);

  function resetDraft() {
    setDisplayName(user?.display_name ?? user?.name ?? "");
    setEmail(user?.email ?? "");
    setPassword("");
    setEmailError("");
    setEmailModalOpen(false);
    setOauthModalOpen(false);
    setPhone(user?.phone_number ?? "");
    setCountry(user?.country ?? "");
    setNativeLanguage(user?.native_language ?? "");
    setGoals(seededGoals);
  }

  function toggleGoal(goal: string) {
    setGoals((current) => current.includes(goal) ? current.filter((item) => item !== goal) : [...current, goal]);
  }

  const emailChanged = email.trim().toLowerCase() !== (user?.email ?? "").toLowerCase();
  const isGoogleAccount = user?.auth_provider === "google";

  async function confirmPasswordEmailChange() {
    setEmailError("");
    try {
      await onConfirmEmail({ email, password });
      setPassword("");
      setEmailModalOpen(false);
    } catch (error) {
      const message =
        error && typeof error === "object" && "response" in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setEmailError(message ?? "Could not change email. Check your password and try again.");
    }
  }

  return (
    <div style={contentCardStyle}>
      <PageHeader eyebrow="ACCOUNT DETAILS" title="Edit Profile" copy="Update your name, contact info and preferences." />
      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <CardInput label="Display name" value={displayName} onChange={setDisplayName} />
        <EmailChangeField
          email={email}
          emailChanged={emailChanged}
          isGoogleAccount={isGoogleAccount}
          onChange={setEmail}
          onOpenConfirm={() => setEmailModalOpen(true)}
          onOpenOauth={() => setOauthModalOpen(true)}
        />
        <CardInput label="Phone number" value={phone} onChange={setPhone} placeholder="Optional" />
        <CardSelect icon={<Globe2 size={16} />} label="Country" options={COUNTRY_OPTIONS} value={country} onChange={setCountry} />
        <CardSelect icon={<Languages size={16} />} label="Native language" options={LANGUAGE_OPTIONS} value={nativeLanguage} onChange={setNativeLanguage} />

        <div style={fieldCardStyle}>
          <label style={fieldLabelStyle}>Primary goal</label>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 10 }}>
            {GOAL_OPTIONS.map((goal) => {
              const selected = goals.includes(goal);
              return (
                <button
                  key={goal}
                  type="button"
                  onClick={() => toggleGoal(goal)}
                  style={{
                    border: selected ? "1px solid oklch(52% 0.18 240)" : "1px solid rgba(80,120,200,0.14)",
                    borderRadius: 999,
                    background: selected ? "oklch(92% 0.035 245)" : "rgba(255,255,255,0.72)",
                    color: selected ? "oklch(42% 0.14 240)" : "oklch(38% 0.07 240)",
                    cursor: "pointer",
                    fontFamily: "inherit",
                    fontSize: 13,
                    fontWeight: 700,
                    padding: "8px 12px",
                  }}
                >
                  {goal}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <ActionRow
        primaryLabel={isSaving ? "Saving..." : "Save changes"}
        onPrimary={() => onSave({
          display_name: displayName,
          phone_number: phone,
          country,
          native_language: nativeLanguage,
          primary_goals: goals,
        })}
        onSecondary={resetDraft}
        secondaryLabel="Cancel"
      />

      {emailModalOpen && (
        <Modal onClose={() => setEmailModalOpen(false)} title="Confirm email change">
          <p style={modalCopyStyle}>
            You are changing your email to <strong>{email}</strong>. Enter your password to confirm this is really you.
          </p>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            style={inputStyle}
          />
          {emailError && <p style={{ margin: "10px 0 0", color: "oklch(48% 0.18 28)", fontSize: 12 }}>{emailError}</p>}
          <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
            <button type="button" onClick={confirmPasswordEmailChange} style={primaryButtonStyle}>
              {isChangingEmail ? "Confirming..." : "Confirm"}
            </button>
            <button type="button" onClick={() => setEmailModalOpen(false)} style={ghostButtonStyle}>
              Cancel
            </button>
          </div>
        </Modal>
      )}

      {oauthModalOpen && (
        <Modal onClose={() => setOauthModalOpen(false)} title="Change Google account">
          <p style={modalCopyStyle}>
            This account signs in with Google. To change the email, re-authenticate with the Google account you want to use for this profile.
          </p>
          <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
            <button type="button" onClick={onStartGoogleRelink} style={primaryButtonStyle}>
              {isStartingGoogleRelink ? "Opening Google..." : "Re-auth with Google"}
            </button>
            <button type="button" onClick={() => setOauthModalOpen(false)} style={ghostButtonStyle}>
              Cancel
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

function EmailChangeField({
  email,
  emailChanged,
  isGoogleAccount,
  onChange,
  onOpenConfirm,
  onOpenOauth,
}: {
  email: string;
  emailChanged: boolean;
  isGoogleAccount: boolean;
  onChange: (value: string) => void;
  onOpenConfirm: () => void;
  onOpenOauth: () => void;
}) {
  return (
    <div style={fieldCardStyle}>
      <label style={fieldLabelStyle}>Email</label>
      <div style={{ position: "relative" }}>
        {emailChanged && !isGoogleAccount && (
          <button
            type="button"
            aria-label="Confirm email change"
            onClick={onOpenConfirm}
            style={emailArrowButtonStyle}
          >
            <ArrowRight size={18} />
          </button>
        )}
        <input
          readOnly={isGoogleAccount}
          value={email}
          onClick={() => {
            if (isGoogleAccount) onOpenOauth();
          }}
          onChange={(event) => onChange(event.target.value)}
          style={{
            ...inputStyle,
            cursor: isGoogleAccount ? "pointer" : "text",
          }}
        />
      </div>
    </div>
  );
}

function PersonalisationSection({
  isSaving,
  onSave,
  user,
}: {
  isSaving: boolean;
  onSave: (context: string) => void;
  user: UserOut | undefined;
}) {
  const [context, setContext] = useState(user?.personalisation_context ?? "");

  return (
    <div style={contentCardStyle}>
      <PageHeader
        eyebrow="PERSONALISATION"
        title="Context for better tasks"
        copy="Tell the AI about yourself so your tasks feel relevant to your real life."
      />
      <div style={fieldCardStyle}>
        <textarea
          maxLength={500}
          minLength={0}
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder={'Example: "I am a software engineer at a startup. I often need to write emails to international clients and speak in daily standups. My biggest fear is not sounding confident in meetings."'}
          style={{
            width: "100%",
            minHeight: 180,
            resize: "vertical",
            border: "none",
            outline: "none",
            background: "transparent",
            color: "oklch(22% 0.08 245)",
            fontFamily: "inherit",
            fontSize: 14,
            lineHeight: 1.65,
          }}
        />
        <div style={{ marginTop: 10, textAlign: "right", color: "oklch(55% 0.045 240)", fontSize: 12 }}>
          {context.length}/500
        </div>
      </div>
      <ActionRow primaryLabel={isSaving ? "Saving..." : "Save context"} onPrimary={() => onSave(context)} />
      <div style={infoBoxStyle}>
        <Info size={17} style={{ flexShrink: 0 }} />
        <span>
          This text is sent to the AI when generating your tasks. Be specific — the more detail you give, the more relevant your tasks will be.
        </span>
      </div>
    </div>
  );
}

function DiagnosisSection({ scores }: { scores: SkillScoreSnapshot[] }) {
  // Match each canonical sub-skill by its exact backend `skill_name` and render
  // the server `display_label` (falling back to the shared label table). This is
  // what makes "Thought Organization" (expression) and "Listening"
  // (comprehension) resolve to their real scores instead of 0.
  const skillRows = useMemo(() => {
    return SKILL_ORDER.map((key) => {
      const match = scores.find((score) => score.skill_name === key);
      return { label: match?.display_label ?? getSkillLabel(key), value: match?.score ?? 0 };
    });
  }, [scores]);

  const sorted = [...skillRows].sort((a, b) => b.value - a.value);
  const strongest = sorted[0]?.label ?? "No data yet";
  const weakest = [...skillRows].sort((a, b) => a.value - b.value)[0]?.label ?? "No data yet";

  return (
    <div style={contentCardStyle}>
      <PageHeader eyebrow="YOUR BASELINE" title="Initial diagnosis" copy="Your starting point — this is where your journey began." />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 12 }}>
        <SnapshotTile label="Starting CEFR level" value={cefrFromAverage(scores.length ? scores.reduce((sum, score) => sum + score.score, 0) / scores.length : 4)} />
        <SnapshotTile label="Strongest skill at start" value={strongest} />
        <SnapshotTile label="Weakest skill at start" value={weakest} />
      </div>

      <div style={{ marginTop: 28 }}>
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ margin: 0, color: "oklch(18% 0.09 245)", fontSize: 17, fontWeight: 800 }}>Current scores</h3>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {skillRows.map((row) => <SkillScoreBar key={row.label} {...row} />)}
        </div>
      </div>
    </div>
  );
}

function PageHeader({ copy, eyebrow, title }: { copy: string; eyebrow: string; title: string }) {
  return (
    <header style={{ marginBottom: 26 }}>
      <div style={{ color: "oklch(48% 0.14 240)", fontSize: 12, fontWeight: 800, letterSpacing: 1.2 }}>{eyebrow}</div>
      <h1 style={{ margin: "8px 0 6px", color: "oklch(15% 0.09 245)", fontSize: 32, fontWeight: 800, letterSpacing: 0 }}>
        {title}
      </h1>
      <p style={{ margin: 0, color: "oklch(48% 0.06 240)", fontSize: 15, lineHeight: 1.6 }}>{copy}</p>
    </header>
  );
}

function CardInput({
  label,
  note,
  onChange,
  placeholder,
  readOnly,
  value,
}: {
  label: string;
  note?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  readOnly?: boolean;
  value: string;
}) {
  return (
    <div style={fieldCardStyle}>
      <label style={fieldLabelStyle}>{label}</label>
      <input
        readOnly={readOnly}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange?.(e.target.value)}
        style={{
          ...inputStyle,
          background: readOnly ? "oklch(95% 0.01 245)" : inputStyle.background,
          color: readOnly ? "oklch(50% 0.045 240)" : inputStyle.color,
          cursor: readOnly ? "not-allowed" : "text",
        }}
      />
      {note && <p style={{ margin: "8px 0 0", color: "oklch(50% 0.055 240)", fontSize: 12 }}>{note}</p>}
    </div>
  );
}

function CardSelect({
  icon,
  label,
  onChange,
  options,
  value,
}: {
  icon: ReactNode;
  label: string;
  onChange: (value: string) => void;
  options: string[];
  value: string;
}) {
  return (
    <div style={fieldCardStyle}>
      <label style={fieldLabelStyle}>{label}</label>
      <div style={{ display: "flex", alignItems: "center", gap: 10, position: "relative" }}>
        <span style={{ color: "oklch(45% 0.12 240)" }}>{icon}</span>
        <select value={value} onChange={(e) => onChange(e.target.value)} style={inputStyle}>
          <option value="">Select</option>
          {options.map((option) => <option key={option} value={option}>{option}</option>)}
        </select>
      </div>
    </div>
  );
}

function ActionRow({
  onPrimary,
  onSecondary,
  primaryLabel,
  secondaryLabel,
}: {
  onPrimary: () => void;
  onSecondary?: () => void;
  primaryLabel: string;
  secondaryLabel?: string;
}) {
  return (
    <div style={{ display: "flex", gap: 12, marginTop: 24 }}>
      <button type="button" onClick={onPrimary} style={primaryButtonStyle}>{primaryLabel}</button>
      {secondaryLabel && (
        <button type="button" onClick={onSecondary} style={ghostButtonStyle}>{secondaryLabel}</button>
      )}
    </div>
  );
}

function Modal({
  children,
  onClose,
  title,
}: {
  children: ReactNode;
  onClose: () => void;
  title: string;
}) {
  return (
    <div style={modalBackdropStyle}>
      <div style={modalPanelStyle} role="dialog" aria-modal="true" aria-label={title}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
          <h2 style={{ margin: 0, color: "oklch(15% 0.09 245)", fontSize: 20, fontWeight: 800 }}>
            {title}
          </h2>
          <button type="button" aria-label="Close dialog" onClick={onClose} style={iconButtonStyle}>
            <X size={18} />
          </button>
        </div>
        <div style={{ marginTop: 14 }}>{children}</div>
      </div>
    </div>
  );
}

function SnapshotTile({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ borderRadius: 8, background: "oklch(94% 0.025 245)", border: "1px solid rgba(80,120,200,0.1)", padding: 16 }}>
      <div style={{ color: "oklch(55% 0.05 240)", fontSize: 12, fontWeight: 700 }}>{label}</div>
      <div style={{ marginTop: 8, color: "oklch(18% 0.09 245)", fontSize: 20, fontWeight: 800 }}>{value}</div>
    </div>
  );
}

function SkillScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, marginBottom: 7 }}>
        <span style={{ color: "oklch(30% 0.07 240)", fontSize: 13, fontWeight: 750 }}>{label}</span>
        <span style={{ color: "oklch(48% 0.06 240)", fontSize: 12 }}>{value.toFixed(1)}</span>
      </div>
      <div style={{ position: "relative", height: 11, borderRadius: 999, background: "oklch(92% 0.018 245)", overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, width: `${Math.min(value * 10, 100)}%`, background: "oklch(52% 0.18 240)", borderRadius: 999 }} />
      </div>
    </div>
  );
}

function Divider() {
  return <div style={{ height: 1, background: "rgba(80,120,200,0.12)", margin: "22px 0" }} />;
}

const pageShellStyle: CSSProperties = {
  minHeight: "100vh",
  fontFamily: "'Plus Jakarta Sans', sans-serif",
  background: "radial-gradient(ellipse 80% 60% at 50% 0%, oklch(86% 0.07 240) 0%, oklch(90% 0.045 245) 50%, oklch(93% 0.025 250) 100%)",
};

const sidebarStyle: CSSProperties = {
  background: "rgba(255,255,255,0.86)",
  border: "1px solid rgba(255,255,255,0.9)",
  borderRadius: 8,
  boxShadow: "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
  padding: 20,
};

const avatarStyle: CSSProperties = {
  width: 64,
  height: 64,
  borderRadius: "50%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "oklch(52% 0.18 240)",
  color: "white",
  fontSize: 20,
  fontWeight: 800,
};

const levelPillStyle: CSSProperties = {
  borderRadius: 999,
  background: "oklch(92% 0.035 245)",
  color: "oklch(42% 0.14 240)",
  fontSize: 12,
  fontWeight: 800,
  padding: "6px 10px",
};

const sidebarNavStyle: CSSProperties = {
  width: "100%",
  minHeight: 40,
  display: "flex",
  alignItems: "center",
  gap: 10,
  border: "none",
  borderRadius: 999,
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 750,
  padding: "10px 13px",
  textAlign: "left",
  transition: "background 0.15s ease",
};

const contentCardStyle: CSSProperties = {
  background: "rgba(255,255,255,0.86)",
  border: "1px solid rgba(255,255,255,0.9)",
  borderRadius: 8,
  boxShadow: "0 4px 32px rgba(80,110,180,0.1), 0 1.5px 6px rgba(80,120,200,0.05)",
  padding: 30,
};

const fieldCardStyle: CSSProperties = {
  borderRadius: 8,
  background: "oklch(96% 0.012 245)",
  border: "1px solid rgba(80,120,200,0.16)",
  padding: "14px 15px",
};

const emailArrowButtonStyle: CSSProperties = {
  position: "absolute",
  left: -48,
  top: "50%",
  transform: "translateY(-50%)",
  width: 36,
  height: 36,
  border: "1px solid rgba(80,120,200,0.18)",
  borderRadius: "50%",
  background: "oklch(52% 0.18 240)",
  color: "white",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  boxShadow: "0 8px 20px rgba(55,95,180,0.18)",
};

const modalBackdropStyle: CSSProperties = {
  position: "fixed",
  inset: 0,
  zIndex: 100,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "rgba(10, 20, 40, 0.34)",
  padding: 20,
};

const modalPanelStyle: CSSProperties = {
  width: "min(460px, 100%)",
  borderRadius: 8,
  background: "white",
  border: "1px solid rgba(80,120,200,0.14)",
  boxShadow: "0 24px 70px rgba(20,40,90,0.22)",
  padding: 22,
};

const iconButtonStyle: CSSProperties = {
  width: 34,
  height: 34,
  border: "1px solid rgba(80,120,200,0.14)",
  borderRadius: "50%",
  background: "oklch(96% 0.012 245)",
  color: "oklch(38% 0.07 240)",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const modalCopyStyle: CSSProperties = {
  margin: "0 0 14px",
  color: "oklch(42% 0.06 240)",
  fontSize: 14,
  lineHeight: 1.6,
};

const fieldLabelStyle: CSSProperties = {
  display: "block",
  color: "oklch(45% 0.07 240)",
  fontSize: 12,
  fontWeight: 800,
  marginBottom: 6,
};

const inputStyle: CSSProperties = {
  width: "100%",
  minHeight: 44,
  border: "1px solid rgba(80,120,200,0.22)",
  borderRadius: 8,
  outline: "none",
  background: "white",
  color: "oklch(22% 0.08 245)",
  fontFamily: "inherit",
  fontSize: 15,
  fontWeight: 650,
  padding: "10px 12px",
  boxShadow: "inset 0 1px 2px rgba(55,75,130,0.04)",
};

const primaryButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  minHeight: 42,
  border: "none",
  borderRadius: 8,
  background: "oklch(52% 0.18 240)",
  color: "white",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 800,
  padding: "11px 18px",
};

const ghostButtonStyle: CSSProperties = {
  ...primaryButtonStyle,
  border: "1px solid rgba(80,120,200,0.16)",
  background: "rgba(255,255,255,0.46)",
  color: "oklch(42% 0.1 240)",
};

const infoBoxStyle: CSSProperties = {
  display: "flex",
  gap: 10,
  marginTop: 18,
  borderRadius: 8,
  background: "oklch(94% 0.025 245)",
  color: "oklch(38% 0.08 240)",
  fontSize: 13,
  lineHeight: 1.55,
  padding: 14,
};

const oauthErrorBannerStyle: CSSProperties = {
  display: "flex",
  gap: 10,
  marginBottom: 16,
  borderRadius: 8,
  background: "oklch(95% 0.06 88)",
  color: "oklch(42% 0.12 70)",
  fontSize: 13,
  fontWeight: 700,
  lineHeight: 1.55,
  padding: 14,
};
