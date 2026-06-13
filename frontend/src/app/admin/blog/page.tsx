"use client";

import type { CSSProperties } from "react";
import { useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff, Image as ImageIcon, Plus, Save, Trash2 } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminButton,
  AdminPanel,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { CoverArt } from "@/components/blog/BlogVisuals";
import { MarkdownContent } from "@/components/blog/MarkdownContent";
import {
  adminApi,
  type BlogPostAdmin,
  type BlogStatus,
} from "@/lib/admin-api";
import { absolutizeMediaUrl } from "@/lib/blog-api";

const BLOG_KEY = ["admin", "blog"] as const;

interface EditorState {
  id: number | null;
  title: string;
  slug: string;
  excerpt: string;
  category: string;
  status: BlogStatus;
  content: string;
  cover_image_url: string | null;
}

function blankEditor(): EditorState {
  return {
    id: null,
    title: "",
    slug: "",
    excerpt: "",
    category: "",
    status: "draft",
    content: "",
    cover_image_url: null,
  };
}

function toEditor(post: BlogPostAdmin): EditorState {
  return {
    id: post.id,
    title: post.title,
    slug: post.slug,
    excerpt: post.excerpt ?? "",
    category: post.category ?? "",
    status: post.status,
    content: post.content,
    cover_image_url: post.cover_image_url,
  };
}

export default function AdminBlogPage() {
  const queryClient = useQueryClient();
  const [editor, setEditor] = useState<EditorState | null>(null);
  const [flash, setFlash] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const postsQuery = useQuery({ queryKey: BLOG_KEY, queryFn: adminApi.blogList });
  const posts = postsQuery.data ?? [];

  const showFlash = (kind: "ok" | "err", text: string) => {
    setFlash({ kind, text });
    window.setTimeout(() => setFlash(null), 3500);
  };
  const invalidate = () => queryClient.invalidateQueries({ queryKey: BLOG_KEY });

  const saveMutation = useMutation({
    mutationFn: (state: EditorState) => {
      const payload = {
        title: state.title,
        slug: state.slug.trim() || undefined,
        excerpt: state.excerpt.trim() || null,
        category: state.category.trim() || null,
        content: state.content,
        status: state.status,
        cover_image_url: state.cover_image_url,
      };
      return state.id == null
        ? adminApi.blogCreate(payload)
        : adminApi.blogUpdate(state.id, payload);
    },
    onSuccess: async (post) => {
      await invalidate();
      setEditor(toEditor(post)); // keep open with the saved id (enables cover upload)
      showFlash("ok", "Saved.");
    },
    onError: (err: unknown) => showFlash("err", apiError(err, "Could not save post.")),
  });

  const deleteMutation = useMutation({
    mutationFn: (postId: number) => adminApi.blogDelete(postId),
    onSuccess: async (_data, postId) => {
      await invalidate();
      if (editor?.id === postId) setEditor(null);
      showFlash("ok", "Deleted.");
    },
    onError: (err: unknown) => showFlash("err", apiError(err, "Could not delete post.")),
  });

  const statusMutation = useMutation({
    mutationFn: ({ post }: { post: BlogPostAdmin }) =>
      post.status === "published"
        ? adminApi.blogUnpublish(post.id)
        : adminApi.blogPublish(post.id),
    onSuccess: async (post) => {
      await invalidate();
      if (editor?.id === post.id) setEditor(toEditor(post));
      showFlash("ok", post.status === "published" ? "Published." : "Unpublished.");
    },
    onError: (err: unknown) => showFlash("err", apiError(err, "Could not change status.")),
  });

  const coverMutation = useMutation({
    mutationFn: ({ postId, file }: { postId: number; file: File }) =>
      adminApi.blogUploadCover(postId, file),
    onSuccess: async (post) => {
      await invalidate();
      setEditor(toEditor(post));
      showFlash("ok", "Cover image uploaded.");
    },
    onError: (err: unknown) => showFlash("err", apiError(err, "Could not upload image.")),
  });

  const onPickCover = (file: File | undefined) => {
    if (!file || editor?.id == null) return;
    coverMutation.mutate({ postId: editor.id, file });
  };

  return (
    <AdminLayout
      title="Blog Management"
      eyebrow="Content"
      actions={
        <AdminButton onClick={() => { setEditor(blankEditor()); setFlash(null); }}>
          <Plus size={15} />
          New Post
        </AdminButton>
      }
    >
      {flash && (
        <div style={flash.kind === "ok" ? flashOkStyle : flashErrStyle}>{flash.text}</div>
      )}

      <div style={layoutStyle}>
        {/* ── List ─────────────────────────────────────────────── */}
        <AdminPanel style={{ overflow: "hidden" }}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Title</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Published</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {posts.map((post) => (
                <tr key={post.id}>
                  <td style={tdStyle}>
                    <div style={{ fontWeight: 800, color: "oklch(18% 0.055 245)" }}>
                      {post.title}
                    </div>
                    <div style={mutedStyle}>
                      {(post.category ?? "Uncategorized")} · /{post.slug}
                    </div>
                  </td>
                  <td style={tdStyle}>
                    <BlogStatusPill status={post.status} />
                  </td>
                  <td style={tdStyle}>{formatAdminDate(post.published_at)}</td>
                  <td style={{ ...tdStyle, textAlign: "right" }}>
                    <div style={actionsCellStyle}>
                      <AdminButton tone="secondary" onClick={() => { setEditor(toEditor(post)); setFlash(null); }}>
                        Edit
                      </AdminButton>
                      <AdminButton
                        tone="secondary"
                        disabled={statusMutation.isPending}
                        onClick={() => statusMutation.mutate({ post })}
                      >
                        {post.status === "published" ? <EyeOff size={14} /> : <Eye size={14} />}
                        {post.status === "published" ? "Unpublish" : "Publish"}
                      </AdminButton>
                      <AdminButton
                        tone="danger"
                        disabled={deleteMutation.isPending}
                        onClick={() => {
                          if (window.confirm(`Delete "${post.title}"? This cannot be undone.`)) {
                            deleteMutation.mutate(post.id);
                          }
                        }}
                      >
                        <Trash2 size={14} />
                      </AdminButton>
                    </div>
                  </td>
                </tr>
              ))}
              {posts.length === 0 && !postsQuery.isLoading && (
                <tr>
                  <td style={tdStyle} colSpan={4}>No blog posts yet. Create your first one.</td>
                </tr>
              )}
              {postsQuery.isLoading && (
                <tr>
                  <td style={tdStyle} colSpan={4}>Loading…</td>
                </tr>
              )}
            </tbody>
          </table>
        </AdminPanel>

        {/* ── Editor ───────────────────────────────────────────── */}
        {editor && (
          <Editor
            editor={editor}
            setEditor={setEditor}
            onSave={() => saveMutation.mutate(editor)}
            onClose={() => setEditor(null)}
            saving={saveMutation.isPending}
            uploadingCover={coverMutation.isPending}
            fileInputRef={fileInputRef}
            onPickCover={onPickCover}
          />
        )}
      </div>
    </AdminLayout>
  );
}

