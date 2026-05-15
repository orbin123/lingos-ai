"use client";

import type { CSSProperties } from "react";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Plus, Save } from "lucide-react";

import { AdminLayout } from "@/components/admin/AdminLayout";
import {
  AdminButton,
  AdminPanel,
  TemplateStatusPill,
  formatAdminDate,
  tableStyle,
  tdStyle,
  thStyle,
} from "@/components/admin/AdminPrimitives";
import { adminApi, type TaskTemplate, type TaskTemplateInput } from "@/lib/admin-api";

const TASK_TYPES = [
  "reading",
  "writing",
  "speaking",
  "listening",
  "fill_in_blanks",
  "error_spotting",
  "sentence_transformation",
  "voice_conversion",
  "error_correction",
  "speak_with_tense",
  "curriculum_grammar_fill_blanks",
  "curriculum_grammar_open_text",
  "curriculum_grammar_listen_mcq",
  "curriculum_grammar_speak",
  "curriculum_vocab_mcq",
  "curriculum_vocab_open_text",
  "curriculum_vocab_listen_mcq",
  "curriculum_vocab_speak",
  "curriculum_pron_read_aloud",
  "curriculum_pron_phonetic_mcq",
  "curriculum_pron_listen_discriminate",
  "curriculum_pron_speak_drill",
  "curriculum_fluency_speed_read",
  "curriculum_fluency_timed_write",
  "curriculum_fluency_shadow",
  "curriculum_fluency_speak",
  "curriculum_expression_summarize",
  "curriculum_expression_essay",
  "curriculum_expression_listen_structure",
  "curriculum_expression_storyboard",
  "curriculum_comprehension_read_mcq",
  "curriculum_comprehension_write_answers",
  "curriculum_comprehension_listen_mcq",
  "curriculum_comprehension_retell",
  "curriculum_tone_read_mcq",
  "curriculum_tone_rewrite",
  "curriculum_tone_listen_mcq",
  "curriculum_tone_roleplay",
];

const DEFAULT_CONTENT = {
  instruction: "Write the learner-facing instruction here.",
  activities: [],
};

