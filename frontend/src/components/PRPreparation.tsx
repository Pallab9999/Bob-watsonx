import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import { api } from "../services/api";
import type { GuidedTask, PRDraft } from "../types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface LocationState {
  task?: GuidedTask;
  filesChanged?: string[];
  testsPerformed?: string[];
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function PRPreparation() {
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [filesChanged, setFilesChanged] = useState<string>(
    (state?.filesChanged ?? []).join("\n")
  );
  const [testsPerformed, setTestsPerformed] = useState<string>(
    (state?.testsPerformed ?? []).join("\n")
  );
  const [loading, setLoading] = useState(false);
  const [pr, setPR] = useState<PRDraft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Use a placeholder task when none is passed via state (e.g. direct navigation)
  const task: GuidedTask = state?.task ?? {
    id: "demo",
    title: "General contribution",
    objective: "Improve the codebase",
    context: "",
    difficulty: "beginner",
    estimated_minutes: 30,
    files_to_explore: [],
    steps: [],
    hints: [],
    acceptance_criteria: [],
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setPR(null);
    try {
      const files = filesChanged
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);
      const tests = testsPerformed
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);
      const result = await api.generatePR(task, files, tests);
      setPR(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "PR generation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!pr) return;
    const text = `## ${pr.title}\n\n${pr.description}\n\n### Checklist\n${pr.checklist.map((c) => `- [ ] ${c}`).join("\n")}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>Prepare Your First PR</h1>
        <p style={styles.subtitle}>
          You're ready to open your first pull request. Fill in what you changed
          and we'll generate the title and description for you.
        </p>

        {/* Readiness checklist */}
        <div style={styles.readinessBox}>
          <p style={styles.readinessTitle}>✓ Readiness checklist</p>
          {[
            "Code changes made",
            "Existing tests still pass",
            "New functionality is tested",
            "Code follows project style",
            "No unrelated changes included",
          ].map((item) => (
            <div key={item} style={styles.readinessItem}>
              <span style={styles.readinessCheck}>✓</span>
              <span>{item}</span>
            </div>
          ))}
        </div>

        {/* Task info */}
        <div style={styles.taskBox}>
          <p style={styles.fieldLabel}>Task completed</p>
          <p style={styles.taskTitle}>{task.title}</p>
          {task.objective && <p style={styles.taskObjective}>{task.objective}</p>}
        </div>

        {/* Files changed */}
        <div style={styles.field}>
          <label style={styles.fieldLabel}>Files changed (one per line)</label>
          <textarea
            style={styles.textarea}
            value={filesChanged}
            onChange={(e) => setFilesChanged(e.target.value)}
            placeholder={"src/components/Login.tsx\nsrc/utils/auth.ts"}
            rows={4}
            disabled={loading}
          />
        </div>

        {/* Tests performed */}
        <div style={styles.field}>
          <label style={styles.fieldLabel}>Tests performed (one per line)</label>
          <textarea
            style={styles.textarea}
            value={testsPerformed}
            onChange={(e) => setTestsPerformed(e.target.value)}
            placeholder={"Ran npm test — all 34 tests pass\nManually verified login flow"}
            rows={3}
            disabled={loading}
          />
        </div>

        <button
          style={{
            ...styles.generateBtn,
            opacity: loading ? 0.6 : 1,
            cursor: loading ? "not-allowed" : "pointer",
          }}
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? "Generating…" : "Generate PR Description"}
        </button>

        {error && <p style={styles.errorMsg}>{error}</p>}

        {/* PR Preview */}
        {pr && (
          <div style={styles.prPreview}>
            <div style={styles.prHeader}>
              <h2 style={styles.prTitle}>{pr.title}</h2>
              <button style={styles.copyBtn} onClick={handleCopy}>
                {copied ? "✓ Copied!" : "Copy PR Template"}
              </button>
            </div>

            {pr.labels.length > 0 && (
              <div style={styles.labelsRow}>
                {pr.labels.map((l) => (
                  <span key={l} style={styles.label}>{l}</span>
                ))}
              </div>
            )}

            <div style={styles.prDescription}>
              <pre style={styles.prBody}>{pr.description}</pre>
            </div>

            {pr.checklist.length > 0 && (
              <div style={styles.checklistSection}>
                <p style={styles.checklistHeading}>Pre-merge checklist</p>
                {pr.checklist.map((item, i) => (
                  <div key={i} style={styles.checklistItem}>
                    <input type="checkbox" id={`cl-${i}`} style={{ marginRight: 8 }} />
                    <label htmlFor={`cl-${i}`} style={{ fontSize: 13, cursor: "pointer" }}>
                      {item}
                    </label>
                  </div>
                ))}
              </div>
            )}

            {pr.files_changed.length > 0 && (
              <div style={styles.filesSection}>
                <p style={styles.checklistHeading}>Files changed</p>
                {pr.files_changed.map((f) => (
                  <code key={f} style={styles.fileChip}>{f}</code>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    background: "#f7f8fa",
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
    padding: "32px 16px 64px",
  },
  container: {
    maxWidth: 680,
    margin: "0 auto",
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    margin: "0 0 8px",
    color: "#1f2328",
  },
  subtitle: {
    fontSize: 15,
    color: "#57606a",
    lineHeight: 1.6,
    margin: "0 0 28px",
  },
  readinessBox: {
    background: "#e6f4ea",
    border: "1px solid #1a7f37",
    borderRadius: 8,
    padding: "16px 20px",
    marginBottom: 24,
  },
  readinessTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#1a7f37",
    margin: "0 0 10px",
  },
  readinessItem: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    fontSize: 13,
    color: "#1f2328",
    padding: "3px 0",
  },
  readinessCheck: {
    color: "#1a7f37",
    fontWeight: 700,
  },
  taskBox: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "16px 20px",
    marginBottom: 20,
  },
  taskTitle: {
    fontSize: 15,
    fontWeight: 700,
    color: "#1f2328",
    margin: "4px 0",
  },
  taskObjective: {
    fontSize: 13,
    color: "#57606a",
    lineHeight: 1.5,
    margin: 0,
  },
  field: {
    marginBottom: 20,
  },
  fieldLabel: {
    display: "block",
    fontSize: 13,
    fontWeight: 600,
    color: "#1f2328",
    marginBottom: 6,
  },
  textarea: {
    width: "100%",
    fontFamily: '"SFMono-Regular", "Consolas", monospace',
    fontSize: 12,
    border: "1px solid #e5e7eb",
    borderRadius: 6,
    padding: "10px 12px",
    resize: "vertical",
    boxSizing: "border-box",
    outline: "none",
    background: "#fafbfc",
  },
  generateBtn: {
    width: "100%",
    background: "#3b82d4",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "13px",
    fontSize: 15,
    fontWeight: 700,
    marginBottom: 8,
  },
  errorMsg: {
    color: "#cf222e",
    fontSize: 13,
    margin: "8px 0",
  },
  prPreview: {
    marginTop: 24,
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    background: "#fff",
    overflow: "hidden",
  },
  prHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    padding: "20px 24px 16px",
    borderBottom: "1px solid #e5e7eb",
    gap: 12,
    flexWrap: "wrap",
  },
  prTitle: {
    fontSize: 18,
    fontWeight: 700,
    margin: 0,
    color: "#1f2328",
    flex: 1,
  },
  copyBtn: {
    background: "#fff",
    border: "1px solid #3b82d4",
    color: "#3b82d4",
    borderRadius: 6,
    padding: "8px 16px",
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
    flexShrink: 0,
  },
  labelsRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
    padding: "0 24px 12px",
  },
  label: {
    background: "#f0f4ff",
    color: "#3b5bdb",
    borderRadius: 12,
    padding: "2px 10px",
    fontSize: 12,
    fontWeight: 600,
  },
  prDescription: {
    padding: "16px 24px",
    borderBottom: "1px solid #f0f0f0",
  },
  prBody: {
    fontSize: 13,
    lineHeight: 1.7,
    color: "#3b3f45",
    margin: 0,
    whiteSpace: "pre-wrap",
    fontFamily: "inherit",
  },
  checklistSection: {
    padding: "16px 24px",
    borderBottom: "1px solid #f0f0f0",
  },
  checklistHeading: {
    fontSize: 12,
    fontWeight: 700,
    color: "#57606a",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
    margin: "0 0 10px",
  },
  checklistItem: {
    display: "flex",
    alignItems: "center",
    padding: "4px 0",
  },
  filesSection: {
    padding: "16px 24px",
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
  },
  fileChip: {
    background: "#f0f4ff",
    color: "#3b5bdb",
    borderRadius: 4,
    padding: "2px 8px",
    fontSize: 11,
    fontFamily: '"SFMono-Regular", "Consolas", monospace',
  },
};
