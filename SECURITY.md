# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

Do not open a public issue. Email `security@ai-meal-plan-generator.dev`
with a description, a repro, and the version. We acknowledge within 72h.

## Scope

In scope:
- Arbitrary code execution via recipe import files (`.recipe.json`, `.recipe.yaml`)
- Path traversal in the export pipeline (`src/services/export_service.py`)
- Prompt-injection that escapes the constraint engine and produces an
  allergen-containing plan
- Credential leakage in logs (`src/utils/logging_setup.py` must redact keys)

Out of scope:
- Nutrition accuracy of third-party sources
- Anything requiring local admin on the user's machine

## Hardening notes for users

- Run with `--no-network` to disable all outbound LLM/DB calls.
- Export files are written to `data/exports/` with `0600` on POSIX and
  owner-only ACL on Windows.
- The planner never executes recipe payloads. Import is data-only.