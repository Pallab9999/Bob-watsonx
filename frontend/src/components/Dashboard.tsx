import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import type { OnboardingPlan, UserProfile, PlanProgress, OnboardingTask } from "../types";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface LocationState {
  plan: OnboardingPlan;
  repoData: Record<string, unknown>;
  userProfile: UserProfile;
  progress?: PlanProgress;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as LocationState | null;

  if (!state?.plan) {
    return (
      <div style={styles.center}>
        <p style={{ color: "#57606a" }}>No plan loaded.</p>
        <button style={styles.btnPrimary} onClick={() => navigate("/input")}>
          Start onboarding
        </button>
      </div>
    );
  }

  const { plan, repoData } = state;

  const totalTasks = plan.days.reduce((n, d) => n + d.tasks.length, 0);
  const completedTasks = plan.days.reduce(
    (n, d) => n + d.tasks.filter((t) => t.status === "completed").length,
    0
  );
  const percent = totalTasks ? Math.round((completedTasks / totalTasks) * 100) : 0;

  const techStack: string[] =
    (repoData?.languages as string[]) ??
    (repoData?.tech_stack as string[]) ??
    [];

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.repoTitle}>{plan.repo_id}</h1>
          <p style={styles.repoSubtitle}>
            {plan.user_profile.role} · {plan.user_profile.experience_level}
          </p>
        </div>
        <button
          style={styles.btnPrimary}
          onClick={() => navigate("/plan", { state })}
        >
          Continue Onboarding →
        </button>
      </header>

      {/* Overview */}
      <p style={styles.overview}>{plan.overview}</p>

      {/* Tech stack badges */}
      {techStack.length > 0 && (
        <div style={styles.badgeRow}>
          {techStack.map((t) => (
            <span key={t} style={styles.badge}>{t}</span>
          ))}
        </div>
      )}

      {/* Progress bar */}
      <section style={styles.progressSection}>
        <div style={styles.progressHeader}>
          <span style={styles.sectionLabel}>Overall Progress</span>
          <span style={styles.progressPct}>{percent}%</span>
        </div>
        <div style={styles.progressTrack}>
          <div style={{ ...styles.progressFill, width: `${percent}%` }} />
        </div>
        <p style={styles.progressCaption}>
          {completedTasks} of {totalTasks} tasks completed
        </p>
      </section>

      {/* Day cards */}
      <section>
        <h2 style={styles.sectionTitle}>Your Learning Path</h2>
        <div style={styles.dayGrid}>
          {plan.days.map((day) => {
            const done = day.tasks.filter((t) => t.status === "completed").length;
            const total = day.tasks.length;
            const pct = total ? Math.round((done / total) * 100) : 0;
            return (
              <div key={day.day} style={styles.dayCard}>
                <div style={styles.dayBadge}>Day {day.day}</div>
                <h3 style={styles.dayTitle}>{day.title}</h3>
                <p style={styles.dayGoal}>{day.goal}</p>
                <div style={styles.dayProgressRow}>
                  <div style={styles.dayProgressTrack}>
                    <div style={{ ...styles.dayProgressFill, width: `${pct}%` }} />
                  </div>
                  <span style={styles.dayProgressLabel}>{done}/{total}</span>
                </div>
                <TaskPreviewList tasks={day.tasks} />
              </div>
            );
          })}
        </div>
      </section>

      {/* Quick actions */}
      <section style={styles.actionsRow}>
        <ActionCard
          title="Explore Codebase"
          desc="Navigate the directory structure and key modules."
          onClick={() => navigate("/map", { state })}
        />
        <ActionCard
          title="Ask the Codebase"
          desc="Chat with AI about any part of the repository."
          onClick={() => navigate("/chat", { state })}
        />
        <ActionCard
          title="Guided Tasks"
          desc="Complete hands-on tasks to build real understanding."
          onClick={() => navigate("/tasks", { state })}
        />
        <ActionCard
          title="First Contribution"
          desc="Find the perfect starter task to open your first PR."
          onClick={() => navigate("/contribute", { state })}
        />
      </section>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function TaskPreviewList({ tasks }: { tasks: OnboardingTask[] }) {
  return (
    <ul style={{ margin: "8px 0 0", padding: 0, listStyle: "none" }}>
      {tasks.slice(0, 3).map((t) => (
        <li key={t.id} style={styles.taskPreviewItem}>
          <StatusDot status={t.status} />
          <span style={styles.taskPreviewLabel}>{t.title}</span>
        </li>
      ))}
      {tasks.length > 3 && (
        <li style={{ ...styles.taskPreviewItem, color: "#57606a", fontSize: 12 }}>
          +{tasks.length - 3} more tasks
        </li>
      )}
    </ul>
  );
}

