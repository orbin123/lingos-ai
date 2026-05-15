"use client";

import type { CSSProperties } from "react";
import { useQuery } from "@tanstack/react-query";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminPanel,
  formatAdminDateTime,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi } from "@/lib/admin-api";

export default function AdminAuditLogsPage() {
  const auditQuery = useQuery({
    queryKey: ["admin", "audit-logs"],
    queryFn: adminApi.auditLogs,
  });
  const logs = auditQuery.data ?? [];

  return (
    <AdminLayout title="Audit Logs" eyebrow="Admin activity">
      <AdminPanel style={{ overflow: "hidden" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Admin</th>
              <th style={thStyle}>Action</th>
              <th style={thStyle}>Resource</th>
              <th style={thStyle}>Resource ID</th>
              <th style={thStyle}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td style={tdStyle}>
                  <div style={strongTextStyle}>{log.admin?.name ?? "Deleted admin"}</div>
                  <div style={mutedTextStyle}>{log.admin?.email ?? "No email"}</div>
                </td>
                <td style={tdStyle}>{log.action}</td>
                <td style={tdStyle}>{log.resource_type}</td>
                <td style={tdStyle}>{log.resource_id}</td>
                <td style={tdStyle}>{formatAdminDateTime(log.created_at)}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td style={tdStyle} colSpan={5}>
                  No audit logs found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </AdminPanel>
    </AdminLayout>
  );
}

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
