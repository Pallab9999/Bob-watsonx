"""
AI Provider Interface for the Developer Onboarding Copilot.

Abstracts underlying LLM calls so the rest of the application is
decoupled from any specific vendor (OpenAI-compatible, IBM watsonx, etc.).

IBM watsonx notes
-----------------
The watsonx chat API lives at:
  POST  <host>/ml/v1/text/chat?version=2023-05-29
and requires:
  - Authorization: Bearer <IAM_TOKEN>   (exchanged from the raw API key)
  - project_id in the JSON body

Set the following environment variables:
  LLM_API_KEY    = your IBM Cloud API key
  LLM_BASE_URL   = https://us-south.ml.cloud.ibm.com   (host only, no path)
  LLM_MODEL      = ibm/granite-3-8b-instruct
  WATSONX_PROJECT_ID = your watsonx project ID

The provider detects watsonx automatically when LLM_BASE_URL contains
"ml.cloud.ibm.com" or when WATSONX_PROJECT_ID is set.

For a standard OpenAI-compatible endpoint just set:
  LLM_BASE_URL   = https://api.openai.com/v1
and the provider appends /chat/completions as normal.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read at import time so the module-level constants are
# available to contributions.py and any other callers.
# ---------------------------------------------------------------------------

LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
WATSONX_PROJECT_ID: str | None = os.getenv("WATSONX_PROJECT_ID")
WATSONX_API_VERSION: str = os.getenv("WATSONX_API_VERSION", "2023-05-29")

# IBM IAM token endpoint used to exchange an API key for a bearer token.
_IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

# Cached IAM bearer token (simple in-process cache; good enough for MVP).
_iam_token_cache: Optional[str] = None


# ---------------------------------------------------------------------------
# Watsonx detection
# ---------------------------------------------------------------------------

def _is_watsonx() -> bool:
    """Return True when the configured endpoint is IBM watsonx."""
    return (
        "ml.cloud.ibm.com" in LLM_BASE_URL
        or bool(WATSONX_PROJECT_ID)
    )


# ---------------------------------------------------------------------------
# IBM IAM token exchange
# ---------------------------------------------------------------------------

async def _get_iam_token() -> str:
    """
    Exchange the IBM Cloud API key for a short-lived IAM bearer token.

    The token is cached in-process for the lifetime of the server process.
    In production, add expiry checking; for the hackathon MVP this is fine.
    """
    global _iam_token_cache
    if _iam_token_cache:
        return _iam_token_cache

    if not LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY must be set to your IBM Cloud API key for watsonx"
        )

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                _IAM_TOKEN_URL,
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": LLM_API_KEY,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"IAM token exchange failed [{exc.response.status_code}]: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"IAM token exchange connection error: {exc}") from exc

    _iam_token_cache = resp.json()["access_token"]
    return _iam_token_cache


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

    Automatically routes to the IBM watsonx native chat API when the base URL
    is a watsonx host, otherwise uses the standard OpenAI-compatible path.

    Returns the assistant message content as a raw string.
    Raises RuntimeError on HTTP or parsing failures.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    if _is_watsonx():
        return await _watsonx_chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    return await _openai_chat(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=json_mode,
    )


async def _openai_chat(
    messages: list,
    *,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """Call a standard OpenAI-compatible /chat/completions endpoint."""
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    payload: Dict[str, Any] = {
        "model": LLM_MODEL,
        "messages": messages,
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


async def _watsonx_chat(
    messages: list,
    *,
    temperature: float,
    max_tokens: int,
) -> str:
    """
    Call the IBM watsonx native chat endpoint.

    Endpoint: POST <host>/ml/v1/text/chat?version=<WATSONX_API_VERSION>
    Auth:     Bearer <IAM token exchanged from the API key>
    Body:     { model_id, project_id, messages, parameters }
    """
    if not WATSONX_PROJECT_ID:
        raise RuntimeError(
            "WATSONX_PROJECT_ID must be set to use the IBM watsonx endpoint. "
            "Find it in your watsonx.ai project settings."
        )

    token = await _get_iam_token()

    # Strip any path suffix — we need the bare host
    base = LLM_BASE_URL.rstrip("/")
    # If the user accidentally kept /openai or /ml/v1/... strip it back to host
    for suffix in ("/ml/v1/openai", "/ml/v1", "/openai"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break

    url = f"{base}/ml/v1/text/chat"
    params = {"version": WATSONX_API_VERSION}

    payload: Dict[str, Any] = {
        "model_id": LLM_MODEL,
        "project_id": WATSONX_PROJECT_ID,
        "messages": messages,
        "parameters": {
            "temperature": temperature,
            "max_new_tokens": max_tokens,
        },
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        try:
            response = await client.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # IAM token may have expired — clear cache so next call re-exchanges
            global _iam_token_cache
            _iam_token_cache = None
            raise RuntimeError(
                f"watsonx request failed [{exc.response.status_code}]: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"watsonx connection error: {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected watsonx response structure: {data}") from exc


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
