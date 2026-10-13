"""LLM recipe adapter. Turns a prompt into structured recipes.

The LLM is asked for strict JSON. We validate every item through the Recipe
model before it reaches the pool — a malformed item is dropped, not raised on.
"""

from __future__ import annotations

from collections.abc import Iterator

import httpx

from src.models.recipe import Recipe

_SYSTEM_PROMPT = (
    "You output only JSON. Return an object with key 'recipes', an array of "
    "objects with keys: id, name, calories, protein_g, carbs_g, fat_g, "
    "allergens (array), diet (array). No prose."
)


class LlmRecipeSource:
    """Calls an OpenAI-compatible chat endpoint.

    *httpx: the LLM endpoint may stream; we disable streaming and rely on the
    read timeout to bail on a stalled generation.*
    """

    def __init__(self, endpoint: str, api_key: str, timeout_s: float = 30.0) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._timeout = httpx.Timeout(timeout_s, connect=3.0)

    def fetch(self) -> Iterator[Recipe]:
        if not self._api_key:
            return
        body = {
            "model": "planner-v1",
            "stream": False,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": "Give me 40 healthy dinner recipes."},
            ],
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.post(self._endpoint, json=body, headers=headers)
                resp.raise_for_status()
                payload = resp.json()
        except (httpx.HTTPError, ValueError):
            return

        content = payload["choices"][0]["message"]["content"]
        import json

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return
        for item in parsed.get("recipes", []):
            try:
                yield Recipe(
                    id=item["id"],
                    name=item["name"],
                    calories=float(item["calories"]),
                    protein_g=float(item.get("protein_g", 0)),
                    carbs_g=float(item.get("carbs_g", 0)),
                    fat_g=float(item.get("fat_g", 0)),
                    allergen_tags=frozenset(item.get("allergens", [])),
                    diet_tags=frozenset(item.get("diet", [])),
                    source="llm",
                )
            except (KeyError, TypeError, ValueError):
                continue