---
name: testing-qa
description: Run tests and quality checks. Use when user asks to "test the app", "run test suite", or "check coverage".
---

# Testing & QA

When active:
1. Unit: `bash scripts/run_tests.sh unit`
2. Integration: `bash scripts/run_tests.sh integration`
3. All: `bash scripts/run_tests.sh all`
4. Target 80%+ coverage, all pre-commit hooks passing