export default function AdminTaskTemplatesPage() {
  const queryClient = useQueryClient();
  const templatesQuery = useQuery({
    queryKey: ["admin", "task-templates"],
    queryFn: adminApi.taskTemplates,
  });
  const templates = useMemo(() => templatesQuery.data ?? [], [templatesQuery.data]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const selectedTemplate = useMemo(
    () => templates.find((template) => template.id === selectedId) ?? null,
    [selectedId, templates],
  );

  const createMutation = useMutation({
    mutationFn: adminApi.createTaskTemplate,
    onSuccess: async (template) => {
      setSelectedId(template.id);
      await queryClient.invalidateQueries({ queryKey: ["admin", "task-templates"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<TaskTemplateInput> }) =>
      adminApi.updateTaskTemplate(id, data),
    onSuccess: async (template) => {
      setSelectedId(template.id);
      await queryClient.invalidateQueries({ queryKey: ["admin", "task-templates"] });
    },
  });

  const archiveMutation = useMutation({
    mutationFn: adminApi.archiveTaskTemplate,
    onSuccess: async (template) => {
      setSelectedId(template.id);
      await queryClient.invalidateQueries({ queryKey: ["admin", "task-templates"] });
    },
  });

  return (
    <AdminLayout
      title="Task Templates"
      eyebrow="Curriculum operations"
      actions={
        <AdminButton tone="secondary" onClick={() => setSelectedId(null)}>
          <Plus size={16} />
          New template
        </AdminButton>
      }
    >
      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.3fr) 440px", gap: 18 }}>
        <AdminPanel style={{ overflow: "hidden" }}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Template</th>
                <th style={thStyle}>Type</th>
                <th style={thStyle}>Difficulty</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Updated</th>
              </tr>
            </thead>
            <tbody>
              {templates.map((template) => (
                <tr
                  key={template.id}
                  onClick={() => setSelectedId(template.id)}
                  style={{
                    cursor: "pointer",
                    background: selectedId === template.id ? "oklch(97% 0.025 240)" : "white",
                  }}
                >
                  <td style={tdStyle}>
                    <strong>{template.title}</strong>
                  </td>
                  <td style={tdStyle}>{template.task_type}</td>
                  <td style={tdStyle}>{template.difficulty}</td>
                  <td style={tdStyle}>
                    <TemplateStatusPill status={template.status} />
                  </td>
                  <td style={tdStyle}>{formatAdminDate(template.updated_at)}</td>
                </tr>
              ))}
              {templates.length === 0 && (
                <tr>
                  <td style={tdStyle} colSpan={5}>
                    No templates found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </AdminPanel>

        <TemplateEditor
          key={
            selectedTemplate
              ? `${selectedTemplate.id}-${selectedTemplate.updated_at}-${selectedTemplate.status}`
              : "new"
          }
          isSaving={createMutation.isPending || updateMutation.isPending}
          isArchiving={archiveMutation.isPending}
          template={selectedTemplate}
          onArchive={(templateId) => archiveMutation.mutate(templateId)}
          onCreate={(payload) => createMutation.mutate(payload)}
          onUpdate={(templateId, payload) =>
            updateMutation.mutate({ id: templateId, data: payload })
          }
        />
      </div>
    </AdminLayout>
  );
}

function TemplateEditor({
  template,
  isSaving,
  isArchiving,
  onArchive,
  onCreate,
  onUpdate,
}: {
  template: TaskTemplate | null;
  isSaving: boolean;
  isArchiving: boolean;
  onArchive: (templateId: number) => void;
  onCreate: (payload: TaskTemplateInput) => void;
  onUpdate: (templateId: number, payload: Partial<TaskTemplateInput>) => void;
}) {
  const [title, setTitle] = useState(template?.title ?? "");
  const [taskType, setTaskType] = useState(template?.task_type ?? "reading");
  const [difficulty, setDifficulty] = useState(template?.difficulty ?? 1);
  const [status, setStatus] = useState<TaskTemplateInput["status"]>(
    template?.status ?? "draft",
  );
  const [contentText, setContentText] = useState(
    JSON.stringify(template?.content ?? DEFAULT_CONTENT, null, 2),
  );
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = () => {
    setError(null);
    let content: Record<string, unknown>;
    try {
      content = JSON.parse(contentText) as Record<string, unknown>;
    } catch {
      setError("Content must be valid JSON.");
      return;
    }

    const payload = {
      title,
      task_type: taskType,
      difficulty,
      status,
      content,
    };

    if (template) {
      onUpdate(template.id, payload);
    } else {
      onCreate(payload);
    }
  };

  return (
    <AdminPanel style={{ padding: 20, alignSelf: "start" }}>
      <div style={editorHeadStyle}>
        <h2 style={editorTitleStyle}>{template ? "Edit template" : "Create template"}</h2>
        {template && <TemplateStatusPill status={template.status} />}
      </div>

      <div style={formGridStyle}>
        <label style={fieldStyle}>
          <span style={labelStyle}>Title</span>
          <input value={title} onChange={(event) => setTitle(event.target.value)} style={inputStyle} />
        </label>

        <label style={fieldStyle}>
          <span style={labelStyle}>Task type</span>
          <select value={taskType} onChange={(event) => setTaskType(event.target.value)} style={inputStyle}>
            {TASK_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </label>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          <label style={fieldStyle}>
            <span style={labelStyle}>Difficulty</span>
            <input
              min={1}
              max={10}
              type="number"
              value={difficulty}
              onChange={(event) => setDifficulty(Number(event.target.value))}
              style={inputStyle}
            />
          </label>
          <label style={fieldStyle}>
            <span style={labelStyle}>Status</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value as TaskTemplateInput["status"])}
              style={inputStyle}
            >
              <option value="draft">draft</option>
              <option value="active">active</option>
              <option value="archived">archived</option>
            </select>
          </label>
        </div>

        <label style={fieldStyle}>
          <span style={labelStyle}>Content JSON</span>
          <textarea
            value={contentText}
            onChange={(event) => setContentText(event.target.value)}
            style={textareaStyle}
            spellCheck={false}
          />
        </label>
      </div>

      {error && <div style={errorStyle}>{error}</div>}

      <div style={editorActionsStyle}>
        <AdminButton disabled={isSaving || !title.trim()} onClick={handleSubmit}>
          <Save size={16} />
          {template ? "Save changes" : "Create template"}
        </AdminButton>
        {template && template.status !== "archived" && (
          <AdminButton
            tone="danger"
            disabled={isArchiving}
            onClick={() => onArchive(template.id)}
          >
            <Archive size={16} />
            Archive
          </AdminButton>
        )}
      </div>
    </AdminPanel>
  );
}

const editorHeadStyle: CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  marginBottom: 16,
};

const editorTitleStyle: CSSProperties = {
  margin: 0,
  color: "oklch(18% 0.055 245)",
  fontSize: 18,
  fontWeight: 850,
};

const formGridStyle: CSSProperties = {
  display: "grid",
  gap: 12,
};

const fieldStyle: CSSProperties = {
  display: "grid",
  gap: 7,
};

const labelStyle: CSSProperties = {
  color: "oklch(48% 0.045 245)",
  fontSize: 11,
  fontWeight: 850,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
};

const inputStyle: CSSProperties = {
  width: "100%",
  minHeight: 40,
  borderRadius: 8,
  border: "1px solid oklch(86% 0.018 245)",
  padding: "0 11px",
  color: "oklch(18% 0.055 245)",
  fontSize: 14,
  fontWeight: 650,
  fontFamily: "inherit",
  background: "white",
};

const textareaStyle: CSSProperties = {
  ...inputStyle,
  minHeight: 260,
  padding: 12,
  fontFamily: "var(--font-geist-mono), ui-monospace, SFMono-Regular, monospace",
  lineHeight: 1.5,
  resize: "vertical",
};

const errorStyle: CSSProperties = {
  marginTop: 12,
  borderRadius: 8,
  background: "oklch(95% 0.04 25)",
  color: "oklch(42% 0.16 25)",
  padding: "10px 12px",
  fontSize: 13,
  fontWeight: 750,
};

const editorActionsStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 10,
  marginTop: 16,
};
