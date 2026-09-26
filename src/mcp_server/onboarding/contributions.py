"""
Contribution and PR logic for the Developer Onboarding Copilot.

Suggests good first issues based on the repository analysis and generates
pull-request descriptions once a developer completes a task.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from ..ai.provider import ai_provider
from ..ai.prompts import (
    CONTRIBUTION_SYSTEM,
    contribution_user,
    PR_GENERATION_SYSTEM,
    pr_generation_user,
)

logger = logging.getLogger(__name__)

# In-memory stores
_contribution_suggestions: Dict[str, Dict[str, Any]] = {}
_pr_drafts: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Public API — Contribution suggestions
# ---------------------------------------------------------------------------

async def suggest_contributions(
    repo_id: str,
    repo_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyse the repository and suggest 3-5 good first contribution tasks.

    Args:
        repo_id: Repository identifier.
        repo_data: Structured repository analysis dict.

    Returns:
        Dict with ``suggestion_id``, ``repo_id``, and ``suggestions`` list.
    """
    import json
    import httpx

    from ..ai.provider import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT

    logger.info("Generating contribution suggestions for repo_id=%s", repo_id)

    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": CONTRIBUTION_SYSTEM},
            {"role": "user", "content": contribution_user(repo_data)},
        ],
        "temperature": 0.5,
        "max_tokens": 1500,
        "response_format": {"type": "json_object"},
    }

    url = LLM_BASE_URL.rstrip("/") + "/chat/completions"
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    try:
        ai_result = json.loads(content)
    except json.JSONDecodeError:
        ai_result = {"suggestions": []}

    suggestion_id = str(uuid.uuid4())
    result = {
        "suggestion_id": suggestion_id,
        "repo_id": repo_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "suggestions": ai_result.get("suggestions", []),
    }
    _contribution_suggestions[suggestion_id] = result
    return result


def get_contribution_suggestions(suggestion_id: str) -> Dict[str, Any] | None:
    """Retrieve previously generated contribution suggestions."""
    return _contribution_suggestions.get(suggestion_id)


# ---------------------------------------------------------------------------
# Public API — PR description generation
# ---------------------------------------------------------------------------

async def generate_pr(
    task: Dict[str, Any],
    files_changed: List[str],
    tests_performed: List[str],
) -> Dict[str, Any]:
    """
    Generate a pull-request title and description for a completed task.

    Args:
        task: The completed task dict.
        files_changed: List of changed file paths.
        tests_performed: List of test descriptions performed.

    Returns:
        Dict with ``pr_id``, ``title``, ``description``, ``checklist``, ``labels``.
    """
    import json
    import httpx

    from ..ai.provider import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TIMEOUT

    logger.info("Generating PR description for task '%s'", task.get("title"))

    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": PR_GENERATION_SYSTEM},
            {
                "role": "user",
                "content": pr_generation_user(task, files_changed, tests_performed),
            },
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }

    url = LLM_BASE_URL.rstrip("/") + "/chat/completions"
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    content = response.json()["choices"][0]["message"]["content"]
    try:
        ai_result = json.loads(content)
    except json.JSONDecodeError:
        ai_result = {"title": task.get("title", "chore: update"), "description": "", "checklist": [], "labels": []}

    pr_id = str(uuid.uuid4())
    pr_draft = {
        "pr_id": pr_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "task_id": task.get("id"),
        "task_title": task.get("title"),
        "files_changed": files_changed,
        "tests_performed": tests_performed,
        **ai_result,
    }
    _pr_drafts[pr_id] = pr_draft
    return pr_draft


def get_pr_draft(pr_id: str) -> Dict[str, Any] | None:
    """Retrieve a generated PR draft."""
    return _pr_drafts.get(pr_id)

# Made with Bob
