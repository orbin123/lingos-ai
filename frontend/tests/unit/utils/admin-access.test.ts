import { describe, expect, it } from "vitest";

import {
  ADMIN_NAV_ITEMS,
  canAccessAdmin,
  canManageRoles,
  canManageSubscriptions,
  getUserRoles,
  isSuperAdmin,
  shouldShowAdminConsoleButton,
} from "@/lib/admin-access";

// Migrated from tests/admin-access.test.mjs. The old test transpiled the
// source in a vm and snapshotted a STALE label list; importing the real module
// keeps this honest — if the nav model changes, this fails loudly.
describe("ADMIN_NAV_ITEMS", () => {
  it("lists the admin navigation labels in display order", () => {
    expect(ADMIN_NAV_ITEMS.map((item) => item.label)).toEqual([
      "Dashboard",
      "Users",
      "User Progress",
      "Payments",
      "Subscribers",
      "AI Logs",
      "AI Quality",
      "AI Costs",
      "Feedback Analytics",
      "User Reviews",
      "Blog",
      "Audit Logs",
      "Roles & Permissions",
    ]);
  });

  it("marks only Roles & Permissions as super-admin-only", () => {
    const superAdminOnly = ADMIN_NAV_ITEMS.filter(
      (item) => (item as { superAdminOnly?: boolean }).superAdminOnly === true,
    ).map((item) => item.label);
    expect(superAdminOnly).toEqual(["Roles & Permissions"]);
  });
});

describe("role derivation", () => {
  it("prefers the explicit roles array", () => {
    expect(getUserRoles({ roles: ["admin", "learner"] })).toEqual([
      "admin",
      "learner",
    ]);
  });

  it("falls back to super_admin when is_superuser is set", () => {
    expect(getUserRoles({ is_superuser: true })).toEqual(["super_admin"]);
  });

  it("falls back to the single role field", () => {
    expect(getUserRoles({ role: "admin" })).toEqual(["admin"]);
  });

  it("returns no roles for a null user", () => {
    expect(getUserRoles(null)).toEqual([]);
    expect(getUserRoles(undefined)).toEqual([]);
  });
});

describe("access checks", () => {
  it("hides the admin console button from learners", () => {
    expect(
      shouldShowAdminConsoleButton({
        role: "learner",
        roles: ["learner"],
        is_superuser: false,
      }),
    ).toBe(false);
  });

  it("grants admin surfaces to admin and super_admin", () => {
    expect(canAccessAdmin({ roles: ["admin"] })).toBe(true);
    expect(canAccessAdmin({ roles: ["super_admin"] })).toBe(true);
    expect(canAccessAdmin({ roles: ["learner"] })).toBe(false);
  });

  it("limits role + subscription management to super admins", () => {
    expect(canManageRoles({ roles: ["admin"] })).toBe(false);
    expect(canManageRoles({ roles: ["super_admin"] })).toBe(true);
    expect(canManageSubscriptions({ roles: ["admin"] })).toBe(false);
    expect(canManageSubscriptions({ is_superuser: true })).toBe(true);
  });

  it("treats is_superuser as super admin", () => {
    expect(isSuperAdmin({ is_superuser: true })).toBe(true);
    expect(isSuperAdmin({ roles: ["admin"] })).toBe(false);
  });
});
