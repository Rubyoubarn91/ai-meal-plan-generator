"""Macro math. Pure, testable, no floats where ints will do."""

from __future__ import annotations

from src.models.recipe import Recipe


def recipe_macros(recipe: Recipe) -> tuple[int, int, int]:
    """Return (calories, protein_g, carbs_g) for a recipe, rounded to int."""
    return (round(recipe.calories), round(recipe.protein_g), round(recipe.carbs_g))


def daily_totals(recipes: list[Recipe]) -> tuple[int, int, int]:
    """Sum macros across a day's recipes."""
    cals = sum(round(r.calories) for r in recipes)
    protein = sum(round(r.protein_g) for r in recipes)
    carbs = sum(round(r.carbs_g) for r in recipes)
    return cals, protein, carbs


def macro_split(recipe: Recipe) -> tuple[float, float, float]:
    """Return (protein_pct, carb_pct, fat_pct) as fractions of total calories.

    Uses 4/4/9 kcal-per-gram. Returns (0,0,0) for a zero-calorie recipe.
    """
    total = recipe.protein_g * 4 + recipe.carbs_g * 4 + recipe.fat_g * 9
    if total <= 0:
        return (0.0, 0.0, 0.0)
    return (
        (recipe.protein_g * 4) / total,
        (recipe.carbs_g * 4) / total,
        (recipe.fat_g * 9) / total,
    )