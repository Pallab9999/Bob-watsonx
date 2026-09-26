"""
AI Provider Interface for the Developer Onboarding Copilot.

Abstracts underlying LLM calls so the rest of the application is
decoupled from any specific vendor (OpenAI-compatible, IBM watsonx, etc.).
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

async def _chat_completion(
    system_prompt: str,
    user_message: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    """
    Send a single-turn chat completion request to the configured LLM endpoint.

    Returns the assistant message content as a raw string.
    Raises RuntimeError on HTTP or parsing failures.
    """
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
    }
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload: Dict[str, Any] = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    url = LLM_BASE_URL.rstrip("/") + "/chat/completions"

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"LLM request failed [{exc.response.status_code}]: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"LLM connection error: {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected LLM response structure: {data}") from exc


# ---------------------------------------------------------------------------
# Public AIProvider interface
# ---------------------------------------------------------------------------

class AIProvider:
    """
    High-level AI operations used by the onboarding copilot.

    All methods are async and return plain Python dicts so callers can
    serialise them directly into API responses.
    """

    # ------------------------------------------------------------------
    # Repository understanding
    # ------------------------------------------------------------------

    async def analyze_repository(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produce a human-readable narrative analysis of a repository.

        Args:
            repo_data: Structured dict produced by Developer A's repo_analyzer.

        Returns:
            Dict with keys: summary, architecture_notes, key_modules, entry_points.
        """
        from .prompts import REPO_ANALYSIS_SYSTEM, repo_analysis_user

        raw = await _chat_completion(
            REPO_ANALYSIS_SYSTEM,
            repo_analysis_user(repo_data),
            json_mode=True,
            max_tokens=1500,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON for analyze_repository; wrapping.")
            return {"summary": raw, "architecture_notes": "", "key_modules": [], "entry_points": []}

    # ------------------------------------------------------------------
    # Onboarding plan
    # ------------------------------------------------------------------

    async def generate_onboarding_plan(
        self,
        repo_data: Dict[str, Any],
        user_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a personalised day-by-day onboarding plan.

        Args:
            repo_data: Structured repository analysis dict.
            user_profile: Keys: experience_level, role, goal.

        Returns:
            Dict with keys: days (list), overview, estimated_hours.
        """
        from .prompts import PLAN_GENERATION_SYSTEM, plan_generation_user

        raw = await _chat_completion(
            PLAN_GENERATION_SYSTEM,
            plan_generation_user(repo_data, user_profile),
            json_mode=True,
            max_tokens=2048,
            temperature=0.5,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("LLM returned non-JSON for generate_onboarding_plan.")
            return {"days": [], "overview": raw, "estimated_hours": 0}

    # ------------------------------------------------------------------
    # Q&A chat
    # ------------------------------------------------------------------

    async def answer_question(
        self,
        question: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Answer a developer question given the repository context.

        Args:
            question: Free-text question from the developer.
            context: Dict containing repo_data and optional conversation_history.

        Returns:
            Markdown-formatted answer string.
        """
        from .prompts import QA_SYSTEM, qa_user

        return await _chat_completion(
            QA_SYSTEM,
            qa_user(question, context),
            max_tokens=1024,
            temperature=0.3,
        )

    # ------------------------------------------------------------------
    # Task generation
    # ------------------------------------------------------------------

    async def generate_task(
        self,
        difficulty: str,
        module: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a guided coding task for a specific module.

        Args:
            difficulty: "beginner" | "intermediate" | "advanced"
            module: Dict describing the module (name, purpose, files).

        Returns:
            Dict with keys: title, objective, context, hints, acceptance_criteria.
        """
        from .prompts import TASK_GENERATION_SYSTEM, task_generation_user

        raw = await _chat_completion(
            TASK_GENERATION_SYSTEM,
            task_generation_user(difficulty, module),
            json_mode=True,
            max_tokens=1024,
            temperature=0.6,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"title": "Explore the module", "objective": raw, "hints": [], "acceptance_criteria": []}

    # ------------------------------------------------------------------
    # Code evaluation
    # ------------------------------------------------------------------

    async def evaluate_code(
        self,
        code: str,
        task: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate submitted code against a task's acceptance criteria.

        Args:
            code: Developer-submitted code snippet or diff.
            task: The original task dict (title, objective, acceptance_criteria).

        Returns:
            Dict with keys: passed (bool), score (0-100), feedback, suggestions.
        """
        from .prompts import CODE_EVAL_SYSTEM, code_eval_user

        raw = await _chat_completion(
            CODE_EVAL_SYSTEM,
            code_eval_user(code, task),
            json_mode=True,
            max_tokens=1024,
            temperature=0.2,
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"passed": False, "score": 0, "feedback": raw, "suggestions": []}


# Singleton instance used throughout the app
ai_provider = AIProvider()

# Made with Bob
