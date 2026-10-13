"""Entry point. Boots settings, wires services, hands control to the CLI handler."""

from __future__ import annotations

import sys

from src.config.settings import load_settings
from src.handlers.cli_handler import CliHandler
from src.services.planner_service import PlannerService
from src.services.recipe_service import RecipeService
from src.utils.logging_setup import configure_logging


def main(argv: list[str] | None = None) -> int:
    """Bootstrap the app and dispatch to the CLI handler.

    Returns a POSIX exit code. Never raises past this boundary — the CLI is a
    user-facing surface and a stack trace is worse than an error line.
    """
    argv = argv if argv is not None else sys.argv[1:]
    settings = load_settings()
    configure_logging(settings.log_level, redact=settings.redact_keys)

    recipe_service = RecipeService.from_settings(settings)
    planner_service = PlannerService(settings=settings, recipes=recipe_service)
    handler = CliHandler(planner=planner_service, recipes=recipe_service)

    try:
        return handler.run(argv)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())