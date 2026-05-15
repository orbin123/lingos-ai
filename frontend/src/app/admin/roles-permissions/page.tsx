"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminButton,
  AdminPanel,
  RolePill,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import {
  adminApi,
  type AdminPermission,
  type AdminRole,
  type AdminUserListItem,
} from "@/lib/admin-api";

const ROLE_OPTIONS = ["learner", "admin", "super_admin"];

export default function AdminRolesPermissionsPage() {
  const queryClient = useQueryClient();
  const usersQuery = useQuery({ queryKey: ["admin", "users"], queryFn: adminApi.users });
  const rolesQuery = useQuery({ queryKey: ["admin", "roles"], queryFn: adminApi.roles });
  const permissionsQuery = useQuery({
    queryKey: ["admin", "permissions"],
    queryFn: adminApi.permissions,
  });

  const userRoleMutation = useMutation({
    mutationFn: ({ userId, roles }: { userId: number; roles: string[] }) =>
      adminApi.updateUserRoles(userId, { roles }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "roles"] });
    },
  });

  const rolePermissionMutation = useMutation({
    mutationFn: ({ roleId, permissionKeys }: { roleId: number; permissionKeys: string[] }) =>
      adminApi.updateRolePermissions(roleId, { permission_keys: permissionKeys }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "roles"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "permissions"] });
    },
  });

  const users = usersQuery.data ?? [];
  const roles = rolesQuery.data ?? [];
  const permissions = permissionsQuery.data ?? [];

  return (
    <AdminLayout
      title="Roles & Permissions"
      eyebrow="Super admin"
      superAdminOnly
    >
      <div style={pageGridStyle}>
        <AdminPanel style={{ overflow: "hidden" }}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>User</th>
                <th style={thStyle}>Current Roles</th>
                <th style={thStyle}>Assignment</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <UserRoleRow
                  key={`${user.id}-${user.roles.join("-")}`}
                  user={user}
                  isSaving={userRoleMutation.isPending}
                  onSave={(roles) => userRoleMutation.mutate({ userId: user.id, roles })}
                />
              ))}
              {users.length === 0 && (
                <tr>
                  <td style={tdStyle} colSpan={3}>
                    No users found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </AdminPanel>

        <div style={roleGridStyle}>
          {roles.map((role) => (
            <RolePermissionPanel
              key={`${role.id}-${role.permissions.join("-")}`}
              role={role}
              permissions={permissions}
              isSaving={rolePermissionMutation.isPending}
              onSave={(permissionKeys) =>
                rolePermissionMutation.mutate({
                  roleId: role.id,
                  permissionKeys,
                })
              }
            />
          ))}
        </div>
      </div>
    </AdminLayout>
  );
}

function UserRoleRow({
  user,
  isSaving,
  onSave,
}: {
  user: AdminUserListItem;
  isSaving: boolean;
  onSave: (roles: string[]) => void;
}) {
  const [selectedRoles, setSelectedRoles] = useState(() => new Set(user.roles));
  const selected = useMemo(() => Array.from(selectedRoles).sort(), [selectedRoles]);
  const changed = selected.join("|") !== [...user.roles].sort().join("|");

  const toggleRole = (role: string) => {
    setSelectedRoles((current) => {
      const next = new Set(current);
      if (next.has(role)) {
        next.delete(role);
      } else {
        next.add(role);
      }
      if (next.size === 0) next.add("learner");
      return next;
    });
  };

  return (
    <tr>
      <td style={tdStyle}>
        <div style={strongTextStyle}>{user.name}</div>
        <div style={mutedTextStyle}>{user.email}</div>
      </td>
      <td style={tdStyle}>
        <div style={pillRowStyle}>
          {user.roles.map((role) => (
            <RolePill key={role} role={role} />
          ))}
        </div>
      </td>
      <td style={tdStyle}>
        <div style={assignmentStyle}>
          {ROLE_OPTIONS.map((role) => (
            <label key={role} style={checkboxLabelStyle}>
              <input
                type="checkbox"
                checked={selectedRoles.has(role)}
                onChange={() => toggleRole(role)}
              />
              <span>{role.replace("_", " ")}</span>
            </label>
          ))}
          <AdminButton
            tone="secondary"
            disabled={!changed || isSaving}
            onClick={() => onSave(selected)}
          >
            <Save size={15} />
            Save
          </AdminButton>
        </div>
      </td>
    </tr>
  );
}

