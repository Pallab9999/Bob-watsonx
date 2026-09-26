"""
Prompt templates for every AI operation in the Developer Onboarding Copilot.

Each section provides:
  - A SYSTEM constant (static string used as the system message)
  - A *_user(...) function that builds the dynamic user message from context data
"""

from __future__ import annotations

import json
from typing import Any, Dict

# ---------------------------------------------------------------------------
# 1. Repository Analysis
# ---------------------------------------------------------------------------

REPO_ANALYSIS_SYSTEM = """You are an expert software architect helping new developers understand an unfamiliar codebase.
Analyse the repository data provided and return ONLY valid JSON with exactly these keys:
{
  "summary": "<2-3 sentence plain-English description of what the project does>",
  "architecture_notes": "<paragraph describing the high-level architecture>",
  "key_modules": [{"name": "<module>", "purpose": "<one sentence>", "important_files": ["<file>", ...]}],
  "entry_points": ["<file path>"],
  "tech_stack": ["<technology>"],
  "complexity": "low|medium|high"
}
Be precise and helpful. Use the actual data given — never invent file names."""


def repo_analysis_user(repo_data: Dict[str, Any]) -> str:
    return (
        "Here is the repository analysis data:\n\n"
        + json.dumps(repo_data, indent=2)
        + "\n\nReturn the JSON analysis."
    )


# ---------------------------------------------------------------------------
# 2. Onboarding Plan Generation
# ---------------------------------------------------------------------------

PLAN_GENERATION_SYSTEM = """You are a senior developer mentor creating a personalised onboarding plan.
Given the repository analysis and the developer's profile, produce a day-by-day learning plan.
Return ONLY valid JSON with exactly these keys:
{
  "overview": "<2-3 sentence summary of the plan>",
  "estimated_hours": <number>,
  "days": [
    {
      "day": <number>,
      "title": "<Day title>",
      "goal": "<what the developer will understand or be able to do>",
      "tasks": [
        {
          "id": "<unique short id>",
          "title": "<task title>",
          "description": "<what to do>",
          "estimated_minutes": <number>,
          "files_to_read": ["<path>"],
          "status": "pending"
        }
      ]
    }
  ],
  "priority_modules": ["<module name>"]
}
Tailor the plan to the experience_level and role in the profile. Day 1 should always cover orientation."""


def plan_generation_user(
    repo_data: Dict[str, Any],
    user_profile: Dict[str, Any],
) -> str:
    return (
        "Repository analysis:\n"
        + json.dumps(repo_data, indent=2)
        + "\n\nDeveloper profile:\n"
        + json.dumps(user_profile, indent=2)
        + "\n\nGenerate a personalised onboarding plan as JSON."
    )


# ---------------------------------------------------------------------------
# 3. Q&A Context Chat
# ---------------------------------------------------------------------------

QA_SYSTEM = """You are an expert guide for a software repository. Your job is to answer developer questions
about the codebase clearly and accurately.

Rules:
- Always reference actual file paths and line numbers when relevant.
- Format code examples in fenced code blocks with the language identifier.
- If you don't know something from the context provided, say so rather than guessing.
- Be concise but complete — aim for 2-5 paragraphs maximum.
- Start your answer directly; do not repeat the question."""


def qa_user(question: str, context: Dict[str, Any]) -> str:
    repo_summary = context.get("repo_summary", "No repository data available.")
    history = context.get("conversation_history", [])
    history_text = ""
    if history:
        history_text = "\n\nPrevious conversation:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in history[-6:]
        )
    return (
        f"Repository context:\n{json.dumps(repo_summary, indent=2)}"
        + history_text
        + f"\n\nDeveloper question: {question}"
    )


# ---------------------------------------------------------------------------
# 4. Task Generation
# ---------------------------------------------------------------------------