function Editor({
  editor,
  setEditor,
  onSave,
  onClose,
  saving,
  uploadingCover,
  fileInputRef,
  onPickCover,
}: {
  editor: EditorState;
  setEditor: (e: EditorState) => void;
  onSave: () => void;
  onClose: () => void;
  saving: boolean;
  uploadingCover: boolean;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  onPickCover: (file: File | undefined) => void;
}) {
  const set = <K extends keyof EditorState>(key: K, value: EditorState[K]) =>
    setEditor({ ...editor, [key]: value });
  const coverPreview = absolutizeMediaUrl(editor.cover_image_url);
  const canSave = editor.title.trim().length > 0 && editor.content.trim().length > 0;

  return (
    <AdminPanel style={{ padding: 22, alignSelf: "start", position: "sticky", top: 24 }}>
      <div style={editorHeadStyle}>
        <h2 style={editorTitleStyle}>{editor.id == null ? "New post" : "Edit post"}</h2>
        <button type="button" onClick={onClose} style={closeBtnStyle}>Close</button>
      </div>

      <Field label="Title">
        <input style={inputStyle} value={editor.title} onChange={(e) => set("title", e.target.value)} placeholder="Article title" />
      </Field>

      <div style={twoColStyle}>
        <Field label="Slug" hint="Leave blank to auto-generate">
          <input style={inputStyle} value={editor.slug} onChange={(e) => set("slug", e.target.value)} placeholder="auto-from-title" />
        </Field>
        <Field label="Category">
          <input style={inputStyle} value={editor.category} onChange={(e) => set("category", e.target.value)} placeholder="e.g. Communication" />
        </Field>
      </div>

      <Field label="Excerpt" hint="Short summary shown on cards">
        <textarea style={{ ...inputStyle, minHeight: 60, resize: "vertical" }} value={editor.excerpt} onChange={(e) => set("excerpt", e.target.value)} />
      </Field>

      <Field label="Status">
        <select style={inputStyle} value={editor.status} onChange={(e) => set("status", e.target.value as BlogStatus)}>
          <option value="draft">Draft</option>
          <option value="published">Published</option>
        </select>
      </Field>

      <Field label="Cover image">
        <div style={{ display: "grid", gap: 10 }}>
          <div style={{ position: "relative", height: 150, borderRadius: 10, overflow: "hidden", border: "1px solid oklch(90% 0.014 245)" }}>
            <CoverArt src={coverPreview} alt="Cover preview" radius={0} />
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
            <AdminButton
              tone="secondary"
              disabled={editor.id == null || uploadingCover}
              onClick={() => fileInputRef.current?.click()}
            >
              <ImageIcon size={14} />
              {uploadingCover ? "Uploading…" : "Upload"}
            </AdminButton>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              style={{ display: "none" }}
              onChange={(e) => { onPickCover(e.target.files?.[0]); e.target.value = ""; }}
            />
            <span style={mutedStyle}>
              {editor.id == null ? "Save the post first to upload, or paste a URL below." : "PNG/JPEG/WebP/GIF, max 5 MB."}
            </span>
          </div>
          <input
            style={inputStyle}
            value={editor.cover_image_url ?? ""}
            onChange={(e) => set("cover_image_url", e.target.value || null)}
            placeholder="…or paste an image URL"
          />
        </div>
      </Field>

      <Field label="Content (Markdown)">
        <textarea
          style={{ ...inputStyle, minHeight: 240, fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", resize: "vertical" }}
          value={editor.content}
          onChange={(e) => set("content", e.target.value)}
          placeholder="Write your article in Markdown…"
        />
      </Field>

      {editor.content.trim() && (
        <details style={{ marginBottom: 16 }}>
          <summary style={previewSummaryStyle}>Preview</summary>
          <div style={previewBodyStyle}>
            <MarkdownContent>{editor.content}</MarkdownContent>
          </div>
        </details>
      )}

      <div style={{ display: "flex", gap: 10 }}>
        <AdminButton onClick={onSave} disabled={!canSave || saving}>
          <Save size={15} />
          {saving ? "Saving…" : "Save"}
        </AdminButton>
      </div>
    </AdminPanel>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label style={{ display: "block", marginBottom: 16 }}>
      <div style={fieldLabelStyle}>
        {label}
        {hint && <span style={fieldHintStyle}>{hint}</span>}
      </div>
      {children}
    </label>
  );
}

function BlogStatusPill({ status }: { status: BlogStatus }) {
  const published = status === "published";
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        minHeight: 26,
        borderRadius: 999,
        padding: "0 12px",
        fontSize: 12,
        fontWeight: 800,
        textTransform: "capitalize",
        background: published ? "oklch(94% 0.06 155)" : "oklch(96% 0.05 80)",
        color: published ? "oklch(34% 0.13 155)" : "oklch(42% 0.12 70)",
      }}
    >
      {status}
    </span>
  );
}

