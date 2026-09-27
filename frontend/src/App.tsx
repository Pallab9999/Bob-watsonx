import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";

// Developer B components
import Analysis from "./components/Analysis";
import Dashboard from "./components/Dashboard";
import ChatInterface from "./components/ChatInterface";
import FirstContribution from "./components/FirstContribution";
import PRPreparation from "./components/PRPreparation";

import type { ExperienceLevel, DeveloperRole } from "./types";

// ---------------------------------------------------------------------------
// GitHub API helpers
// ---------------------------------------------------------------------------

function parseGitHubUrl(url: string): { owner: string; repo: string } | null {
  try {
    const cleaned = url.trim().replace(/\/$/g, "").replace(/\.git$/g, "");
    const patterns = [
      /github\.com\/([^/]+)\/([^/]+)/,
      /^([^/]+)\/([^/]+)$/,
    ];
    for (const p of patterns) {
      const m = cleaned.match(p);
      if (m) return { owner: m[1], repo: m[2] };
    }
  } catch {}
  return null;
}

async function fetchRepoData(owner: string, repo: string) {
  const base = "https://api.github.com";

  const repoRes = await fetch(`${base}/repos/${owner}/${repo}`);
  if (!repoRes.ok) throw new Error(`Repository not found: ${owner}/${repo}`);
  const repoJson = await repoRes.json();

  const langsRes = await fetch(`${base}/repos/${owner}/${repo}/languages`);
  const langsJson = langsRes.ok ? await langsRes.json() : {};

  // Fetch top-level tree for entry points & structure
  let treeItems: any[] = [];
  try {
    const treeRes = await fetch(
      `${base}/repos/${owner}/${repo}/git/trees/${repoJson.default_branch}?recursive=1`
    );
    if (treeRes.ok) {
      const treeJson = await treeRes.json();
      treeItems = (treeJson.tree || []).slice(0, 200);
    }
  } catch {}

  const languages = Object.keys(langsJson);
  const files = treeItems.filter((t: any) => t.type === "blob").map((t: any) => t.path);

  // Detect frameworks from file names
  const frameworks: string[] = [];
  const fileList = files.join(" ").toLowerCase();
  if (fileList.includes("package.json")) {
    if (fileList.includes("next.config")) frameworks.push("Next.js");
    else if (fileList.includes("vite.config")) frameworks.push("Vite");
    else if (files.some((f: string) => f.includes("react"))) frameworks.push("React");
  }
  if (fileList.includes("requirements.txt") || fileList.includes("pyproject.toml")) {
    if (fileList.includes("fastapi")) frameworks.push("FastAPI");
    else if (fileList.includes("django")) frameworks.push("Django");
    else if (fileList.includes("flask")) frameworks.push("Flask");
    else frameworks.push("Python");
  }
  if (fileList.includes("go.mod")) frameworks.push("Go");
  if (fileList.includes("cargo.toml")) frameworks.push("Rust/Cargo");

  // Detect entry points
  const entryPatterns = [
    "main.py", "app.py", "index.ts", "index.js", "main.ts", "main.js",
    "src/index.ts", "src/index.js", "src/main.ts", "src/main.py",
    "server.py", "server.js", "server.ts", "manage.py",
  ];
  const entry_points = files.filter((f: string) =>
    entryPatterns.some((p) => f.toLowerCase().endsWith(p))
  ).slice(0, 10);

  // Detect test frameworks
  const test_frameworks: string[] = [];
  if (files.some((f: string) => /jest\.config|\.test\.(ts|js|tsx|jsx)$/.test(f))) test_frameworks.push("Jest");
  if (files.some((f: string) => /pytest\.ini|conftest\.py|test_.*\.py$/.test(f))) test_frameworks.push("pytest");
  if (files.some((f: string) => /\.spec\.(ts|js)$/.test(f))) test_frameworks.push("Vitest/Spec");

  // Build directory structure (top-level only)
  const dirs = Array.from(new Set(treeItems.filter((t: any) => t.type === "tree").map((t: any) => t.path.split("/")[0])));

  return {
    name: repoJson.full_name,
    description: repoJson.description || "",
    languages,
    frameworks: frameworks.length ? frameworks : languages.slice(0, 2),
    entry_points: entry_points.length ? entry_points : ["(auto-detected)"],
    test_frameworks: test_frameworks.length ? test_frameworks : ["(none detected)"],
    topics: repoJson.topics || [],
    stars: repoJson.stargazers_count,
    default_branch: repoJson.default_branch,
    directory_structure: dirs.slice(0, 20),
    file_count: files.length,
  };
}

// ---------------------------------------------------------------------------
// Landing Page
// ---------------------------------------------------------------------------

