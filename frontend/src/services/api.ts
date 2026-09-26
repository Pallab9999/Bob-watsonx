/**
 * API client for the Developer Onboarding Copilot backend.
 *
 * All methods return the inner payload directly (unwrapped from { success, ... })
 * and throw on errors so callers can use try/catch or React error boundaries.
 */

import type {
  UserProfile,
  RepoAnalysis,
  OnboardingPlan,
  PlanProgress,
  ValidationResult,
  ContributionSuggestion,
  PRDraft,
  GuidedTask,
} from "../types";

const BASE_URL = process.env.REACT_APP_API_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Internal helper
// ---------------------------------------------------------------------------

async function request<T>(
  method: "GET" | "POST" | "PATCH",
  path: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const json = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(json?.detail ?? `Request failed: ${res.status}`);
  }
  return json as T;
}

// ---------------------------------------------------------------------------
// API surface
// ---------------------------------------------------------------------------

export const api = {
  // ---- Repository analysis -----------------------------------------------

  /** Run AI analysis on raw repo data produced by Developer A's analyser. */
  async analyzeRepository(repoData: Record<string, unknown>): Promise<RepoAnalysis> {
    const res = await request<{ success: boolean; analysis: RepoAnalysis }>(
      "POST",
      "/api/analyze-repo",
      { repo_data: repoData }
    );
    return res.analysis;
  },

  // ---- Plan generation ---------------------------------------------------

  /** Generate a personalised onboarding plan. */
  async generatePlan(
    repoId: string,
    repoData: Record<string, unknown>,
    userProfile: UserProfile
  ): Promise<OnboardingPlan> {
    const res = await request<{ success: boolean; plan: OnboardingPlan }>(
      "POST",
      "/api/generate-plan",
      { repo_id: repoId, repo_data: repoData, user_profile: userProfile }
    );
    return res.plan;
  },

  /** Retrieve an existing plan with its current progress. */
  async getPlan(planId: string): Promise<{ plan: OnboardingPlan; progress: PlanProgress }> {
    return request<{ success: boolean; plan: OnboardingPlan; progress: PlanProgress }>(
      "GET",
      `/api/plan/${planId}`
    );
  },

  /** Customise an existing plan (focus modules, skip days, add goal). */
  async customizePlan(
    planId: string,
    opts: { focus_modules?: string[]; skip_days?: number[]; add_goal?: string }
  ): Promise<OnboardingPlan> {
    const res = await request<{ success: boolean; plan: OnboardingPlan }>(
      "POST",
      `/api/plan/${planId}/customize`,
      opts
    );
    return res.plan;
  },

  /** Update the status of a single task within a plan. */
  async updateTaskStatus(
    planId: string,
    taskId: string,
    status: "pending" | "in_progress" | "completed"
  ): Promise<void> {
    await request("PATCH", `/api/plan/${planId}/task-status`, {
      task_id: taskId,
      status,
    });
  },

  // ---- Chat --------------------------------------------------------------

  /** Send a question to the AI codebase assistant. */
  async chat(
    question: string,
    context: Record<string, unknown>
  ): Promise<string> {
    const res = await request<{ success: boolean; answer: string }>(
      "POST",
      "/api/chat",
      { question, context }
    );
    return res.answer;
  },

  // ---- Validation --------------------------------------------------------

  /** Validate code against a task. */
  async validate(
    task: GuidedTask,
    codeSubmission: string,
    opts?: { run_tests?: boolean; run_lint?: boolean }
  ): Promise<ValidationResult> {
    const res = await request<{ success: boolean; validation: ValidationResult }>(
      "POST",
      "/api/validate",
      {
        task,
        code_submission: codeSubmission,
        run_tests: opts?.run_tests ?? false,
        run_lint: opts?.run_lint ?? false,
      }
    );
    return res.validation;
  },

  /** Retrieve a stored validation result. */
  async getValidation(validationId: string): Promise<ValidationResult> {
    const res = await request<{ success: boolean; validation: ValidationResult }>(
      "GET",
      `/api/validation/${validationId}/status`
    );
    return res.validation;
  },

  // ---- Contributions -----------------------------------------------------

  /** Get good-first-task suggestions for a repository. */
  async suggestContributions(
    repoId: string,
    repoData: Record<string, unknown>
  ): Promise<{ suggestion_id: string; suggestions: ContributionSuggestion[] }> {
    return request("POST", "/api/contributions/suggest", {
      repo_id: repoId,
      repo_data: repoData,
    });
  },

  // ---- PR ----------------------------------------------------------------

  /** Generate a PR title and description for a completed task. */
  async generatePR(
    task: GuidedTask,
    filesChanged: string[],
    testsPerformed: string[]
  ): Promise<PRDraft> {
    const res = await request<{ success: boolean; pr: PRDraft }>(
      "POST",
      "/api/pr/generate",
      { task, files_changed: filesChanged, tests_performed: testsPerformed }
    );
    return res.pr;
  },

  /** Retrieve a stored PR draft. */
  async getPR(prId: string): Promise<PRDraft> {
    const res = await request<{ success: boolean; pr: PRDraft }>(
      "GET",
      `/api/pr/${prId}`
    );
    return res.pr;
  },
};
