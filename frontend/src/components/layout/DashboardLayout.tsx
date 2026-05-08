"use client";

import type { CSSProperties, ReactNode } from "react";
import type { UserOut } from "@/lib/auth-api";
import { LandingFooter } from "@/components/layout/LandingFooter";
import { Navbar } from "@/components/layout/Navbar";

interface DashboardLayoutProps {
  children: ReactNode;
  mainStyle?: CSSProperties;
  onSignOut?: () => void;
  user: UserOut | undefined;
}

export function DashboardLayout({
  children,
  mainStyle,
  onSignOut,
  user,
}: DashboardLayoutProps) {
  return (
    <>
      <Navbar user={user} onSignOut={onSignOut} />
      <main style={mainStyle}>{children}</main>
      <LandingFooter />
    </>
  );
}
