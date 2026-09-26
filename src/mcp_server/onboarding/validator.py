"""
Validator for the Developer Onboarding Copilot.

Checks whether a developer's code changes satisfy a task's acceptance criteria
and provides structured feedback.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from ..ai.provider import ai_provider

logger = logging.getLogger(__name__)

# In-memory validation results store (replace with DB in production)
_validations: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def run_validation(
    task: Dict[str, Any],
    code_submission: str,
    *,
    run_tests: bool = False,
    run_lint: bool = False,
) -> Dict[str, Any]:
    """
    Validate a developer's code submission against a task.

    Args:
        task: The original task dict (title, objective, acceptance_criteria, etc.)
        code_submission: The developer's code or diff to evaluate.
        run_tests: Whether to simulate a test run check (MVP: always returns simulated result).
        run_lint: Whether to simulate a lint check (MVP: always returns simulated result).

    Returns:
        A validation result dict persisted in the in-memory store.
    """
    validation_id = str(uuid.uuid4())
    logger.info("Running validation %s for task '%s'", validation_id, task.get("title"))

    # --- AI evaluation ---
    ai_result = await ai_provider.evaluate_code(code_submission, task)

    # --- Simulated CI checks (MVP placeholders) ---
    checks: List[Dict[str, Any]] = [
        {
            "name": "AI Code Review",
            "status": "passed" if ai_result.get("passed") else "failed",
            "details": ai_result.get("feedback", ""),
        }
    ]

    if run_tests:
        checks.append({
            "name": "Unit Tests",
            "status": "passed",  # MVP: simulated
            "details": "All existing tests pass (simulated).",
        })

    if run_lint:
        checks.append({
            "name": "Lint",
            "status": "passed",  # MVP: simulated
            "details": "No lint errors detected (simulated).",
        })

    overall_passed = all(c["status"] == "passed" for c in checks)

    result: Dict[str, Any] = {
        "validation_id": validation_id,
        "task_id": task.get("id"),
        "task_title": task.get("title"),
        "submitted_at": datetime.utcnow().isoformat() + "Z",
        "status": "completed",
        "passed": overall_passed,
        "score": ai_result.get("score", 0),
        "checks": checks,
        "feedback": ai_result.get("feedback", ""),
        "strengths": ai_result.get("strengths", []),
        "suggestions": ai_result.get("suggestions", []),
        "next_steps": ai_result.get("next_steps", []),
    }

    _validations[validation_id] = result
    return result


def get_validation(validation_id: str) -> Dict[str, Any] | None:
    """Retrieve a stored validation result."""
    return _validations.get(validation_id)


def get_validations_for_task(task_id: str) -> List[Dict[str, Any]]:
    """Return all validation attempts for a given task."""
    return [v for v in _validations.values() if v.get("task_id") == task_id]

# Made with Bob
