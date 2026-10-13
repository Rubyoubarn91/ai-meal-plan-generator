"""Recipe service. Owns the recipe pool and the adapters that populate it."""

from __future__ import annotations

from collections.abc import Iterable

from src.adapters.local_csv_source import LocalCsvSource
from src.adapters.llm_recipe_source import LlmRecipeSource
from src.adapters.nutrition_db_source import NutritionDbSource
from src.config.settings import Settings
from src.models.recipe import Recipe


class RecipeService:
    """Aggregates recipe sources behind one interface.

    Sources are tried in order; the first one that returns a non-empty pool
    wins. This keeps the app usable offline (local CSV) while letting the
    LLM source enrich when network is available.
    """

    def __init__(self, sources: Iterable[object], cache_dir: str) -> None:
        self._sources = tuple(sources)
        self._cache_dir = cache_dir
        self._pool: list[Recipe] | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> "RecipeService":
        sources: list[object] = [LocalCsvSource(data_dir=str(settings.data_dir))]
        if not settings.no_network:
            sources.append(NutritionDbSource(base_url=settings.nutrition_db_url))
            sources.append(
                LlmRecipeSource(endpoint=settings.llm_endpoint, api_key=settings.llm_api_key)
            )
        return cls(sources=sources, cache_dir=str(settings.data_dir))

    def pool(self) -> list[Recipe]:
        """Return the recipe pool, loading it on first call."""
        if self._pool is None:
            self._pool = self._load_pool()
        return self._pool

    def _load_pool(self) -> list[Recipe]:
        for source in self._sources:
            recipes = list(source.fetch())  # type: ignore[attr-defined]
            if recipes:
                return recipes
        return []

    def by_id(self, recipe_id: str) -> Recipe | None:
        return next((r for r in self.pool() if r.id == recipe_id), None)

    def search(self, query: str, limit: int = 20) -> list[Recipe]:
        q = query.lower().strip()
        if not q:
            return self.pool()[:limit]
        hits = [r for r in self.pool() if q in r.name.lower()]
        return hits[:limit]