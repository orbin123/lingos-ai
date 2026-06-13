"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { CSSProperties, ReactNode } from "react";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  BarChart3,
  Bot,
  CreditCard,
  LayoutDashboard,
  ListChecks,
  LogOut,
  Newspaper,
  Repeat,
  ShieldCheck,
  Star,
  ThumbsUp,
  TrendingUp,
  Users,
} from "lucide-react";

import { ADMIN_NAV_ITEMS, canAccessAdmin, canManageRoles } from "@/lib/admin-access";
import { authApi } from "@/lib/auth-api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useAuthStore } from "@/store/authStore";

const NAV_ICONS: Record<string, ReactNode> = {
  Dashboard: <LayoutDashboard size={18} />,
  Users: <Users size={18} />,
  "User Progress": <TrendingUp size={18} />,
  Payments: <CreditCard size={18} />,
  Subscribers: <Repeat size={18} />,
  "AI Logs": <Bot size={18} />,
  "AI Quality": <BarChart3 size={18} />,
  "Feedback Analytics": <ThumbsUp size={18} />,
  "User Reviews": <Star size={18} />,
  Blog: <Newspaper size={18} />,
  "Audit Logs": <ListChecks size={18} />,
  "Roles & Permissions": <ShieldCheck size={18} />,
};

interface AdminLayoutProps {
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
  superAdminOnly?: boolean;
  children: ReactNode;
}

export function AdminLayout({
  title,
  eyebrow,
  actions,
  superAdminOnly,
  children,
}: AdminLayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isReady } = useRequireAuth();
  const logout = useAuthStore((s) => s.logout);

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled: isReady,
  });

  useEffect(() => {
    if (user && !canAccessAdmin(user)) {
      router.replace("/dashboard");
    }
    if (user && superAdminOnly && !canManageRoles(user)) {
      router.replace("/admin");
    }
  }, [router, superAdminOnly, user]);

  const handleLogout = () => {
    logout();
    router.replace("/login");
  };

  if (
    !isReady ||
    isLoading ||
    !user ||
    !canAccessAdmin(user) ||
    (superAdminOnly && !canManageRoles(user))
  ) {
    return (
      <main style={loadingStyle}>
        <p>Checking admin access...</p>
      </main>
    );
  }

  return (
    <div style={shellStyle}>
      <aside style={sidebarStyle}>
        <div style={brandStyle}>
          <div style={brandMarkStyle}>A</div>
          <div>
            <div style={brandNameStyle}>Admin Console</div>
            <div style={brandMetaStyle}>{user.role.replace("_", " ")}</div>
          </div>
        </div>

        <nav style={navStyle} aria-label="Admin navigation">
          {ADMIN_NAV_ITEMS.filter(
            (item) => !("superAdminOnly" in item) || canManageRoles(user),
          ).map((item) => {
            const active =
              item.href === "/admin"
                ? pathname === "/admin"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  ...navItemStyle,
                  ...(active ? navItemActiveStyle : null),
                }}
              >
                {NAV_ICONS[item.label]}
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div style={footerStyle}>
          <Link href="/dashboard" style={backToAppStyle}>
            <ArrowLeft size={17} />
            Back to app
          </Link>
          <button type="button" onClick={handleLogout} style={logoutStyle}>
            <LogOut size={17} />
            Sign out
          </button>
        </div>
      </aside>

      <main style={mainStyle}>
        <header style={headerStyle}>
          <div>
            {eyebrow && <div style={eyebrowStyle}>{eyebrow}</div>}
            <h1 style={titleStyle}>{title}</h1>
          </div>
          {actions && <div style={actionsStyle}>{actions}</div>}
        </header>
        {children}
      </main>
    </div>
  );
}

const loadingStyle: CSSProperties = {
  minHeight: "100vh",
  display: "grid",
  placeItems: "center",
  background: "oklch(96% 0.01 240)",
  color: "oklch(36% 0.06 245)",
  fontFamily: "Inter, system-ui, sans-serif",
  fontWeight: 650,
};

const shellStyle: CSSProperties = {
  minHeight: "100vh",
  display: "grid",
  gridTemplateColumns: "260px minmax(0, 1fr)",
  background: "oklch(96% 0.012 245)",
  color: "oklch(18% 0.055 245)",
  fontFamily: "Inter, system-ui, sans-serif",
};

const sidebarStyle: CSSProperties = {
  position: "sticky",
  top: 0,
  height: "100vh",
  display: "flex",
  flexDirection: "column",
  gap: 18,
  padding: 22,
  background: "white",
  borderRight: "1px solid oklch(88% 0.018 245)",
};

const brandStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  paddingBottom: 18,
  borderBottom: "1px solid oklch(91% 0.014 245)",
};

const brandMarkStyle: CSSProperties = {
  width: 38,
  height: 38,
  borderRadius: 8,
  display: "grid",
  placeItems: "center",
  background: "#0070C4",
  color: "white",
  fontWeight: 800,
};

const brandNameStyle: CSSProperties = {
  fontSize: 15,
  fontWeight: 800,
};

const brandMetaStyle: CSSProperties = {
  marginTop: 2,
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 650,
  textTransform: "capitalize",
};

const navStyle: CSSProperties = {
  display: "grid",
  gap: 6,
};

const navItemStyle: CSSProperties = {
  minHeight: 42,
  display: "flex",
  alignItems: "center",
  gap: 10,
  padding: "0 12px",
  borderRadius: 8,
  color: "oklch(35% 0.055 245)",
  textDecoration: "none",
  fontSize: 14,
  fontWeight: 700,
};

const navItemActiveStyle: CSSProperties = {
  background: "oklch(94% 0.04 240)",
  color: "#00599e",
};

const footerStyle: CSSProperties = {
  marginTop: "auto",
  display: "grid",
  gap: 8,
};

const backToAppStyle: CSSProperties = {
  minHeight: 42,
  display: "flex",
  alignItems: "center",
  gap: 10,
  border: "1px solid oklch(88% 0.018 245)",
  borderRadius: 8,
  background: "white",
  color: "oklch(35% 0.055 245)",
  padding: "0 12px",
  textDecoration: "none",
  fontSize: 14,
  fontWeight: 750,
};

const logoutStyle: CSSProperties = {
  minHeight: 42,
  display: "flex",
  alignItems: "center",
  gap: 10,
  border: "1px solid oklch(88% 0.018 245)",
  borderRadius: 8,
  background: "white",
  color: "oklch(45% 0.12 25)",
  padding: "0 12px",
  cursor: "pointer",
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 750,
};

const mainStyle: CSSProperties = {
  minWidth: 0,
  padding: "30px 34px 56px",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-end",
  gap: 18,
  marginBottom: 24,
};

const eyebrowStyle: CSSProperties = {
  color: "#0070C4",
  fontSize: 12,
  fontWeight: 800,
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  marginBottom: 6,
};

const titleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(18% 0.055 245)",
  fontSize: 28,
  fontWeight: 850,
  lineHeight: 1.15,
};

const actionsStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  flexWrap: "wrap",
  justifyContent: "flex-end",
};