const Landing = () => {
  const navigate = useNavigate();
  return (
    <div style={pageStyle}>
      <div style={{ maxWidth: 600 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, margin: "0 0 12px", color: "#1f2328" }}>
          🚀 Developer Onboarding Copilot
        </h1>
        <p style={{ color: "#57606a", marginBottom: 36, fontSize: 16, lineHeight: 1.6 }}>
          Transform any unfamiliar GitHub repository into an interactive,
          personalised learning journey — from first clone to first contribution.
        </p>
        <button style={btnStyle} onClick={() => navigate("/input")}>
          Start Onboarding →
        </button>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Repo Input Page
// ---------------------------------------------------------------------------

const RepoInput = () => {
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState("");
  const [experience, setExperience] = useState<ExperienceLevel>("beginner");
  const [role, setRole] = useState<DeveloperRole>("fullstack");
  const [goal, setGoal] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsed = parseGitHubUrl(repoUrl);
    if (!parsed) {
      setError("Please enter a valid GitHub repository URL (e.g. https://github.com/owner/repo)");
      return;
    }

    setLoading(true);
    try {
      const repoData = await fetchRepoData(parsed.owner, parsed.repo);
      navigate("/analyze", {
        state: {
          repoId: `${parsed.owner}/${parsed.repo}`,
          repoData,
          userProfile: {
            experience_level: experience,
            role,
            goal: goal || "Understand the architecture and make my first contribution",
          },
        },
      });
    } catch (err: any) {
      setError(err.message || "Failed to fetch repository data. Check the URL and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={pageStyle}>
      <form onSubmit={handleSubmit} style={formStyle}>
        <h2 style={{ margin: "0 0 4px", fontSize: 22, fontWeight: 700 }}>
          Enter a GitHub Repository
        </h2>
        <p style={{ color: "#57606a", margin: "0 0 28px", fontSize: 14 }}>
          Paste a GitHub repo URL and we'll build your personalised onboarding plan.
        </p>

        {/* Repo URL */}
        <label style={labelStyle}>Repository URL</label>
        <input
          id="repo-url-input"
          type="text"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
          style={inputStyle}
          required
          autoFocus
        />

        {/* Experience Level */}
        <label style={labelStyle}>Experience Level</label>
        <select
          id="experience-select"
          value={experience}
          onChange={(e) => setExperience(e.target.value as ExperienceLevel)}
          style={inputStyle}
        >
          <option value="beginner">🌱 Beginner</option>
          <option value="intermediate">🌿 Intermediate</option>
          <option value="advanced">🌳 Advanced</option>
        </select>

        {/* Role */}
        <label style={labelStyle}>Role</label>
        <select
          id="role-select"
          value={role}
          onChange={(e) => setRole(e.target.value as DeveloperRole)}
          style={inputStyle}
        >
          <option value="fullstack">💻 Full Stack</option>
          <option value="frontend">🎨 Frontend</option>
          <option value="backend">⚙️ Backend</option>
          <option value="data">📊 Data</option>
          <option value="devops">🔧 DevOps</option>
        </select>

        {/* Goal */}
        <label style={labelStyle}>Goal (optional)</label>
        <input
          id="goal-input"
          type="text"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g. Understand the architecture and contribute a bug fix"
          style={inputStyle}
        />

        {error && (
          <div style={errorStyle}>{error}</div>
        )}

        <button
          type="submit"
          style={{ ...btnStyle, width: "100%", marginTop: 8, opacity: loading ? 0.7 : 1 }}
          disabled={loading}
        >
          {loading ? "Fetching repository..." : "Analyse Repository →"}
        </button>
      </form>
    </div>
  );
};

// ---------------------------------------------------------------------------
// App Router
// ---------------------------------------------------------------------------

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Root */}
        <Route path="/" element={<Landing />} />

        {/* Repository input */}
        <Route path="/input" element={<RepoInput />} />

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
// Shared styles
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
  background: "#f7f8fa",
};

const btnStyle: React.CSSProperties = {
  display: "inline-block",
  background: "#3b82d4",
  color: "#fff",
  border: "none",
  borderRadius: 6,
  padding: "12px 28px",
  fontSize: 15,
  fontWeight: 600,
  cursor: "pointer",
};

const formStyle: React.CSSProperties = {
  background: "#ffffff",
  border: "1px solid #e5e7eb",
  borderRadius: 10,
  padding: "36px 40px",
  maxWidth: 480,
  width: "100%",
  textAlign: "left",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: 13,
  fontWeight: 600,
  color: "#1f2328",
  marginBottom: 6,
  marginTop: 16,
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  fontSize: 14,
  border: "1px solid #d1d5db",
  borderRadius: 6,
  boxSizing: "border-box",
  fontFamily: "inherit",
  outline: "none",
};

const errorStyle: React.CSSProperties = {
  marginTop: 16,
  padding: "10px 14px",
  background: "#fff0f0",
  border: "1px solid #ffc1c1",
  borderRadius: 6,
  fontSize: 13,
  color: "#cf222e",
  lineHeight: 1.5,
};
