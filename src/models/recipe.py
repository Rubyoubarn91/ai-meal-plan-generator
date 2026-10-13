"""Recipe model. The atom of the whole app."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Recipe(BaseModel):
    """A single dish.

    `allergen_tags` uses the canonical vocabulary in `src/core/constraint_engine.py`.
    `diet_tags` uses free-form labels like "vegan", "keto", "mediterranean".
    """

    id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=200)
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    servings: int = Field(default=1, ge=1, le=12)
    prep_minutes: int = Field(default=10, ge=0, le=600)
    allergen_tags: frozenset[str] = Field(default_factory=frozenset)
    diet_tags: frozenset[str] = Field(default_factory=frozenset)
    source: str = Field(default="local")

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()

    def scaled(self, servings: int) -> "Recipe":
        """Return a copy with macros scaled to `servings`."""
        factor = servings / self.servings
        return self.model_copy(
            update={
                "servings": servings,
                "calories": self.calories * factor,
                "protein_g": self.protein_g * factor,
                "carbs_g": self.carbs_g * factor,
                "fat_g": self.fat_g * factor,
            }
        )