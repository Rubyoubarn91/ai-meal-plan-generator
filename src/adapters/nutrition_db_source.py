"""Nutrition DB adapter. HTTP JSON over httpx."""

from __future__ import annotations

from collections.abc import Iterator

import httpx

from src.models.recipe import Recipe


class NutritionDbSource:
    """Pulls recipes from a nutrition DB.

    *httpx: set a client-level timeout — the default has no read timeout and
    will hang the planner on a dead endpoint.*
    """

    def __init__(self, base_url: str, timeout_s: float = 8.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = httpx.Timeout(timeout_s, connect=3.0)

    def fetch(self) -> Iterator[Recipe]:
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/recipes", params={"limit": 500})
                resp.raise_for_status()
                payload = resp.json()
        except (httpx.HTTPError, ValueError):
            return
        for item in payload.get("items", []):
            yield Recipe(
                id=item["id"],
                name=item["name"],
                calories=float(item["calories"]),
                protein_g=float(item.get("protein_g", 0)),
                carbs_g=float(item.get("carbs_g", 0)),
                fat_g=float(item.get("fat_g", 0)),
                allergen_tags=frozenset(item.get("allergens", [])),
                diet_tags=frozenset(item.get("diet", [])),
                source="nutrition_db",
            )