function StatusDot({ status }: { status: OnboardingTask["status"] }) {
  const color =
    status === "completed" ? "#1a7f37" :
    status === "in_progress" ? "#3b82d4" : "#d0d7de";
  return (
    <span
      style={{
        display: "inline-block",
        width: 8,
        height: 8,
        borderRadius: "50%",
        background: color,
        marginRight: 6,
        flexShrink: 0,
      }}
    />
  );
}

function ActionCard({
  title,
  desc,
  onClick,
}: {
  title: string;
  desc: string;
  onClick: () => void;
}) {
  return (
    <button style={styles.actionCard} onClick={onClick}>
      <span style={styles.actionTitle}>{title}</span>
      <span style={styles.actionDesc}>{desc}</span>
    </button>
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
  center: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "60vh",
    gap: 16,
    fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 16,
    flexWrap: "wrap",
    gap: 12,
  },
  repoTitle: {
    fontSize: 24,
    fontWeight: 700,
    margin: 0,
  },
  repoSubtitle: {
    fontSize: 14,
    color: "#57606a",
    margin: "4px 0 0",
    textTransform: "capitalize",
  },
  overview: {
    fontSize: 15,
    lineHeight: 1.7,
    color: "#3b3f45",
    margin: "0 0 20px",
    padding: "16px",
    background: "#f7f8fa",
    borderLeft: "3px solid #3b82d4",
    borderRadius: "0 6px 6px 0",
  },
  badgeRow: {
    display: "flex",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 28,
  },
  badge: {
    background: "#eef2ff",
    color: "#3b5bdb",
    borderRadius: 4,
    padding: "3px 10px",
    fontSize: 12,
    fontWeight: 600,
  },
  progressSection: {
    marginBottom: 36,
  },
  progressHeader: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: 6,
  },
  sectionLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: "#57606a",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
  },
  progressPct: {
    fontSize: 13,
    fontWeight: 700,
    color: "#1f2328",
  },
  progressTrack: {
    background: "#e5e7eb",
    borderRadius: 4,
    height: 8,
    overflow: "hidden",
  },
  progressFill: {
    background: "#3b82d4",
    height: "100%",
    borderRadius: 4,
    transition: "width 0.4s ease",
  },
  progressCaption: {
    fontSize: 12,
    color: "#57606a",
    margin: "6px 0 0",
  },
  sectionTitle: {
    fontSize: 17,
    fontWeight: 700,
    margin: "0 0 16px",
  },
  dayGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
    gap: 16,
    marginBottom: 36,
  },
  dayCard: {
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    padding: "20px",
    background: "#ffffff",
  },
  dayBadge: {
    display: "inline-block",
    background: "#f0f4ff",
    color: "#3b5bdb",
    borderRadius: 4,
    padding: "2px 8px",
    fontSize: 11,
    fontWeight: 700,
    marginBottom: 8,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  dayTitle: {
    fontSize: 15,
    fontWeight: 700,
    margin: "0 0 4px",
  },
  dayGoal: {
    fontSize: 13,
    color: "#57606a",
    lineHeight: 1.5,
    margin: "0 0 12px",
  },
  dayProgressRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
  },
  dayProgressTrack: {
    flex: 1,
    background: "#e5e7eb",
    borderRadius: 3,
    height: 5,
    overflow: "hidden",
  },
  dayProgressFill: {
    background: "#1a7f37",
    height: "100%",
    borderRadius: 3,
    transition: "width 0.3s ease",
  },
  dayProgressLabel: {
    fontSize: 11,
    color: "#57606a",
    minWidth: 28,
    textAlign: "right",
  },
  taskPreviewItem: {
    display: "flex",
    alignItems: "center",
    padding: "3px 0",
    fontSize: 13,
    color: "#3b3f45",
  },
  taskPreviewLabel: {
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  actionsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
    gap: 12,
  },
  actionCard: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: 4,
    padding: "16px 18px",
    border: "1px solid #e5e7eb",
    borderRadius: 8,
    background: "#ffffff",
    cursor: "pointer",
    textAlign: "left",
    transition: "border-color 0.15s",
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#1f2328",
  },
  actionDesc: {
    fontSize: 12,
    color: "#57606a",
    lineHeight: 1.4,
  },
  btnPrimary: {
    background: "#3b82d4",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "10px 20px",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
  },
};
