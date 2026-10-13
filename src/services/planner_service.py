"""Planner service. The brain of the app: profile + pool -> MealPlan."""

from __future__ import annotations

import random
import uuid
from datetime import date

from src.config.settings import Settings
from src.core.constraint_engine import ConstraintEngine
from src.core.nutrition_math import daily_totals
from src.models.plan import DayPlan, MealPlan
from src.models.profile import HealthProfile
from src.models.recipe import Recipe
from src.services.recipe_service import RecipeService


class PlannerService:
    """Builds a meal plan.

    Deterministic: same (profile, seed, pool) -> identical plan. The random
    module is seeded explicitly so tests can pin output.
    """

    def __init__(
        self,
        settings: Settings,
        recipes: RecipeService,
        engine: ConstraintEngine | None = None,
    ) -> None:
        self._settings = settings
        self._recipes = recipes
        self._engine = engine or ConstraintEngine()

    def generate(self, profile: HealthProfile, days: int | None = None) -> MealPlan:
        """Produce a plan for `days` days (default from settings)."""
        days = days or self._settings.default_days
        pool, rejected = self._engine.filter(self._recipes.pool(), profile)
        if not pool:
            raise ValueError(
                f"no recipes survive constraints ({len(rejected)} rejected); "
                "loosen allergens or widen the calorie band"
            )

        rng = random.Random(self._settings.planner_seed)
        day_plans: list[DayPlan] = []
        notes: list[str] = []

        for day_index in range(days):
            meals = self._pick_day(pool, profile, rng)
            day_plans.append(DayPlan(day_index=day_index, meals=meals))
            cals, _protein, _carbs = daily_totals(meals)
            drift = abs(cals - profile.daily_calorie_target) / profile.daily_calorie_target
            if drift > 0.15:
                notes.append(
                    f"day {day_index}: calorie drift {drift:.0%} "
                    f"({cals} vs {profile.daily_calorie_target})"
                )

        return MealPlan(
            id=str(uuid.uuid4()),
            created_on=date.today(),
            days=day_plans,
            seed=self._settings.planner_seed,
            notes=notes,
        )

    def _pick_day(
        self, pool: list[Recipe], profile: HealthProfile, rng: random.Random
    ) -> list[Recipe]:
        chosen: list[Recipe] = []
        used_ids: set[str] = set()
        for _ in range(profile.meals_per_day):
            candidates = [r for r in pool if r.id not in used_ids]
            if not candidates:
                break
            pick = rng.choice(candidates)
            chosen.append(pick)
            used_ids.add(pick.id)
        return chosen