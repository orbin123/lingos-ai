export const ADMIN_ROLES = ["admin", "super_admin"] as const;

export const ADMIN_NAV_ITEMS = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/users", label: "Users" },
  { href: "/admin/user-progress", label: "User Progress" },
  { href: "/admin/payments", label: "Payments" },
  { href: "/admin/subscribers", label: "Subscribers" },
  { href: "/admin/ai-logs", label: "AI Logs" },
  { href: "/admin/ai-quality", label: "AI Quality" },
  { href: "/admin/ai-costs", label: "AI Costs" },
  { href: "/admin/feedback-analytics", label: "Feedback Analytics" },
  { href: "/admin/user-reviews", label: "User Reviews" },
  { href: "/admin/blog", label: "Blog" },
  { href: "/admin/audit-logs", label: "Audit Logs" },
  { href: "/admin/roles-permissions", label: "Roles & Permissions", superAdminOnly: true },
] as const;

export interface AdminCapableUser {
  role?: string | null;
  roles?: string[] | null;
  is_superuser?: boolean | null;
}

export function getUserRoles(user: AdminCapableUser | null | undefined): string[] {
  if (!user) return [];
  const explicitRoles = Array.isArray(user.roles) ? user.roles.filter(Boolean) : [];
  if (explicitRoles.length > 0) return explicitRoles;
  if (user.is_superuser) return ["super_admin"];
  return user.role ? [user.role] : [];
}

export function canAccessAdmin(user: AdminCapableUser | null | undefined): boolean {
  const roles = getUserRoles(user);
  return roles.some((role) => ADMIN_ROLES.includes(role as (typeof ADMIN_ROLES)[number]));
}

export function isSuperAdmin(user: AdminCapableUser | null | undefined): boolean {
  const roles = getUserRoles(user);
  return roles.includes("super_admin") || user?.is_superuser === true;
}

export function canManageRoles(user: AdminCapableUser | null | undefined): boolean {
  return isSuperAdmin(user);
}

export function canManageSubscriptions(user: AdminCapableUser | null | undefined): boolean {
  return isSuperAdmin(user);
}

export function shouldShowAdminConsoleButton(
  user: AdminCapableUser | null | undefined,
): boolean {
  return canAccessAdmin(user);
}
