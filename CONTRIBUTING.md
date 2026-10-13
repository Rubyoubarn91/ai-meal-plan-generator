# Contributing to ai-meal-plan-generator

Thanks for wanting to cook with us. This repo is a service-oriented Python
desktop tool that turns a pantry + a health profile into a week of meals.
Read this before you open a PR.

## Ground rules

- Python 3.11+. We use `ruff` for lint, `mypy --strict` for types, `pytest` for tests.
- Thin handlers. Fat services. If a handler has business logic in it, move it.
- Every service takes its dependencies as constructor args. No module-level singletons.
- Every external call (LLM, nutrition DB, grocery API) goes behind an adapter in `src/adapters/`.
- No new top-level dependency without a note in the PR description explaining what it replaces.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
pytest -q
ruff check src tests
mypy src
```

## Branch + commit style

- Branch: `feat/`, `fix/`, `chore/`, `docs/` prefix.
- Commits: imperative mood, one logical change per commit.
- PRs under 400 lines of diff get reviewed fastest.

## Adding a new meal source

1. Implement `MealSource` in `src/adapters/`.
2. Register it in `src/services/recipe_service.py`.
3. Add a fixture in `tests/fixtures/`.
4. Add one test proving the adapter maps raw payload -> `Recipe`.

## Adding a new dietary constraint

1. Add the rule to `src/core/constraint_engine.py`.
2. Cover it in `tests/test_constraint_engine.py`.
3. Document the rule in the docstring. We don't do tribal knowledge.

## What we won't merge

- Handler logic that belongs in a service.
- Hard-coded API keys. Use `src/config/settings.py`.
- Any change that makes the planner non-deterministic without a seed.