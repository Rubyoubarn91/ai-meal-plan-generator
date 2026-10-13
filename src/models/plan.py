"""A generated meal plan. Output of the planner, input to the exporter."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from src.models.recipe import Recipe


class DayPlan(BaseModel):
    day_index: int = Field(ge=0)
    meals: list[Recipe] = Field(default_factory=list)

    @property
    def total_calories(self) -> float:
        return sum(m.calories for m in self.meals)

    @property
    def total_protein_g(self) -> float:
        return sum(m.protein_g for m in self.meals)


class MealPlan(BaseModel):
    """A multi-day plan. Deterministic given (profile, seed, recipe pool)."""

    id: str
    created_on: date
    days: list[DayPlan]
    seed: int
    notes: list[str] = Field(default_factory=list)

    @property
    def total_days(self) -> int:
        return len(self.days)