"""
Plan Generator for the Developer Onboarding Copilot.

Combines raw repository analysis data (from Developer A's repo_analyzer)
with the user's profile to produce and persist a personalised learning plan.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from ..ai.provider import ai_provider

logger = logging.getLogger(__name__)

# In-memory store for MVP (swap for a database in production)
_plans: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def generate_plan(
    repo_id: str,
    repo_data: Dict[str, Any],
    user_profile: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate a personalised onboarding plan and persist it.

    Args:
        repo_id: Identifier of the analysed repository.
        repo_data: Structured dict from the repo analyser containing
                   languages, frameworks, directory structure, entry points, etc.
        user_profile: Dict with keys:
                      - experience_level: "beginner" | "intermediate" | "advanced"
                      - role: "frontend" | "backend" | "fullstack" | "data" | "devops"
                      - goal: Optional free-text description of what the developer wants to achieve.

    Returns:
        The complete plan dict including a newly assigned ``plan_id``.
    """
    logger.info(
        "Generating onboarding plan for repo_id=%s, profile=%s",
        repo_id,
        user_profile,
    )

    # 1. Ask AI for the plan structure
    ai_plan = await ai_provider.generate_onboarding_plan(repo_data, user_profile)

    # 2. Enrich with metadata
    plan_id = str(uuid.uuid4())
    plan = {
        "plan_id": plan_id,
        "repo_id": repo_id,
        "user_profile": user_profile,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "status": "active",
        **ai_plan,
    }

    # Ensure every task has a unique id
    for day in plan.get("days", []):
        for task in day.get("tasks", []):
            if not task.get("id"):
                task["id"] = str(uuid.uuid4())

    _plans[plan_id] = plan
    logger.info("Plan %s created with %d days", plan_id, len(plan.get("days", [])))
    return plan


def get_plan(plan_id: str) -> Dict[str, Any] | None:
    """Retrieve a previously generated plan by its ID."""
    return _plans.get(plan_id)


def list_plans_for_repo(repo_id: str) -> List[Dict[str, Any]]:
    """Return all plans generated for a given repository."""
    return [p for p in _plans.values() if p.get("repo_id") == repo_id]


async def customize_plan(
    plan_id: str,
    customizations: Dict[str, Any],
) -> Dict[str, Any] | None:
    """
    Apply developer-requested customisations to an existing plan.

    Supported customisations:
      - ``focus_modules``: list of module names to prioritise
      - ``skip_days``: list of day numbers to remove
      - ``add_goal``: free-text additional goal to factor into the plan

    Returns the updated plan or None if the plan_id is not found.
    """
    plan = _plans.get(plan_id)
    if plan is None:
        return None

    focus = customizations.get("focus_modules", [])
    skip_days = set(customizations.get("skip_days", []))

    if skip_days:
        plan["days"] = [d for d in plan.get("days", []) if d["day"] not in skip_days]

    if focus:
        # Move days that mention focused modules to the front
        def _score(day: Dict[str, Any]) -> int:
            text = str(day).lower()
            return sum(1 for m in focus if m.lower() in text)

        plan["days"] = sorted(plan["days"], key=_score, reverse=True)

    add_goal = customizations.get("add_goal")
    if add_goal:
        plan["overview"] = (plan.get("overview", "") + f"\n\nAdditional goal: {add_goal}").strip()

    plan["updated_at"] = datetime.utcnow().isoformat() + "Z"
    _plans[plan_id] = plan
    return plan


def update_task_status(
    plan_id: str,
    task_id: str,
    status: str,
) -> Dict[str, Any] | None:
    """
    Update the status of a single task within a plan.

    Args:
        plan_id: Plan identifier.
        task_id: Task identifier.
        status: New status — "pending" | "in_progress" | "completed".

    Returns:
        The updated task dict, or None if not found.
    """
    plan = _plans.get(plan_id)
    if plan is None:
        return None

    for day in plan.get("days", []):
        for task in day.get("tasks", []):
            if task.get("id") == task_id:
                task["status"] = status
                plan["updated_at"] = datetime.utcnow().isoformat() + "Z"
                return task
    return None


def calculate_progress(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate completion progress for a plan.

    Returns:
        Dict with ``total``, ``completed``, ``in_progress``, ``percent`` keys.
    """
    total = completed = in_progress = 0
    for day in plan.get("days", []):
        for task in day.get("tasks", []):
            total += 1
            s = task.get("status", "pending")
            if s == "completed":
                completed += 1
            elif s == "in_progress":
                in_progress += 1

    percent = round(completed / total * 100) if total else 0
    return {
        "total": total,
        "completed": completed,
        "in_progress": in_progress,
        "pending": total - completed - in_progress,
        "percent": percent,
    }

# Made with Bob
