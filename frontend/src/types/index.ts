/**
 * Shared TypeScript types for the Developer Onboarding Copilot frontend.
 */

// ---------------------------------------------------------------------------
// User Profile
// ---------------------------------------------------------------------------

export type ExperienceLevel = "beginner" | "intermediate" | "advanced";
export type DeveloperRole = "frontend" | "backend" | "fullstack" | "data" | "devops";

export interface UserProfile {
  experience_level: ExperienceLevel;
  role: DeveloperRole;
  goal?: string;
}

// ---------------------------------------------------------------------------
// Repository
// ---------------------------------------------------------------------------

export interface Repository {
  repo_id: string;
  url: string;
  name: string;
  description?: string;
  languages: string[];
  frameworks: string[];
  entry_points: string[];
  directory_structure: DirectoryNode[];
  test_frameworks: string[];
  config_files: string[];
  analysed_at: string;
}

export interface DirectoryNode {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: DirectoryNode[];
  purpose?: string;
}

export interface RepoAnalysis {
  summary: string;
  architecture_notes: string;
  key_modules: KeyModule[];
  entry_points: string[];
  tech_stack: string[];
  complexity: "low" | "medium" | "high";
}

export interface KeyModule {
  name: string;
  purpose: string;
  important_files: string[];
}

// ---------------------------------------------------------------------------
// Onboarding Plan
// ---------------------------------------------------------------------------

export type TaskStatus = "pending" | "in_progress" | "completed";

export interface OnboardingTask {
  id: string;
  title: string;
  description: string;
  estimated_minutes: number;
  files_to_read: string[];
  status: TaskStatus;
}

export interface OnboardingDay {
  day: number;
  title: string;
  goal: string;
  tasks: OnboardingTask[];
}

export interface OnboardingPlan {
  plan_id: string;
  repo_id: string;
  user_profile: UserProfile;
  overview: string;
  estimated_hours: number;
  days: OnboardingDay[];
  priority_modules: string[];
  created_at: string;
  updated_at: string;
  status: "active" | "completed";
}

export interface PlanProgress {
  total: number;
  completed: number;
  in_progress: number;
  pending: number;
  percent: number;
}

// ---------------------------------------------------------------------------
// Task (guided tasks for Dev A's TaskList, also used in validation)
// ---------------------------------------------------------------------------

export interface GuidedTask {
  id: string;
  title: string;
  objective: string;
  context: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  estimated_minutes: number;
  files_to_explore: string[];
  steps: string[];
  hints: string[];
  acceptance_criteria: string[];
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

export interface ValidationCheck {
  name: string;
  status: "passed" | "failed" | "skipped";
  details: string;
}

export interface ValidationResult {
  validation_id: string;
  task_id?: string;
  task_title?: string;
  submitted_at: string;
  status: "completed" | "running";
  passed: boolean;
  score: number;
  checks: ValidationCheck[];
  feedback: string;
  strengths: string[];
  suggestions: string[];
  next_steps: string[];
}

// ---------------------------------------------------------------------------
// Contributions
// ---------------------------------------------------------------------------

export interface ContributionSuggestion {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate";
  estimated_hours: number;
  files_involved: string[];
  why_good_first_task: string;
  description: string;
  acceptance_criteria: string[];
}

// ---------------------------------------------------------------------------
// Pull Request
// ---------------------------------------------------------------------------

export interface PRDraft {
  pr_id: string;
  created_at: string;
  task_id?: string;
  task_title?: string;
  title: string;
  description: string;
  checklist: string[];
  labels: string[];
  files_changed: string[];
  tests_performed: string[];
}

// ---------------------------------------------------------------------------
// API response wrappers
// ---------------------------------------------------------------------------

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
