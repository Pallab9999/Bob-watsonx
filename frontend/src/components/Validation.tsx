import React, { useState } from "react";
import { api } from "../services/api";
import type { GuidedTask, ValidationResult, ValidationCheck } from "../types";

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface ValidationProps {
  task: GuidedTask;
  onClose?: () => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function Validation({ task, onClose }: ValidationProps) {
  const [code, setCode] = useState("");
  const [runTests, setRunTests] = useState(false);
  const [runLint, setRunLint] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.validate(task, code, { run_tests: runTests, run_lint: runLint });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Validation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.panel}>
        {/* Header */}
        <div style={styles.header}>
          <div>
            <h2 style={styles.title}>Validate Your Work</h2>
            <p style={styles.taskName}>{task.title}</p>
          </div>
          {onClose && (
            <button style={styles.closeBtn} onClick={onClose}>✕</button>
          )}
        </div>

        {/* Acceptance criteria reminder */}
        <div style={styles.criteria}>
          <p style={styles.criteriaLabel}>Acceptance criteria</p>
          <ul style={styles.criteriaList}>
            {task.acceptance_criteria.map((c, i) => (
              <li key={i} style={styles.criteriaItem}>
                {result
                  ? result.passed
                    ? "✓ "
                    : "✕ "
                  : "· "}
                {c}
              </li>
            ))}
          </ul>
        </div>

        {/* Code input */}
        <label style={styles.label}>Paste your code or diff</label>
        <textarea
          style={styles.codeInput}
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="// Paste your implementation here…"
          spellCheck={false}
          disabled={loading}
        />

        {/* Options */}
        <div style={styles.optionRow}>
          <ToggleCheck
            label="Run tests check"
            checked={runTests}
            onChange={setRunTests}
          />
          <ToggleCheck
            label="Run lint check"
            checked={runLint}
            onChange={setRunLint}
          />
        </div>

        {/* Validate button */}
        <button
          style={{
            ...styles.validateBtn,
            opacity: !code.trim() || loading ? 0.5 : 1,
            cursor: !code.trim() || loading ? "not-allowed" : "pointer",
          }}
          onClick={handleValidate}
          disabled={!code.trim() || loading}
        >
          {loading ? "Validating…" : "Run Validation"}
        </button>

        {/* Error */}
        {error && <p style={styles.errorMsg}>{error}</p>}

        {/* Results */}
        {result && <ValidationResults result={result} />}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function ToggleCheck({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label style={styles.toggleLabel}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        style={{ marginRight: 6 }}
      />
      {label}
    </label>
  );
}

function ValidationResults({ result }: { result: ValidationResult }) {
  return (
    <div style={styles.results}>
      {/* Overall banner */}
      <div
        style={{
          ...styles.banner,
          background: result.passed ? "#e6f4ea" : "#fef0ee",
          borderColor: result.passed ? "#1a7f37" : "#cf222e",
          color: result.passed ? "#1a7f37" : "#cf222e",
        }}
      >
        <span style={{ fontWeight: 700, fontSize: 16 }}>
          {result.passed ? "✓ All checks passed" : "✕ Some checks failed"}
        </span>
        <span style={styles.scoreChip}>Score: {result.score}/100</span>
      </div>

      {/* Individual checks */}
      <div style={styles.checkList}>
        {result.checks.map((c, i) => (
          <CheckRow key={i} check={c} />
        ))}
      </div>

      {/* Feedback */}
      {result.feedback && (
        <div style={styles.feedbackSection}>
          <p style={styles.sectionHeading}>Feedback</p>
          <p style={styles.feedbackText}>{result.feedback}</p>
        </div>
      )}

      {/* Strengths */}
      {result.strengths.length > 0 && (
        <div style={styles.feedbackSection}>
          <p style={styles.sectionHeading}>Strengths</p>
          <ul style={styles.dotList}>
            {result.strengths.map((s, i) => (
              <li key={i} style={styles.dotItem}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Suggestions */}
      {result.suggestions.length > 0 && (
        <div style={styles.feedbackSection}>
          <p style={styles.sectionHeading}>Suggestions</p>
          <ul style={styles.dotList}>
            {result.suggestions.map((s, i) => (
              <li key={i} style={styles.dotItem}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Next steps */}
      {result.next_steps.length > 0 && (
        <div style={styles.feedbackSection}>
          <p style={styles.sectionHeading}>Next Steps</p>
          <ul style={styles.dotList}>
            {result.next_steps.map((s, i) => (
              <li key={i} style={styles.dotItem}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function CheckRow({ check }: { check: ValidationCheck }) {
  const icon = check.status === "passed" ? "✓" : check.status === "failed" ? "✕" : "–";
  const color = check.status === "passed" ? "#1a7f37" : check.status === "failed" ? "#cf222e" : "#57606a";
  return (
    <div style={styles.checkRow}>
      <span style={{ color, fontWeight: 700, minWidth: 14 }}>{icon}</span>
      <div>
        <span style={styles.checkName}>{check.name}</span>
        {check.details && <p style={styles.checkDetails}>{check.details}</p>}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
    padding: "24px",
    overflowY: "auto",
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
  },
  panel: {
    background: "#fff",
    borderRadius: 10,
    padding: "32px",
    maxWidth: 640,
    width: "100%",
    maxHeight: "90vh",
    overflowY: "auto",
    boxSizing: "border-box",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 20,
  },
  title: {
    fontSize: 18,
    fontWeight: 700,
    margin: 0,
    color: "#1f2328",
  },
  taskName: {
    fontSize: 13,
    color: "#57606a",
    margin: "4px 0 0",
  },
  closeBtn: {
    background: "none",
    border: "none",
    fontSize: 16,
    cursor: "pointer",
    color: "#57606a",
    padding: 4,
  },
  criteria: {
    background: "#f7f8fa",
    border: "1px solid #e5e7eb",
    borderRadius: 6,
    padding: "12px 16px",
    marginBottom: 20,
  },
  criteriaLabel: {
    fontSize: 12,
    fontWeight: 600,
    color: "#57606a",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
    margin: "0 0 8px",
  },
  criteriaList: {
    margin: 0,
    paddingLeft: 0,
    listStyle: "none",
  },
  criteriaItem: {
    fontSize: 13,
    color: "#3b3f45",
    padding: "3px 0",
    lineHeight: 1.5,
  },
  label: {
    display: "block",
    fontSize: 13,
    fontWeight: 600,
    color: "#1f2328",
    marginBottom: 8,
  },
  codeInput: {
    width: "100%",
    minHeight: 160,
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
  optionRow: {
    display: "flex",
    gap: 20,
    margin: "12px 0 20px",
  },
  toggleLabel: {
    display: "flex",
    alignItems: "center",
    fontSize: 13,
    color: "#3b3f45",
    cursor: "pointer",
  },
  validateBtn: {
    width: "100%",
    background: "#3b82d4",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "12px",
    fontSize: 15,
    fontWeight: 700,
    marginBottom: 8,
  },
  errorMsg: {
    color: "#cf222e",
    fontSize: 13,
    margin: "8px 0 0",
  },
  results: {
    marginTop: 20,
  },
  banner: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    borderRadius: 6,
    border: "1px solid",
    marginBottom: 16,
  },
  scoreChip: {
    fontSize: 13,
    fontWeight: 600,
  },
  checkList: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    marginBottom: 16,
  },
  checkRow: {
    display: "flex",
    gap: 10,
    alignItems: "flex-start",
    background: "#f7f8fa",
    borderRadius: 6,
    padding: "10px 12px",
  },
  checkName: {
    fontSize: 13,
    fontWeight: 600,
    color: "#1f2328",
  },
  checkDetails: {
    fontSize: 12,
    color: "#57606a",
    margin: "2px 0 0",
    lineHeight: 1.5,
  },
  feedbackSection: {
    marginBottom: 14,
  },
  sectionHeading: {
    fontSize: 12,
    fontWeight: 700,
    color: "#57606a",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
    margin: "0 0 6px",
  },
  feedbackText: {
    fontSize: 13,
    color: "#3b3f45",
    lineHeight: 1.6,
    margin: 0,
  },
  dotList: {
    margin: 0,
    paddingLeft: 18,
  },
  dotItem: {
    fontSize: 13,
    color: "#3b3f45",
    lineHeight: 1.6,
    marginBottom: 4,
  },
};