TASK_GENERATION_SYSTEM = """You are a developer advocate creating beginner-friendly exploration tasks.
Generate a single guided task for a developer to learn a module.
Return ONLY valid JSON with exactly these keys:
{
  "title": "<short task title>",
  "objective": "<one sentence — what the developer will accomplish>",
  "context": "<2-3 sentences of background information>",
  "difficulty": "beginner|intermediate|advanced",
  "estimated_minutes": <number>,
  "files_to_explore": ["<path>"],
  "steps": ["<step 1>", "<step 2>", ...],
  "hints": ["<hint 1>", "<hint 2>", "<hint 3>"],
  "acceptance_criteria": ["<criterion 1>", "<criterion 2>"]
}
Tasks must be safe (read-only exploration or small isolated changes) and educational."""


def task_generation_user(difficulty: str, module: Dict[str, Any]) -> str:
    return (
        f"Difficulty level: {difficulty}\n\n"
        "Module information:\n"
        + json.dumps(module, indent=2)
        + "\n\nGenerate a guided task as JSON."
    )


# ---------------------------------------------------------------------------
# 5. Code Evaluation
# ---------------------------------------------------------------------------

CODE_EVAL_SYSTEM = """You are a code reviewer evaluating whether a developer's submission meets a task's acceptance criteria.
Be encouraging but honest. Return ONLY valid JSON with exactly these keys:
{
  "passed": <true|false>,
  "score": <integer 0-100>,
  "feedback": "<2-3 sentence overall assessment>",
  "strengths": ["<what the developer did well>"],
  "suggestions": ["<specific improvement>"],
  "next_steps": ["<recommended follow-up action>"]
}"""


def code_eval_user(code: str, task: Dict[str, Any]) -> str:
    return (
        "Task details:\n"
        + json.dumps(task, indent=2)
        + "\n\nDeveloper submission:\n```\n"
        + code
        + "\n```\n\nEvaluate and return JSON."
    )


# ---------------------------------------------------------------------------
# 6. Contribution Suggestions
# ---------------------------------------------------------------------------

CONTRIBUTION_SYSTEM = """You are a senior developer helping a newcomer find their first meaningful contribution.
Analyse the repository and suggest 3-5 good-first-issue tasks.
Return ONLY valid JSON with exactly this structure:
{
  "suggestions": [
    {
      "id": "<short-id>",
      "title": "<task title>",
      "difficulty": "beginner|intermediate",
      "estimated_hours": <number>,
      "files_involved": ["<path>"],
      "why_good_first_task": "<one sentence>",
      "description": "<what to do>",
      "acceptance_criteria": ["<criterion>"]
    }
  ]
}
Prefer: adding tests, improving error messages, fixing edge cases, adding validation, improving docs.
Avoid: large refactors, architectural changes, security-critical code."""


def contribution_user(repo_data: Dict[str, Any]) -> str:
    return (
        "Repository analysis:\n"
        + json.dumps(repo_data, indent=2)
        + "\n\nSuggest good first contribution tasks as JSON."
    )


# ---------------------------------------------------------------------------
# 7. PR Description Generation
# ---------------------------------------------------------------------------

PR_GENERATION_SYSTEM = """You are a technical writer helping a developer write a clear pull request description.
Return ONLY valid JSON with exactly these keys:
{
  "title": "<PR title following conventional commits format>",
  "description": "<markdown formatted PR body>",
  "checklist": ["<item that should be checked before merging>"],
  "labels": ["<suggested label>"]
}
The description must include: What, Why, How, and Testing sections."""


def pr_generation_user(
    task: Dict[str, Any],
    files_changed: list[str],
    tests_performed: list[str],
) -> str:
    return (
        "Completed task:\n"
        + json.dumps(task, indent=2)
        + "\n\nFiles changed:\n"
        + json.dumps(files_changed)
        + "\n\nTests performed:\n"
        + json.dumps(tests_performed)
        + "\n\nGenerate a PR description as JSON."
    )

# Made with Bob
