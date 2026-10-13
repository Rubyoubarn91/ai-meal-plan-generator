"""CLI handler. Argparse in, service calls out, rich-formatted text to stdout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.models.profile import HealthProfile
from src.services.planner_service import PlannerService
from src.services.recipe_service import RecipeService


class CliHandler:
    """Dispatches CLI subcommands. Each branch is <= 10 lines."""

    def __init__(self, planner: PlannerService, recipes: RecipeService) -> None:
        self._planner = planner
        self._recipes = recipes
        self._console = Console()

    def run(self, argv: list[str]) -> int:
        parser = self._build_parser()
        args = parser.parse_args(argv)
        if args.command == "plan":
            return self._cmd_plan(args)
        if args.command == "search":
            return self._cmd_search(args)
        parser.print_help()
        return 0

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="mealplan")
        sub = parser.add_subparsers(dest="command")

        plan = sub.add_parser("plan", help="generate a meal plan")
        plan.add_argument("--profile", type=Path, required=True)
        plan.add_argument("--days", type=int, default=7)
        plan.add_argument("--json", action="store_true")

        search = sub.add_parser("search", help="search the recipe pool")
        search.add_argument("query")
        return parser

    def _cmd_plan(self, args: argparse.Namespace) -> int:
        profile = HealthProfile.model_validate_json(args.profile.read_text(encoding="utf-8"))
        plan = self._planner.generate(profile, days=args.days)
        if args.json:
            self._console.print_json(json.dumps(plan.model_dump(mode="json")))
        else:
            self._render_plan(plan)
        return 0

    def _cmd_search(self, args: argparse.Namespace) -> int:
        hits = self._recipes.search(args.query)
        for recipe in hits:
            self._console.print(f"{recipe.id}\t{recipe.name}\t{round(recipe.calories)} kcal")
        return 0

    def _render_plan(self, plan: object) -> None:
        table = Table(title=f"meal plan {plan.id[:8]}")  # type: ignore[attr-defined]
        table.add_column("day")
        table.add_column("meal")
        table.add_column("kcal", justify="right")
        for day in plan.days:  # type: ignore[attr-defined]
            for meal in day.meals:
                table.add_row(str(day.day_index), meal.name, str(round(meal.calories)))
        self._console.print(table)