import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { api } from "../services/api";
import type { ContributionSuggestion, OnboardingPlan } from "../types";
import Validation from "./Validation";
import type { GuidedTask } from "../types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface LocationState {
  plan?: OnboardingPlan;
  repoData?: Record<string, unknown>;
}

type DifficultyFilter = "all" | "beginner" | "intermediate";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FirstContribution() {
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [suggestions, setSuggestions] = useState<ContributionSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<DifficultyFilter>("all");
  const [activeTask, setActiveTask] = useState<GuidedTask | null>(null);

  useEffect(() => {
    if (!state?.repoData) return;

    setLoading(true);
    setError(null);

    api
      .suggestContributions("current-repo", state.repoData)
      .then((res) => setSuggestions(res.suggestions))
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load suggestions")
      )
      .finally(() => setLoading(false));
  }, [state?.repoData]);

  const filtered =
    filter === "all"
      ? suggestions
      : suggestions.filter((s) => s.difficulty === filter);

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>First Contribution</h1>
      <p style={styles.subtitle}>
        Starter tasks picked specifically for this repository. Each one is safe,
        focused, and builds real understanding.
      </p>

      {/* Difficulty filter */}
      <div style={styles.filterRow}>
        {(["all", "beginner", "intermediate"] as DifficultyFilter[]).map((f) => (
          <button
            key={f}
            style={{
              ...styles.filterBtn,
              ...(filter === f ? styles.filterBtnActive : {}),
            }}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* States */}
      {loading && <p style={styles.loadingMsg}>Analysing repository for good first tasks…</p>}
      {error && <p style={styles.errorMsg}>{error}</p>}

      {/* Cards */}
      {!loading && filtered.length === 0 && !error && (
        <p style={styles.emptyMsg}>No suggestions found for the selected filter.</p>
      )}

      <div style={styles.cardGrid}>
        {filtered.map((s) => (
          <SuggestionCard
            key={s.id}
            suggestion={s}
            onStart={() => {
              // Convert suggestion to a GuidedTask shape for Validation
              setActiveTask({
                id: s.id,
                title: s.title,
                objective: s.description,
                context: s.why_good_first_task,
                difficulty: s.difficulty,
                estimated_minutes: Math.round(s.estimated_hours * 60),
                files_to_explore: s.files_involved,
                steps: [],
                hints: [],
                acceptance_criteria: s.acceptance_criteria,
              });
            }}
          />
        ))}
      </div>

      {/* Validation modal */}
      {activeTask && (
        <Validation task={activeTask} onClose={() => setActiveTask(null)} />
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SuggestionCard({
  suggestion,
  onStart,
}: {
  suggestion: ContributionSuggestion;
  onStart: () => void;
}) {
  const diffColor =
    suggestion.difficulty === "beginner" ? "#1a7f37" : "#9a6700";

  return (
    <div style={styles.card}>
      <div style={styles.cardHeader}>
        <span style={{ ...styles.diffBadge, borderColor: diffColor, color: diffColor }}>
          {suggestion.difficulty}
        </span>
        <span style={styles.timeEstimate}>~{suggestion.estimated_hours}h</span>
      </div>

      <h3 style={styles.cardTitle}>{suggestion.title}</h3>
      <p style={styles.cardDesc}>{suggestion.description}</p>

      <div style={styles.whyBox}>
        <span style={styles.whyLabel}>Why this is a good first task</span>
        <p style={styles.whyText}>{suggestion.why_good_first_task}</p>
      </div>

      {suggestion.files_involved.length > 0 && (
        <div style={styles.filesRow}>
          {suggestion.files_involved.slice(0, 3).map((f) => (
            <code key={f} style={styles.fileChip}>{f}</code>
          ))}
        </div>
      )}

      {suggestion.acceptance_criteria.length > 0 && (
        <ul style={styles.criteriaList}>
          {suggestion.acceptance_criteria.map((c, i) => (
            <li key={i} style={styles.criteriaItem}>✓ {c}</li>
          ))}
        </ul>
      )}

      <button style={styles.startBtn} onClick={onStart}>
        Start This Task →
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  page: {
    maxWidth: 900,
    margin: "0 auto",
    padding: "32px 24px 64px",
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
    color: "#1f2328",
  },
  title: {
    fontSize: 24,
    fontWeight: 700,
    margin: "0 0 8px",
  },
  subtitle: {
    fontSize: 15,
    color: "#57606a",
    lineHeight: 1.6,
    margin: "0 0 24px",
  },
  filterRow: {
    display: "flex",
    gap: 8,
    marginBottom: 28,
  },
  filterBtn: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 20,
    padding: "6px 16px",
    fontSize: 13,
    cursor: "pointer",
    color: "#3b3f45",
  },
  filterBtnActive: {
    background: "#3b82d4",
    borderColor: "#3b82d4",
    color: "#fff",
  },
  loadingMsg: {
    color: "#57606a",
    fontSize: 14,
  },
  errorMsg: {
    color: "#cf222e",
    fontSize: 14,
  },
  emptyMsg: {
    color: "#57606a",
    fontSize: 14,
  },
  cardGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: 20,
  },
  card: {
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "20px",
    background: "#fff",
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  diffBadge: {
    border: "1px solid",
    borderRadius: 4,
    padding: "2px 8px",
    fontSize: 11,
    fontWeight: 600,
    textTransform: "capitalize",
  },
  timeEstimate: {
    fontSize: 12,
    color: "#57606a",
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: 700,
    margin: 0,
  },
  cardDesc: {
    fontSize: 13,
    color: "#3b3f45",
    lineHeight: 1.6,
    margin: 0,
  },
  whyBox: {
    background: "#f7f8fa",
    borderRadius: 6,
    padding: "10px 12px",
  },
  whyLabel: {
    display: "block",
    fontSize: 11,
    fontWeight: 600,
    color: "#57606a",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
    marginBottom: 4,
  },
  whyText: {
    fontSize: 12,
    color: "#3b3f45",
    lineHeight: 1.5,
    margin: 0,
  },
  filesRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
  },
  fileChip: {
    background: "#f0f4ff",
    color: "#3b5bdb",
    borderRadius: 4,
    padding: "2px 7px",
    fontSize: 11,
    fontFamily: '"SFMono-Regular", "Consolas", monospace',
  },
  criteriaList: {
    margin: 0,
    padding: 0,
    listStyle: "none",
  },
  criteriaItem: {
    fontSize: 12,
    color: "#1a7f37",
    lineHeight: 1.5,
    padding: "2px 0",
  },
  startBtn: {
    marginTop: "auto",
    background: "#3b82d4",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "10px",
    fontSize: 13,
    fontWeight: 700,
    cursor: "pointer",
    textAlign: "center",
  },
};