function apiError(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}

// ── styles ──────────────────────────────────────────────────────────────────
const layoutStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1fr) minmax(380px, 460px)",
  gap: 18,
  alignItems: "start",
};

const mutedStyle: CSSProperties = {
  marginTop: 3,
  color: "oklch(48% 0.045 245)",
  fontSize: 12,
  fontWeight: 600,
};

const actionsCellStyle: CSSProperties = {
  display: "inline-flex",
  gap: 8,
  justifyContent: "flex-end",
  flexWrap: "wrap",
};

const editorHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  marginBottom: 18,
};

const editorTitleStyle: CSSProperties = {
  margin: 0,
  fontSize: 17,
  fontWeight: 850,
  color: "oklch(18% 0.055 245)",
};

const closeBtnStyle: CSSProperties = {
  border: "none",
  background: "transparent",
  color: "oklch(48% 0.045 245)",
  fontWeight: 750,
  fontSize: 13,
  cursor: "pointer",
};

const twoColStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "1fr 1fr",
  gap: 12,
};

const fieldLabelStyle: CSSProperties = {
  display: "flex",
  alignItems: "baseline",
  gap: 8,
  marginBottom: 6,
  color: "oklch(30% 0.055 245)",
  fontSize: 13,
  fontWeight: 800,
};

const fieldHintStyle: CSSProperties = {
  color: "oklch(55% 0.04 245)",
  fontSize: 11,
  fontWeight: 600,
};

const inputStyle: CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  minHeight: 40,
  border: "1px solid oklch(86% 0.018 245)",
  borderRadius: 8,
  padding: "9px 12px",
  fontFamily: "inherit",
  fontSize: 14,
  color: "oklch(20% 0.05 245)",
  background: "white",
};

const previewSummaryStyle: CSSProperties = {
  cursor: "pointer",
  fontSize: 13,
  fontWeight: 800,
  color: "oklch(40% 0.12 240)",
};

const previewBodyStyle: CSSProperties = {
  marginTop: 12,
  padding: 16,
  border: "1px solid oklch(91% 0.014 245)",
  borderRadius: 10,
  background: "oklch(99% 0.004 245)",
};

const flashOkStyle: CSSProperties = {
  marginBottom: 16,
  padding: "11px 16px",
  borderRadius: 8,
  background: "oklch(94% 0.06 155)",
  color: "oklch(32% 0.13 155)",
  fontWeight: 750,
  fontSize: 13,
};

const flashErrStyle: CSSProperties = {
  ...flashOkStyle,
  background: "oklch(95% 0.05 25)",
  color: "oklch(42% 0.16 25)",
};
