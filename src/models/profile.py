"""User health profile. What the planner optimizes against."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class HealthProfile(BaseModel):
    """Everything the planner needs to know about the eater.

    `daily_calorie_target` is the ceiling, not a goal. The planner aims for
    +/-15% across the day, not per meal.
    """

    name: str = Field(default="default", max_length=80)
    daily_calorie_target: int = Field(ge=1200, le=5000)
    meals_per_day: int = Field(default=3, ge=2, le=6)
    min_protein_per_meal_g: float = Field(default=15.0, ge=0)
    allergens: frozenset[str] = Field(default_factory=frozenset)
    diet_pattern: Literal[
        "none", "vegan", "vegetarian", "keto", "mediterranean", "paleo", "halal", "kosher"
    ] = "none"
    cuisine_prefs: frozenset[str] = Field(default_factory=frozenset)

    @model_validator(mode="after")
    def _calorie_sanity(self) -> "HealthProfile":
        if self.daily_calorie_target < 1200 * self.meals_per_day / 3:
            raise ValueError("calorie target too low for the meal count")
        return self