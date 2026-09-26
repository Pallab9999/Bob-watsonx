import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

// Developer B components
import Analysis from "./components/Analysis";
import Dashboard from "./components/Dashboard";
import ChatInterface from "./components/ChatInterface";
import FirstContribution from "./components/FirstContribution";
import PRPreparation from "./components/PRPreparation";

// Developer A components (imported when available; stubbed here as placeholders)
// import Landing from "./components/Landing";
// import RepoInput from "./components/RepoInput";
// import CodebaseMap from "./components/CodebaseMap";
// import OnboardingPlan from "./components/OnboardingPlan";
// import TaskList from "./components/TaskList";

// ---------------------------------------------------------------------------
// Temporary placeholders for Dev A screens so routing works independently
// ---------------------------------------------------------------------------

const PlaceholderLanding = () => (
  <div style={pageStyle}>
    <h1 style={{ fontSize: 28, fontWeight: 700, margin: "0 0 12px" }}>
      Developer Onboarding Copilot
    </h1>
    <p style={{ color: "#57606a", marginBottom: 32 }}>
      Transform unfamiliar repositories into interactive learning journeys.
    </p>
    <a href="/input" style={btnStyle}>
      Start Onboarding →
    </a>
  </div>
);

const PlaceholderInput = () => (
  <div style={pageStyle}>
    <h2 style={{ marginBottom: 8 }}>Enter a Repository</h2>
    <p style={{ color: "#57606a", marginBottom: 24, fontSize: 14 }}>
      (Repository input form — implemented by Developer A)
    </p>
    {/* Direct navigation to Analysis with demo data for testing */}
    <a
      href="/analyze"
      style={btnStyle}
      onClick={(e) => {
        e.preventDefault();
        window.history.pushState(
          {
            repoId: "demo-repo",
            repoData: {
              languages: ["TypeScript", "Python"],
              frameworks: ["React", "FastAPI"],
              entry_points: ["src/index.ts", "main.py"],
              test_frameworks: ["Jest", "pytest"],
            },
            userProfile: {
              experience_level: "beginner",
              role: "fullstack",
              goal: "Understand the architecture and make my first contribution",
            },
          },
          "",
          "/analyze"
        );
        window.dispatchEvent(new PopStateEvent("popstate"));
      }}
    >
      Try Demo Repository →
    </a>
  </div>
);

// ---------------------------------------------------------------------------
// App Router
// ---------------------------------------------------------------------------

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Root */}
        <Route path="/" element={<PlaceholderLanding />} />

        {/* Repository input (Dev A) */}
        <Route path="/input" element={<PlaceholderInput />} />

        {/* Analysis loading screen (Dev B) */}
        <Route path="/analyze" element={<Analysis />} />

        {/* Dashboard (Dev B) */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* Codebase map (Dev A — placeholder redirect) */}
        <Route path="/map" element={<Navigate to="/dashboard" replace />} />

        {/* Onboarding plan (Dev A — placeholder redirect) */}
        <Route path="/plan" element={<Navigate to="/dashboard" replace />} />

        {/* Task list (Dev A — placeholder redirect) */}
        <Route path="/tasks" element={<Navigate to="/dashboard" replace />} />

        {/* AI Chat (Dev B) */}
        <Route path="/chat" element={<ChatInterface />} />

        {/* First contribution (Dev B) */}
        <Route path="/contribute" element={<FirstContribution />} />

        {/* PR preparation (Dev B) */}
        <Route path="/pr" element={<PRPreparation />} />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// ---------------------------------------------------------------------------
// Shared mini-styles (only for placeholder screens)
// ---------------------------------------------------------------------------

const pageStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "100vh",
  fontFamily: '-apple-system, "Segoe UI", system-ui, sans-serif',
  color: "#1f2328",
  textAlign: "center",
  padding: "0 24px",
};

const btnStyle: React.CSSProperties = {
  display: "inline-block",
  background: "#3b82d4",
  color: "#fff",
  borderRadius: 6,
  padding: "12px 28px",
  fontSize: 15,
  fontWeight: 600,
  textDecoration: "none",
};
