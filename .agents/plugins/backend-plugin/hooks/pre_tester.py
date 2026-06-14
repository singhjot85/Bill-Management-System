"""
pre_tester.py — BMA Backend Plugin Hook
========================================
Validates Coder subagent output before the Tester is invoked.

Position in pipeline: happy_path / full_implementation exit → before tester entry
Max retries: 2
On exceed: hard-stop, set plugin_state.json → blocked_on

Logs to: .agents/logs/<feature_slug>/<timestamp>_pre_tester.log
Stdout:   Structured JSON (read by orchestrator)

Usage:
    python .agents/plugins/backend-plugin/hooks/pre_tester.py \
        --coder-output <path_to_coder_output_file> \
        --plugin-state <path_to_plugin_state_json> \
        --log-dir <path_to_feature_log_dir> \
        --project-root <path_to_project_root>
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

MAX_RETRIES = 2

DOCKER_COMPOSE_CMD = ["docker", "compose", "exec", "backend"]

# Files the Coder is never allowed to touch during a backend-plugin session
# unless declared in inter_plugin_contracts
FORBIDDEN_PATH_PREFIXES = ["frontend/", "compose/", ".agents/"]

# ── Logging Setup ─────────────────────────────────────────────────────────────


class HookLogger:
    """
    Identical structure to pre_coder.py logger.
    Each hook owns its own log file. Timestamped per run.
    Partial logs are written immediately so crashes leave readable output.
    """

    def __init__(self, log_dir: Path, hook_start_time: float):
        self.hook_start_time = hook_start_time
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        self.log_path = log_dir / f"{timestamp}_pre_tester.log"
        self._write_header()

    def _append(self, line: str):
        with open(self.log_path, "a") as f:
            f.write(line + "\n")

    def section(self, title: str):
        self._append("")
        self._append(f"── {title} {'─' * max(0, 60 - len(title))}")

    def info(self, msg: str):
        elapsed = round(time.time() - self.hook_start_time, 3)
        self._append(f"  [{elapsed:>8.3f}s] INFO  {msg}")

    def warn(self, msg: str):
        elapsed = round(time.time() - self.hook_start_time, 3)
        self._append(f"  [{elapsed:>8.3f}s] WARN  {msg}")

    def error(self, msg: str):
        elapsed = round(time.time() - self.hook_start_time, 3)
        self._append(f"  [{elapsed:>8.3f}s] ERROR {msg}")

    def _write_header(self):
        self._append("=" * 70)
        self._append("BMA BACKEND PLUGIN — pre_tester HOOK")
        self._append(f"Run started : {datetime.now(timezone.utc).isoformat()}")
        self._append(f"Log file    : {self.log_path}")
        self._append("=" * 70)

    def write_footer(self, passed: bool, error_count: int, total_elapsed: float):
        self._append("")
        self._append("=" * 70)
        self._append(f"Result      : {'PASSED' if passed else 'FAILED'}")
        self._append(f"Errors      : {error_count}")
        self._append(f"Total time  : {total_elapsed:.3f}s")
        self._append(f"Run ended   : {datetime.now(timezone.utc).isoformat()}")
        self._append("=" * 70)


# ── Helpers ───────────────────────────────────────────────────────────────────


def run_in_docker(
    cmd: list[str], logger: HookLogger, timeout: int = 60
) -> tuple[int, str, str]:
    """
    Runs a command inside the backend Docker container.
    Returns (returncode, stdout, stderr).
    Logs the command and its output in full.
    """
    full_cmd = DOCKER_COMPOSE_CMD + cmd
    logger.info(f"Running: {' '.join(full_cmd)}")

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        logger.info(f"Exit code: {result.returncode}")
        if result.stdout:
            logger.info(f"stdout:\n{result.stdout}")
        if result.stderr:
            logger.warn(f"stderr:\n{result.stderr}")
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {' '.join(full_cmd)}")
        return 1, "", f"Timeout after {timeout}s"
    except Exception as e:
        logger.error(f"Command failed to execute: {e}")
        return 1, "", str(e)


# ── Validation Checks ─────────────────────────────────────────────────────────


def check_handoff_block_present(
    coder_output: str, logger: HookLogger
) -> tuple[bool, list[str]]:
    """
    Check 1: Coder output contains a parseable CODER HANDOFF block.
    Extracts the list of files the Coder touched.
    Without this, we cannot verify what was actually changed.
    """
    logger.section("Check 1 — CODER HANDOFF block")

    pattern = r"=== CODER HANDOFF ===(.*?)=== END CODER HANDOFF ==="
    match = re.search(pattern, coder_output, re.DOTALL)

    if not match:
        logger.error("CODER HANDOFF block not found in output.")
        logger.error("Coder must end output with a correctly formatted handoff block.")
        return False, []

    handoff_block = match.group(1).strip()
    logger.info(f"CODER HANDOFF block found:\n{handoff_block}")

    # Extract file paths from handoff
    file_pattern = r"^\s+-\s+([\w./_-]+):\s*(created|modified)"
    files = re.findall(file_pattern, handoff_block, re.MULTILINE)

    if not files:
        logger.error("CODER HANDOFF block contains no file entries.")
        logger.error("Coder must list every file it created or modified.")
        return False, []

    logger.info(f"Files declared in handoff: {len(files)}")
    for path, op in files:
        logger.info(f"  {op:>8}: {path}")

    return True, [path for path, _ in files]


def check_files_exist_on_disk(
    declared_files: list[str], project_root: Path, logger: HookLogger
) -> bool:
    """
    Check 2: Every file declared in CODER HANDOFF actually exists on disk.
    A declared file that doesn't exist means the Coder hallucinated its output.
    """
    logger.section("Check 2 — File existence on disk")

    all_exist = True
    for file_path in declared_files:
        full_path = project_root / file_path
        if not full_path.exists():
            logger.error(f"Declared file does not exist on disk: {full_path}")
            all_exist = False
        else:
            logger.info(f"  Exists: {file_path}")

    return all_exist


def check_no_forbidden_paths(declared_files: list[str], logger: HookLogger) -> bool:
    """
    Check 3: No files outside backend/ were touched.
    The backend-plugin session must not modify frontend, compose, or agent files
    unless declared in inter_plugin_contracts (checked separately by orchestrator).
    """
    logger.section("Check 3 — Forbidden path check")

    violations = []
    for file_path in declared_files:
        for prefix in FORBIDDEN_PATH_PREFIXES:
            if file_path.startswith(prefix):
                violations.append(file_path)
                logger.error(
                    f"Forbidden path touched: {file_path} "
                    f"(prefix '{prefix}' is outside backend-plugin scope)"
                )

    if not violations:
        logger.info("No forbidden paths touched.")
        return True

    return False


def check_python_syntax(
    declared_files: list[str], project_root: Path, logger: HookLogger
) -> bool:
    """
    Check 4: All Python files compile without syntax errors.
    Uses py_compile inside Docker to match the actual runtime environment.
    Catches import errors and syntax mistakes before tests are written against broken code.
    """
    logger.section("Check 4 — Python syntax (py_compile)")

    python_files = [f for f in declared_files if f.endswith(".py")]
    if not python_files:
        logger.info("No Python files to check.")
        return True

    all_ok = True
    for file_path in python_files:
        returncode, stdout, stderr = run_in_docker(
            ["python", "-m", "py_compile", file_path],
            logger,
        )
        if returncode != 0:
            logger.error(f"Syntax error in {file_path}:\n{stderr}")
            all_ok = False
        else:
            logger.info(f"  Syntax OK: {file_path}")

    return all_ok


def check_django_system(logger: HookLogger) -> bool:
    """
    Check 5: Django system check passes inside Docker.
    Catches configuration errors, missing app registrations, broken settings,
    and invalid model definitions before tests try to run against them.
    """
    logger.section("Check 5 — Django system check (manage.py check)")

    returncode, stdout, stderr = run_in_docker(
        ["python", "manage.py", "check", "--no-color"],
        logger,
        timeout=90,
    )

    if returncode != 0:
        logger.error("Django system check failed.")
        logger.error(f"Output:\n{stdout}\n{stderr}")
        return False

    logger.info("Django system check passed.")
    return True


def check_migrations_consistent(declared_files: list[str], logger: HookLogger) -> bool:
    """
    Check 6: No missing migrations for model changes.
    If the Coder modified or created model files, Django must not report
    any unapplied schema changes. A missing migration means the test
    database will be out of sync with the models.
    """
    logger.section("Check 6 — Migration consistency (manage.py makemigrations --check)")

    model_files = [f for f in declared_files if "models" in f and f.endswith(".py")]
    if not model_files:
        logger.info("No model files changed — skipping migration check.")
        return True

    logger.info(f"Model files changed: {model_files}")
    logger.info("Running makemigrations --check to detect missing migrations...")

    returncode, stdout, stderr = run_in_docker(
        ["python", "manage.py", "makemigrations", "--check", "--no-color"],
        logger,
        timeout=60,
    )

    if returncode != 0:
        logger.error("Missing migrations detected.")
        logger.error("Coder must run makemigrations and include the migration file.")
        logger.error(f"Output:\n{stdout}\n{stderr}")
        return False

    logger.info("No missing migrations. Migration state is consistent.")
    return True


def check_no_coder_gap_unresolved(coder_output: str, logger: HookLogger) -> bool:
    """
    Check 7: No unresolved CODER GAP blocks in output.
    If the Coder hit an unspecified case and surfaced a gap, the orchestrator
    must have resolved it before re-invoking. A gap block in the final output
    means the Coder stopped early and the implementation is incomplete.
    """
    logger.section("Check 7 — Unresolved CODER GAP blocks")

    if "=== CODER GAP ===" in coder_output:
        gap_match = re.search(
            r"=== CODER GAP ===(.*?)=== END CODER GAP ===", coder_output, re.DOTALL
        )
        if gap_match:
            logger.error("Unresolved CODER GAP block found in output.")
            logger.error(f"Gap content:\n{gap_match.group(1).strip()}")
            logger.error(
                "Orchestrator must resolve this gap with user input "
                "before Tester can be invoked."
            )
            return False

    logger.info("No unresolved CODER GAP blocks.")
    return True


# ── Output Builder ────────────────────────────────────────────────────────────


def build_output(passed: bool, errors: list[dict], declared_files: list[str]) -> dict:
    output = {
        "passed": passed,
        "hook_name": "pre_tester",
    }

    if passed:
        output["validated_files"] = declared_files
    else:
        output["errors"] = errors
        output["retry_prompt"] = (
            "The Coder output failed validation. "
            "Re-invoke the Coder subagent with these errors as additional context. "
            "The Coder must fix the issues and re-produce a complete CODER HANDOFF block."
        )

    return output


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    hook_start = time.time()

    parser = argparse.ArgumentParser(
        description="pre_tester hook — validates Coder output"
    )
    parser.add_argument("--coder-output", required=True)
    parser.add_argument("--plugin-state", required=True)
    parser.add_argument("--log-dir", required=True)
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    project_root = Path(args.project_root).resolve()
    logger = HookLogger(log_dir, hook_start)

    logger.section("Inputs")
    logger.info(f"Coder output file : {args.coder_output}")
    logger.info(f"Plugin state file : {args.plugin_state}")
    logger.info(f"Project root      : {project_root}")

    try:
        coder_output = Path(args.coder_output).read_text(encoding="utf-8")
        logger.info(f"Coder output loaded ({len(coder_output)} chars).")
    except Exception as e:
        logger.error(f"Failed to read coder output: {e}")
        output = build_output(
            False,
            [
                {
                    "issue": f"Cannot read coder output file: {e}",
                    "convention_ref": "orchestrator.md#subagent-invocation",
                }
            ],
            [],
        )
        logger.write_footer(False, 1, time.time() - hook_start)
        print(json.dumps(output, indent=2))
        sys.exit(1)

    errors = []
    declared_files = []

    handoff_ok, declared_files = check_handoff_block_present(coder_output, logger)
    if not handoff_ok:
        errors.append(
            {
                "file": args.coder_output,
                "issue": "CODER HANDOFF block missing or contains no file entries.",
                "convention_ref": "agents/coder.txt#handoff",
            }
        )

    if declared_files:
        if not check_files_exist_on_disk(declared_files, project_root, logger):
            errors.append(
                {
                    "file": args.coder_output,
                    "issue": "One or more files declared in CODER HANDOFF do not exist on disk.",
                    "convention_ref": "agents/coder.txt#for-all-implementation-stages",
                }
            )

        if not check_no_forbidden_paths(declared_files, logger):
            errors.append(
                {
                    "file": args.coder_output,
                    "issue": "Coder touched files outside backend-plugin scope.",
                    "convention_ref": "context/constraints.md#rollback-safety-invariants",
                }
            )

        if not check_python_syntax(declared_files, project_root, logger):
            errors.append(
                {
                    "file": args.coder_output,
                    "issue": "One or more Python files have syntax or import errors.",
                    "convention_ref": "backend/Readme.md#clean-code",
                }
            )

        if not check_migrations_consistent(declared_files, logger):
            errors.append(
                {
                    "file": args.coder_output,
                    "issue": "Model changes detected but migrations are missing.",
                    "convention_ref": "context/constraints.md#data-model-invariants",
                }
            )

    if not check_django_system(logger):
        errors.append(
            {
                "file": "backend/config/",
                "issue": "Django system check failed after Coder changes.",
                "convention_ref": "backend/Readme.md#settings",
            }
        )

    if not check_no_coder_gap_unresolved(coder_output, logger):
        errors.append(
            {
                "file": args.coder_output,
                "issue": "Unresolved CODER GAP block found. Implementation is incomplete.",
                "convention_ref": "agents/coder.txt#when-you-encounter-an-unspecified-case",
            }
        )

    passed = len(errors) == 0
    total_elapsed = time.time() - hook_start

    logger.section("Summary")
    logger.info(f"Checks run    : 7")
    logger.info(f"Errors found  : {len(errors)}")
    logger.info(f"Result        : {'PASSED' if passed else 'FAILED'}")
    logger.write_footer(passed, len(errors), total_elapsed)

    output = build_output(passed, errors, declared_files)
    print(json.dumps(output, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
