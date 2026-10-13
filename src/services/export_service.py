"""Export service. Writes plans to disk in a few formats.

All writes go under `data/exports/`. Path is sanitized — the plan id is the
only user-influenced component and it must match `[a-z0-9-]+`.
"""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

from src.models.plan import MealPlan

_SAFE_ID = re.compile(r"^[a-z0-9\-]{1,64}$")


class ExportService:
    """Serializes a MealPlan to JSON, CSV, or a plain-text shopping list."""

    def __init__(self, export_dir: Path) -> None:
        self._export_dir = export_dir
        self._export_dir.mkdir(parents=True, exist_ok=True)

    def to_json(self, plan: MealPlan) -> Path:
        target = self._safe_path(plan.id, "json")
        target.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        return target

    def to_csv(self, plan: MealPlan) -> Path:
        target = self._safe_path(plan.id, "csv")
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["day", "meal", "calories", "protein_g", "carbs_g", "fat_g"])
        for day in plan.days:
            for meal in day.meals:
                writer.writerow(
                    [
                        day.day_index,
                        meal.name,
                        round(meal.calories),
                        round(meal.protein_g),
                        round(meal.carbs_g),
                        round(meal.fat_g),
                    ]
                )
        target.write_text(buf.getvalue(), encoding="utf-8")
        return target

    def to_shopping_list(self, plan: MealPlan) -> Path:
        target = self._safe_path(plan.id, "txt")
        seen: dict[str, int] = {}
        for day in plan.days:
            for meal in day.meals:
                seen[meal.name] = seen.get(meal.name, 0) + meal.servings
        lines = [f"{count}x {name}" for name, count in sorted(seen.items())]
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target

    def _safe_path(self, plan_id: str, ext: str) -> Path:
        if not _SAFE_ID.match(plan_id):
            raise ValueError(f"unsafe plan id: {plan_id!r}")
        return self._export_dir / f"{plan_id}.{ext}"