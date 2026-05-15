"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, Power } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminButton,
  AdminPanel,
  RolePill,
  StatusPill,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi } from "@/lib/admin-api";

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const usersQuery = useQuery({
    queryKey: ["admin", "users"],
    queryFn: adminApi.users,
  });
  const statusMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: number; isActive: boolean }) =>
      adminApi.updateUserStatus(userId, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "summary"] });
    },
  });

  const users = usersQuery.data ?? [];

  return (
    <AdminLayout title="Users" eyebrow="User management">
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Name</th>
              <th style={thStyle}>Email</th>
              <th style={thStyle}>Role</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Created</th>
              <th style={thStyle}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td style={tdStyle}>
                  <div style={nameStyle}>{user.name}</div>
                </td>
                <td style={tdStyle}>{user.email}</td>
                <td style={tdStyle}>
                  <RolePill role={user.role} />
                </td>
                <td style={tdStyle}>
                  <StatusPill active={user.is_active} />
                </td>
                <td style={tdStyle}>{formatAdminDate(user.created_at)}</td>
                <td style={tdStyle}>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <Link href={`/admin/users/${user.id}`} style={viewLinkStyle}>
                      <Eye size={15} />
                      View details
                    </Link>
                    <AdminButton
                      tone="secondary"
                      disabled={statusMutation.isPending}
                      onClick={() =>
                        statusMutation.mutate({
                          userId: user.id,
                          isActive: !user.is_active,
                        })
                      }
                    >
                      <Power size={15} />
                      {user.is_active ? "Deactivate" : "Activate"}
                    </AdminButton>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

const nameStyle: CSSProperties = {
  color: "oklch(18% 0.055 245)",
  fontWeight: 800,
};

const viewLinkStyle: CSSProperties = {
  minHeight: 38,
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  borderRadius: 8,
  padding: "0 13px",
  background: "#0070C4",
  color: "white",
  textDecoration: "none",
  fontSize: 13,
  fontWeight: 800,
};
