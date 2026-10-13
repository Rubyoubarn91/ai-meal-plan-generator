"""Dietary + allergen constraint engine.

Pure functions. Every rule is a predicate over a Recipe. The engine composes
predicates into a filter and reports which rule rejected which recipe, so the
planner can explain itself.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from src.models.recipe import Recipe
from src.models.profile import HealthProfile

Rule = Callable[[Recipe, HealthProfile], bool]


@dataclass(frozen=True)
class Rejection:
    recipe_id: str
    rule_name: str
    reason: str


ALLERGEN_TAGS: dict[str, str] = {
    "peanut": "peanut",
    "tree_nut": "tree nut",
    "shellfish": "shellfish",
    "dairy": "dairy",
    "gluten": "gluten",
    "egg": "egg",
    "soy": "soy",
}


def _no_allergens(recipe: Recipe, profile: HealthProfile) -> bool:
    blocked = set(profile.allergens)
    return not (blocked & set(recipe.allergen_tags))


def _within_calorie_band(recipe: Recipe, profile: HealthProfile) -> bool:
    per_meal = profile.daily_calorie_target / profile.meals_per_day
    lo, hi = per_meal * 0.7, per_meal * 1.3
    return lo <= recipe.calories <= hi


def _meets_protein_floor(recipe: Recipe, profile: HealthProfile) -> bool:
    return recipe.protein_g >= profile.min_protein_per_meal_g


def _respects_diet_pattern(recipe: Recipe, profile: HealthProfile) -> bool:
    if profile.diet_pattern == "none":
        return True
    return profile.diet_pattern in recipe.diet_tags


DEFAULT_RULES: tuple[tuple[str, Rule], ...] = (
    ("no_allergens", _no_allergens),
    ("within_calorie_band", _within_calorie_band),
    ("meets_protein_floor", _meets_protein_floor),
    ("respects_diet_pattern", _respects_diet_pattern),
)


class ConstraintEngine:
    """Applies rules to recipes. Deterministic given the same inputs."""

    def __init__(self, rules: Iterable[tuple[str, Rule]] = DEFAULT_RULES) -> None:
        self._rules = tuple(rules)

    def filter(
        self, recipes: Iterable[Recipe], profile: HealthProfile
    ) -> tuple[list[Recipe], list[Rejection]]:
        kept: list[Recipe] = []
        rejected: list[Rejection] = []
        for recipe in recipes:
            failed = next(
                ((name, rule) for name, rule in self._rules if not rule(recipe, profile)),
                None,
            )
            if failed is None:
                kept.append(recipe)
            else:
                name, _ = failed
                rejected.append(
                    Rejection(recipe_id=recipe.id, rule_name=name, reason=f"failed {name}")
                )
        return kept, rejected

    def explain(self, recipe: Recipe, profile: HealthProfile) -> list[str]:
        """Return the names of every rule this recipe fails. Empty list == passes."""
        return [name for name, rule in self._rules if not rule(recipe, profile)]