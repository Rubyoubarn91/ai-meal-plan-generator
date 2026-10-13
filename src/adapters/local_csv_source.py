"""Local CSV recipe source. The offline fallback — always available."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

from src.models.recipe import Recipe


class LocalCsvSource:
    """Reads recipes from `data_dir/recipes.csv`.

    Expected columns: id,name,calories,protein_g,carbs_g,fat_g,allergens,diet.
    `allergens` and `diet` are pipe-separated. Missing file -> empty iterator.
    """

    def __init__(self, data_dir: str) -> None:
        self._path = Path(data_dir) / "recipes.csv"

    def fetch(self) -> Iterator[Recipe]:
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                yield Recipe(
                    id=row["id"],
                    name=row["name"],
                    calories=float(row["calories"]),
                    protein_g=float(row["protein_g"]),
                    carbs_g=float(row["carbs_g"]),
                    fat_g=float(row["fat_g"]),
                    allergen_tags=frozenset(filter(None, row.get("allergens", "").split("|"))),
                    diet_tags=frozenset(filter(None, row.get("diet", "").split("|"))),
                    source="local_csv",
                )