function RolePermissionPanel({
  role,
  permissions,
  isSaving,
  onSave,
}: {
  role: AdminRole;
  permissions: AdminPermission[];
  isSaving: boolean;
  onSave: (permissionKeys: string[]) => void;
}) {
  const [selectedKeys, setSelectedKeys] = useState(() => new Set(role.permissions));
  const selected = useMemo(() => Array.from(selectedKeys).sort(), [selectedKeys]);
  const changed = selected.join("|") !== [...role.permissions].sort().join("|");

  const togglePermission = (permissionKey: string) => {
    setSelectedKeys((current) => {
      const next = new Set(current);
      if (next.has(permissionKey)) {
        next.delete(permissionKey);
      } else {
        next.add(permissionKey);
      }
      return next;
    });
  };

  return (
    <AdminPanel style={{ padding: 18 }}>
      <div style={roleHeadStyle}>
        <div>
          <h2 style={roleTitleStyle}>{role.name.replace("_", " ")}</h2>
          <div style={mutedTextStyle}>{role.user_count} users</div>
        </div>
        <AdminButton
          tone="secondary"
          disabled={!changed || isSaving}
          onClick={() => onSave(selected)}
        >
          <Save size={15} />
          Save
        </AdminButton>
      </div>

      <div style={permissionGridStyle}>
        {permissions.map((permission) => (
          <label key={permission.key} style={permissionLabelStyle}>
            <input
              type="checkbox"
              checked={selectedKeys.has(permission.key)}
              onChange={() => togglePermission(permission.key)}
            />
            <span style={permissionTextStyle}>
              <strong style={permissionKeyStyle}>{permission.key}</strong>
              <small style={permissionDescriptionStyle}>{permission.description}</small>
            </span>
          </label>
        ))}
      </div>
    </AdminPanel>
  );
}

const pageGridStyle: CSSProperties = {
  display: "grid",
  gap: 18,
};

const roleGridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
  gap: 14,
};

const strongTextStyle: CSSProperties = {
  color: "oklch(18% 0.055 245)",
  fontWeight: 800,
};

const mutedTextStyle: CSSProperties = {
  marginTop: 3,
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 650,
};

const pillRowStyle: CSSProperties = {
  display: "flex",
  gap: 6,
  flexWrap: "wrap",
};

const assignmentStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
  flexWrap: "wrap",
};

const checkboxLabelStyle: CSSProperties = {
  minHeight: 34,
  display: "inline-flex",
  alignItems: "center",
  gap: 7,
  border: "1px solid oklch(88% 0.018 245)",
  borderRadius: 8,
  padding: "0 10px",
  color: "oklch(28% 0.06 245)",
  fontSize: 13,
  fontWeight: 750,
  textTransform: "capitalize",
};

const roleHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "flex-start",
  justifyContent: "space-between",
  gap: 12,
  marginBottom: 14,
};

const roleTitleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(18% 0.055 245)",
  fontSize: 17,
  fontWeight: 850,
  textTransform: "capitalize",
};

const permissionGridStyle: CSSProperties = {
  display: "grid",
  gap: 8,
};

const permissionLabelStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "18px minmax(0, 1fr)",
  gap: 9,
  alignItems: "start",
  border: "1px solid oklch(90% 0.014 245)",
  borderRadius: 8,
  padding: 10,
  color: "oklch(25% 0.055 245)",
  fontSize: 13,
  lineHeight: 1.35,
};

const permissionTextStyle: CSSProperties = {
  display: "grid",
  gap: 2,
};

const permissionKeyStyle: CSSProperties = {
  color: "oklch(20% 0.055 245)",
  fontWeight: 850,
};

const permissionDescriptionStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 600,
};
