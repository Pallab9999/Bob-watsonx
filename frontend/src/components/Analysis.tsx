import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { api } from "../services/api";
import type { UserProfile, OnboardingPlan } from "../types";



// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AnalysisStep {
  id: string;
  label: string;
  status: "waiting" | "running" | "done" | "error";
}

interface LocationState {
  repoId: string;
  repoData: Record<string, unknown>;
  userProfile: UserProfile;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const STEPS: Omit<AnalysisStep, "status">[] = [
  { id: "connect", label: "Repository connected" },
  { id: "techstack", label: "Detecting tech stack" },
  { id: "structure", label: "Mapping directory structure" },
  { id: "entrypoints", label: "Finding entry points" },
  { id: "tests", label: "Identifying test frameworks" },
  { id: "plan", label: "Building your onboarding plan" },
];

export default function Analysis() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  const [steps, setSteps] = useState<AnalysisStep[]>(
    STEPS.map((s, i) => ({ ...s, status: i === 0 ? "running" : "waiting" }))
  );
  const [error, setError] = useState<string | null>(null);

  // Advance a step by id
  const advance = (id: string, status: AnalysisStep["status"]) => {
    setSteps((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status } : s))
    );
  };

  // Kick off the next step after the current one
  const runStep = (id: string) => {
    const idx = STEPS.findIndex((s) => s.id === id);
    if (idx < STEPS.length - 1) {
      setSteps((prev) =>
        prev.map((s, i) => (i === idx + 1 ? { ...s, status: "running" } : s))
      );
    }
  };

  useEffect(() => {
    if (!state) {
      navigate("/input");
      return;
    }

    let cancelled = false;

    const run = async () => {
      const { repoId, repoData, userProfile } = state;

      try {
        // Step 1: connect — already shown as running, mark done quickly
        await delay(400);
        if (cancelled) return;
        advance("connect", "done");
        runStep("connect");

        // Step 2: tech stack
        await delay(600);
        if (cancelled) return;
        advance("techstack", "done");
        runStep("techstack");

        // Step 3: structure
        await delay(500);
        if (cancelled) return;
        advance("structure", "done");
        runStep("structure");

        // Step 4: entry points
        await delay(400);
        if (cancelled) return;
        advance("entrypoints", "done");
        runStep("entrypoints");

        // Step 5: tests
        await delay(400);
        if (cancelled) return;
        advance("tests", "done");
        runStep("tests");

        // Step 6: generate plan (real AI call)
        const plan: OnboardingPlan = await api.generatePlan(
          repoId,
          repoData,
          userProfile
        );
        if (cancelled) return;
        advance("plan", "done");

        // Navigate to dashboard
        navigate("/dashboard", { state: { plan, repoData, userProfile } });
      } catch (err: unknown) {
        if (cancelled) return;
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
        // Mark current running step as error
        setSteps((prev) =>
          prev.map((s) => (s.status === "running" ? { ...s, status: "error" } : s))
        );
      }
    };

    run();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Analysing Repository</h1>
        <p style={styles.subtitle}>
          Hang tight — we're building your personalised onboarding path.
        </p>

        <ul style={styles.stepList}>
          {steps.map((step) => (
            <li key={step.id} style={styles.stepItem}>
              <StatusIcon status={step.status} />
              <span
                style={{
                  ...styles.stepLabel,
                  color: step.status === "done" ? "#1f2328" : step.status === "error" ? "#cf222e" : "#57606a",
                  fontWeight: step.status === "running" ? 600 : 400,
                }}
              >
                {step.label}
              </span>
              {step.status === "running" && <Spinner />}
            </li>
          ))}
        </ul>

        {error && (
          <div style={styles.errorBox}>
            <strong>Analysis failed:</strong> {error}
            <br />
            <button style={styles.retryBtn} onClick={() => navigate("/input")}>
              ← Try Again
            </button>
          </div>
        )}

        {!error && steps.every((s) => s.status === "done") && (
          <p style={styles.doneMsg}>✓ Your onboarding path is ready!</p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatusIcon({ status }: { status: AnalysisStep["status"] }) {
  const map: Record<AnalysisStep["status"], string> = {
    waiting: "○",
    running: "◎",
    done: "✓",
    error: "✕",
  };
  const color: Record<AnalysisStep["status"], string> = {
    waiting: "#57606a",
    running: "#3b82d4",
    done: "#1a7f37",
    error: "#cf222e",
  };
  return (
    <span style={{ color: color[status], fontWeight: 700, marginRight: 8, minWidth: 16 }}>
      {map[status]}
    </span>
  );
}

function Spinner() {
  const [frame, setFrame] = useState(0);
  const frames = ["⠋", "⠙", "⠸", "⠴", "⠦", "⠇"];
  useEffect(() => {
    const t = setInterval(() => setFrame((f) => (f + 1) % frames.length), 120);
    return () => clearInterval(t);
  }, [frames.length]);
  return <span style={{ marginLeft: 8, color: "#3b82d4" }}>{frames[frame]}</span>;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f7f8fa",
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
  },
  card: {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "40px 48px",
    maxWidth: 520,
    width: "100%",
  },
  title: {
    fontSize: 22,
    fontWeight: 700,
    color: "#1f2328",
    margin: "0 0 8px",
  },
  subtitle: {
    fontSize: 14,
    color: "#57606a",
    margin: "0 0 32px",
    lineHeight: 1.6,
  },
  stepList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
  },
  stepItem: {
    display: "flex",
    alignItems: "center",
    padding: "10px 0",
    borderBottom: "1px solid #f0f0f0",
  },
  stepLabel: {
    fontSize: 14,
    lineHeight: 1.5,
  },
  errorBox: {
    marginTop: 24,
    padding: 16,
    background: "#fff0f0",
    border: "1px solid #ffc1c1",
    borderRadius: 6,
    fontSize: 14,
    color: "#cf222e",
    lineHeight: 1.6,
  },
  retryBtn: {
    marginTop: 10,
    background: "none",
    border: "1px solid #cf222e",
    borderRadius: 4,
    padding: "4px 12px",
    cursor: "pointer",
    color: "#cf222e",
    fontSize: 13,
  },
  doneMsg: {
    marginTop: 24,
    color: "#1a7f37",
    fontWeight: 600,
    fontSize: 15,
  },
};
