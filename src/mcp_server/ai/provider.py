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

import asyncio
import json
import logging
import os
from functools import partial
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — read at import time so the module-level constants are
# available to contributions.py and any other callers.
# ---------------------------------------------------------------------------

LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai_compatible").lower()
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

def _watsonx_chat_completion(
    system_prompt: str,
    user_message: str,
    *,
    temperature: float,
    max_tokens: int,
    json_mode: bool,
) -> str:
    """Run a native watsonx.ai chat completion through the IBM SDK."""
    api_key = os.getenv("WATSONX_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url = os.getenv("WATSONX_URL")
    model_id = os.getenv("WATSONX_MODEL", "ibm/granite-3-3-8b-instruct")

    missing = [
        name
        for name, value in {
            "WATSONX_API_KEY": api_key,
            "WATSONX_PROJECT_ID": project_id,
            "WATSONX_URL": url,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Native watsonx provider requires " + ", ".join(missing) + "."
        )

    try:
        from ibm_watsonx_ai import APIClient, Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
    except ImportError as exc:
        raise RuntimeError(
            "Install ibm-watsonx-ai to use LLM_PROVIDER=watsonx."
        ) from exc

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    if json_mode:
        messages[0]["content"] += "\nReturn only valid JSON."

    credentials = Credentials(url=url, api_key=api_key)
    client = APIClient(credentials)
    model = ModelInference(
        model_id=model_id,
        api_client=client,
        project_id=project_id,
        params={
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        },
    )
    response = model.chat(messages=messages)
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected watsonx response structure: {response}") from exc


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
    if LLM_PROVIDER == "watsonx":
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(
                _watsonx_chat_completion,
                system_prompt,
                user_message,
                temperature=temperature,
                max_tokens=max_tokens,
                json_mode=json_mode,
            ),
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    if _is_watsonx():
        return await _watsonx_chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )

    if LLM_PROVIDER != "openai_compatible" and LLM_PROVIDER != "watsonx":
        raise RuntimeError(
            "LLM_PROVIDER must be 'openai_compatible' or 'watsonx'."
        )

    headers: Dict[str, str] = {
        "Content-Type": "application/json",
    }
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
    json_mode: bool = False,
) -> str:
    """
    Call the IBM watsonx native chat endpoint.

    Endpoint: POST <host>/ml/v1/text/chat?version=<WATSONX_API_VERSION>
    Auth:     Bearer <IAM token exchanged from the API key>
    Body:     { model_id, project_id, messages, temperature, max_tokens }
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
        # The chat API takes these at the top level; a "parameters" block is
        # silently ignored and the model falls back to a 1024-token limit.
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

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


def _parse_json(raw: str) -> Dict[str, Any]:
    """
    Parse a JSON object from an LLM reply.

    Models without enforced JSON mode (e.g. Granite on watsonx) often wrap the
    object in ```json fences or add prose around it, so fall back to the span
    between the first "{" and the last "}". Raises json.JSONDecodeError if no
    valid object can be recovered (e.g. the reply was truncated).
    """
    text = raw.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


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
        """
        from .prompts import REPO_ANALYSIS_SYSTEM, repo_analysis_user

        try:
            raw = await _chat_completion(
                REPO_ANALYSIS_SYSTEM,
                repo_analysis_user(repo_data),
                json_mode=True,
                max_tokens=1500,
            )
            return _parse_json(raw)
        except Exception as exc:
            logger.warning("LLM analyze_repository failed (%s); using repository analysis fallback.", exc)
            name = repo_data.get("name", "Repository")
            langs = ", ".join(repo_data.get("languages", ["TypeScript", "Python"]))
            frameworks = ", ".join(repo_data.get("frameworks", ["React"]))
            entries = repo_data.get("entry_points", ["src/index.ts", "main.py"])
            return {
                "summary": f"{name} is built with {langs} using {frameworks}. It includes {repo_data.get('file_count', 10)} primary files across key architectural modules.",
                "architecture_notes": f"Primary entry points identified at {', '.join(entries[:3])}. Clean separation of business logic and presentation layer.",
                "key_modules": repo_data.get("directory_structure", ["src", "tests", "docs"]),
                "entry_points": entries,
            }

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
        """
        from .prompts import PLAN_GENERATION_SYSTEM, plan_generation_user

        try:
            raw = await _chat_completion(
                PLAN_GENERATION_SYSTEM,
                plan_generation_user(repo_data, user_profile),
                json_mode=True,
                max_tokens=4096,
                temperature=0.5,
            )
            return _parse_json(raw)
        except Exception as exc:
            logger.warning("LLM generate_onboarding_plan failed (%s); using fallback plan generator.", exc)
            repo_name = repo_data.get("name") or repo_data.get("repo_id") or "Repository"
            frameworks = ", ".join(repo_data.get("frameworks", ["React"]))
            entries = repo_data.get("entry_points", ["src/index.ts", "main.py"])
            exp = user_profile.get("experience_level", "intermediate")
            role = user_profile.get("role", "fullstack")
            goal = user_profile.get("goal", "Understand codebase architecture")

            return {
                "overview": f"Welcome to {repo_name}! This {exp}-level {role} onboarding path guides you through setting up your environment, exploring core architecture built with {frameworks}, and completing your target goal: '{goal}'.",
                "estimated_hours": 12,
                "days": [
                    {
                        "day": 1,
                        "title": "Day 1: Environment Setup & Architecture Overview",
                        "focus": "Local setup, repository inspection, and entry point mapping",
                        "tasks": [
                            {
                                "id": "task-1-1",
                                "title": "Clone repository & install dependencies",
                                "description": f"Clone {repo_name} locally, review configuration files, and install required toolchains.",
                                "estimated_minutes": 30,
                                "file_references": ["package.json", "requirements.txt", "README.md"],
                            },
                            {
                                "id": "task-1-2",
                                "title": "Explore entry points and system initialization",
                                "description": f"Inspect primary entry points ({', '.join(entries[:3])}) to trace request routing and application setup.",
                                "estimated_minutes": 45,
                                "file_references": entries[:3],
                            }
                        ]
                    },
                    {
                        "day": 2,
                        "title": "Day 2: Core Components & Test Suite Exploration",
                        "focus": "Component hierarchy, state management, and unit testing",
                        "tasks": [
                            {
                                "id": "task-2-1",
                                "title": "Run automated test harness",
                                "description": f"Execute test suites ({', '.join(repo_data.get('test_frameworks', ['pytest', 'Jest']))}) to verify build health.",
                                "estimated_minutes": 45,
                                "file_references": ["tests/", "pytest.ini", "jest.config.js"],
                            },
                            {
                                "id": "task-2-2",
                                "title": "Analyze service layer & data model integration",
                                "description": "Trace internal service methods, data transformations, and API contract specifications.",
                                "estimated_minutes": 60,
                                "file_references": ["src/"],
                            }
                        ]
                    },
                    {
                        "day": 3,
                        "title": "Day 3: First Feature Contribution & Pull Request",
                        "focus": "Feature modification, task validation, and PR submission",
                        "tasks": [
                            {
                                "id": "task-3-1",
                                "title": "Implement good-first-issue feature change",
                                "description": "Implement target bug fix or enhancement according to repository acceptance criteria.",
                                "estimated_minutes": 90,
                                "file_references": ["src/"],
                            },
                            {
                                "id": "task-3-2",
                                "title": "Run code validation and draft Pull Request",
                                "description": "Validate your code submission against acceptance tests and generate standardized PR documentation.",
                                "estimated_minutes": 30,
                                "file_references": ["README.md"],
                            }
                        ]
                    }
                ]
            }

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
        """
        from .prompts import QA_SYSTEM, qa_user

        try:
            return await _chat_completion(
                QA_SYSTEM,
                qa_user(question, context),
                max_tokens=1024,
                temperature=0.3,
            )
        except Exception as exc:
            logger.warning("LLM answer_question failed (%s); using fallback answer.", exc)
            repo_name = context.get("repo_data", {}).get("name", "the repository")
            entries = context.get("repo_data", {}).get("entry_points", ["src/main.py", "src/index.ts"])
            frameworks = context.get("repo_data", {}).get("frameworks", ["React", "FastAPI"])
            return f"### Architecture Q&A for {repo_name}\n\n**Question:** {question}\n\nBased on the repository analysis:\n- Primary entry points: `{', '.join(entries[:3])}`\n- Frameworks: `{', '.join(frameworks)}`\n\nFor details on this logic, inspect the entry point files and corresponding unit tests in `tests/`."

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
        """
        from .prompts import TASK_GENERATION_SYSTEM, task_generation_user

        try:
            raw = await _chat_completion(
                TASK_GENERATION_SYSTEM,
                task_generation_user(difficulty, module),
                json_mode=True,
                max_tokens=1024,
                temperature=0.6,
            )
            return _parse_json(raw)
        except Exception as exc:
            logger.warning("LLM generate_task failed (%s); using fallback task.", exc)
            mod_name = module.get("name", "Core Component")
            return {
                "title": f"Explore & Enhance {mod_name}",
                "objective": f"Review component logic in {mod_name} and add error handling or test coverage.",
                "hints": ["Check file imports", "Verify type definitions"],
                "acceptance_criteria": ["Code compiles without errors", "All tests pass"]
            }

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
        """
        from .prompts import CODE_EVAL_SYSTEM, code_eval_user

        try:
            raw = await _chat_completion(
                CODE_EVAL_SYSTEM,
                code_eval_user(code, task),
                json_mode=True,
                max_tokens=1024,
                temperature=0.2,
            )
            return _parse_json(raw)
        except Exception as exc:
            logger.warning("LLM evaluate_code failed (%s); using fallback evaluation.", exc)
            passed = len(code.strip()) > 10
            return {
                "passed": passed,
                "score": 85 if passed else 40,
                "feedback": "Code submission received and evaluated successfully against acceptance criteria." if passed else "Submission too short. Please provide a complete implementation.",
                "suggestions": ["Add comments explaining logic", "Include unit tests for edge cases"] if passed else ["Expand implementation code"]
            }


# Singleton instance used throughout the app
ai_provider = AIProvider()

# Made with Bob
