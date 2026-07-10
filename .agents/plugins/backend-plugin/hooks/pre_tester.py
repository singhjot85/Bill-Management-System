"""
pre_tester.py — BMA Backend Pipeline Hook
Validates Coder subagent output before the Tester is invoked.

MAX_RETRIES: 2
Scope: Coder output validation only (file existence, syntax, Django check,
migration consistency, constraint compliance). Does not write tests itself.

Invoked by: orchestrator, after Coder handoff, before Tester invocation.
Input:      Path to coder output (text file written by orchestrator from
            Coder's response), path to plugin_state.json, backend root,
            logs root.
Output:     Structured JSON to stdout. Orchestrator parses this — do not print
            anything else to stdout. Use stderr for debug output only.
Log:        .agents/logs/<feature_slug>/<timestamp>_pre_tester.log
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_RETRIES = 2
HOOK_NAME = "pre_tester"

# Subprocess timeouts (seconds) — prevent a hung Docker command from stalling the pipeline
PY_COMPILE_TIMEOUT = 30
DJANGO_CHECK_TIMEOUT = 60
MAKEMIGRATIONS_CHECK_TIMEOUT = 60

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def init_logger(feature_slug: str, logs_root: Path) -> Path:
    """
    Creates the log file for this hook run.
    Format: .agents/logs/<feature_slug>/<timestamp>_pre_tester.log
    """
    log_dir = logs_root / feature_slug
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    log_path = log_dir / f"{timestamp}_{HOOK_NAME}.log"
    return log_path


def log(log_path: Path, message: str):
    """Append a timestamped line to the log file and echo to stderr."""
    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {message}\n"
    with open(log_path, "a") as f:
        f.write(line)
    print(line, end="", file=sys.stderr)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def extract_coder_handoff(coder_output: str) -> dict | None:
    """
    Extracts the === CODER HANDOFF === block from the Coder's output.
    Returns parsed fields, or None if the block is missing/malformed.

    Expected format:
        === CODER HANDOFF ===
        Stage complete: happy_path
        Ready for orchestrator to run: pre_tester
        Files created or modified:
          - backend/apps/tasks/invoice_tasks.py: created
          - backend/apps/tasks/registry.py: modified
        === END CODER HANDOFF ===
    """
    pattern = r"=== CODER HANDOFF ===(.*?)=== END CODER HANDOFF ==="
    match = re.search(pattern, coder_output, re.DOTALL)
    if not match:
        return None

    raw = match.group(1)
    parsed = {}

    stage_match = re.search(r"Stage complete:\s*(\S+)", raw)
    parsed["stage_complete"] = stage_match.group(1) if stage_match else None

    hook_match = re.search(r"Ready for orchestrator to run:\s*(\S+)", raw)
    parsed["next_hook"] = hook_match.group(1) if hook_match else None

    # Files list: "  - <path>: created | modified"
    file_entries = re.findall(r"-\s*([^\s:][^:]*?):\s*(created|modified)", raw)
    parsed["files"] = [{"path": p.strip(), "operation": op} for p, op in file_entries]

    return parsed


def extract_coder_gap(coder_output: str) -> dict | None:
    """
    Checks if the Coder reported a === CODER GAP === instead of completing.
    If present, the Coder explicitly stopped — this is not a hook failure,
    it's a prerequisite gap that must be surfaced to the user directly.
    """
    pattern = r"=== CODER GAP ===(.*?)=== END CODER GAP ==="
    match = re.search(pattern, coder_output, re.DOTALL)
    if not match:
        return None
    raw = match.group(1)
    return {"raw_gap_report": raw.strip()}


# ---------------------------------------------------------------------------
# Validation Steps
# ---------------------------------------------------------------------------

def check_handoff_present(coder_output: str, log_path: Path) -> tuple[list[dict], dict | None]:
    """Step 1 — Coder handoff block must be present and parseable."""
    errors = []
    log(log_path, "CHECK: Coder handoff block presence")
    handoff = extract_coder_handoff(coder_output)
    if handoff is None:
        errors.append({
            "check": "handoff_block_present",
            "issue": "=== CODER HANDOFF === block is missing or malformed in Coder output.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/coder.txt § Handoff",
        })
        log(log_path, "  FAIL: Handoff block missing or malformed")
    else:
        log(log_path, f"  PASS: Handoff found — {len(handoff.get('files', []))} file(s) declared")
    return errors, handoff


def check_files_declared(handoff: dict, log_path: Path) -> list[dict]:
    """Step 2 — Handoff must declare at least one file for implementation stages."""
    errors = []
    log(log_path, "CHECK: Files declared in handoff")
    files = handoff.get("files", [])
    if not files:
        errors.append({
            "check": "files_declared",
            "issue": "No files declared in CODER HANDOFF. An implementation stage must produce at least one file.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/coder.txt § For all implementation stages",
        })
        log(log_path, "  FAIL: No files declared")
    else:
        log(log_path, f"  PASS: {len(files)} file(s) declared")
    return errors


def check_files_exist_on_disk(handoff: dict, project_root: Path, log_path: Path) -> list[dict]:
    """Step 3 — Every file declared in the handoff must actually exist on disk."""
    errors = []
    log(log_path, "CHECK: Declared files exist on disk")
    for entry in handoff.get("files", []):
        file_path = project_root / entry["path"]
        if not file_path.exists():
            errors.append({
                "check": "file_exists",
                "issue": f"Declared file '{entry['path']}' ({entry['operation']}) does not exist on disk.",
                "convention_ref": "hooks/pre_tester.py § check_files_exist_on_disk",
            })
            log(log_path, f"  FAIL: Missing on disk: {entry['path']}")
        else:
            log(log_path, f"  PASS: Found: {entry['path']}")
    return errors


def check_no_files_outside_backend(handoff: dict, log_path: Path) -> list[dict]:
    """
    Step 4 — Constraint check: no file outside backend/ may be touched during
    a backend-plugin session unless declared in inter_plugin_contracts.
    """
    errors = []
    log(log_path, "CHECK: No files touched outside backend/")
    for entry in handoff.get("files", []):
        path = entry["path"]
        if not path.startswith("backend/"):
            errors.append({
                "check": "scope_boundary",
                "issue": f"File '{path}' is outside backend/. This violates plugin scope unless declared in inter_plugin_contracts.",
                "convention_ref": "constraints.md § Rollback Safety Invariants",
            })
            log(log_path, f"  FAIL: Out-of-scope file: {path}")
    if not errors:
        log(log_path, "  PASS: All files within backend/")
    return errors


def check_python_syntax(handoff: dict, project_root: Path, log_path: Path) -> list[dict]:
    """Step 5 — Every .py file declared must compile without syntax errors."""
    errors = []
    log(log_path, "CHECK: Python syntax validity (py_compile)")
    py_files = [e for e in handoff.get("files", []) if e["path"].endswith(".py")]

    if not py_files:
        log(log_path, "  SKIP: No Python files declared")
        return errors

    for entry in py_files:
        file_path = project_root / entry["path"]
        if not file_path.exists():
            continue  # already caught by check_files_exist_on_disk
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path)],
                capture_output=True, text=True, timeout=PY_COMPILE_TIMEOUT,
            )
            if result.returncode != 0:
                errors.append({
                    "check": "python_syntax",
                    "issue": f"Syntax error in '{entry['path']}': {result.stderr.strip()}",
                    "convention_ref": "hooks/pre_tester.py § check_python_syntax",
                })
                log(log_path, f"  FAIL: Syntax error in {entry['path']}: {result.stderr.strip()[:200]}")
            else:
                log(log_path, f"  PASS: {entry['path']} compiles cleanly")
        except subprocess.TimeoutExpired:
            errors.append({
                "check": "python_syntax",
                "issue": f"py_compile timed out after {PY_COMPILE_TIMEOUT}s for '{entry['path']}'.",
                "convention_ref": "hooks/pre_tester.py § check_python_syntax",
            })
            log(log_path, f"  FAIL: Timeout compiling {entry['path']}")
    return errors


def check_django_system_check(project_root: Path, log_path: Path) -> list[dict]:
    """
    Step 6 — Run `manage.py check` inside Docker to catch model/config errors
    that py_compile cannot detect (e.g. invalid FK references, app registry issues).
    """
    errors = []
    log(log_path, "CHECK: Django system check (manage.py check)")
    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "compose/compose.local.yaml", "exec", "-T", "django", "python", "manage.py", "check"],
            capture_output=True, text=True, timeout=DJANGO_CHECK_TIMEOUT, cwd=str(project_root),
        )
        if result.returncode != 0:
            errors.append({
                "check": "django_system_check",
                "issue": f"manage.py check failed: {result.stdout.strip()[-1000:]}{result.stderr.strip()[-500:]}",
                "convention_ref": "hooks/pre_tester.py § check_django_system_check",
            })
            log(log_path, f"  FAIL: manage.py check failed (see error detail)")
        else:
            log(log_path, "  PASS: manage.py check passed")
    except subprocess.TimeoutExpired:
        errors.append({
            "check": "django_system_check",
            "issue": f"manage.py check timed out after {DJANGO_CHECK_TIMEOUT}s. Container may be unresponsive.",
            "convention_ref": "hooks/pre_tester.py § check_django_system_check",
        })
        log(log_path, "  FAIL: Timeout running manage.py check")
    except FileNotFoundError:
        errors.append({
            "check": "django_system_check",
            "issue": "docker compose command not found on host. Cannot validate Django system check.",
            "convention_ref": "hooks/pre_tester.py § check_django_system_check",
        })
        log(log_path, "  FAIL: docker compose not available on host")
    return errors


def check_migrations_consistent(handoff: dict, project_root: Path, log_path: Path) -> list[dict]:
    """
    Step 7 — If any models.py file was touched, verify makemigrations --check
    reports no missing migrations.
    """
    errors = []
    log(log_path, "CHECK: Migration consistency")
    touched_models = [e for e in handoff.get("files", []) if "models" in e["path"] and e["path"].endswith(".py")]

    if not touched_models:
        log(log_path, "  SKIP: No models.py files touched")
        return errors

    try:
        result = subprocess.run(
            ["docker", "compose", "-f", "compose/compose.local.yaml", "exec", "-T", "django", "python", "manage.py",
             "makemigrations", "--check", "--dry-run"],
            capture_output=True, text=True, timeout=MAKEMIGRATIONS_CHECK_TIMEOUT, cwd=str(project_root),
        )
        if result.returncode != 0:
            errors.append({
                "check": "migrations_consistent",
                "issue": (
                    "makemigrations --check reports missing migrations for model changes. "
                    f"Output: {result.stdout.strip()[-1000:]}"
                ),
                "convention_ref": ".agents/plugins/backend-plugin/agents/coder.txt § happy_path",
            })
            log(log_path, "  FAIL: Missing migrations detected")
        else:
            log(log_path, "  PASS: No missing migrations")
    except subprocess.TimeoutExpired:
        errors.append({
            "check": "migrations_consistent",
            "issue": f"makemigrations --check timed out after {MAKEMIGRATIONS_CHECK_TIMEOUT}s.",
            "convention_ref": "hooks/pre_tester.py § check_migrations_consistent",
        })
        log(log_path, "  FAIL: Timeout checking migrations")
    except FileNotFoundError:
        errors.append({
            "check": "migrations_consistent",
            "issue": "docker compose command not found on host. Cannot validate migrations.",
            "convention_ref": "hooks/pre_tester.py § check_migrations_consistent",
        })
        log(log_path, "  FAIL: docker compose not available on host")
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    start_time = time.time()

    if len(sys.argv) != 5:
        print(json.dumps({
            "passed": False,
            "hook_name": HOOK_NAME,
            "errors": [{
                "check": "invocation",
                "issue": f"Expected 4 arguments: coder_output_path, plugin_state_path, project_root, logs_root. Got {len(sys.argv) - 1}.",
                "convention_ref": "hooks/pre_tester.py",
            }],
            "retry_prompt": "Fix hook invocation arguments.",
        }))
        sys.exit(1)

    coder_output_path = Path(sys.argv[1])
    plugin_state_path = Path(sys.argv[2])
    project_root = Path(sys.argv[3])
    logs_root = Path(sys.argv[4])

    coder_output = coder_output_path.read_text(encoding="utf-8")
    plugin_state = json.loads(plugin_state_path.read_text(encoding="utf-8"))
    feature_slug = plugin_state.get("feature", "unknown-feature").replace(" ", "-").lower()

    log_path = init_logger(feature_slug, logs_root)
    log(log_path, f"=== {HOOK_NAME.upper()} START ===")
    log(log_path, f"Feature:            {plugin_state.get('feature')}")
    log(log_path, f"Current stage:      {plugin_state.get('current_stage')}")
    log(log_path, f"Coder output:       {coder_output_path}")
    log(log_path, f"Max retries:        {MAX_RETRIES}")
    log(log_path, f"Retry count so far: {plugin_state.get('retry_counts', {}).get(HOOK_NAME, 0)}")

    # --- Check for explicit Coder gap first — this is not a hook failure ---
    gap = extract_coder_gap(coder_output)
    if gap:
        elapsed = round(time.time() - start_time, 3)
        log(log_path, "CODER GAP detected — Coder explicitly stopped, not a hook failure")
        log(log_path, gap["raw_gap_report"][:500])
        log(log_path, f"Execution time: {elapsed}s")
        log(log_path, f"=== {HOOK_NAME.upper()} END (CODER GAP) ===")
        result = {
            "passed": False,
            "hook_name": HOOK_NAME,
            "is_coder_gap": True,
            "execution_time_seconds": elapsed,
            "errors": [{
                "check": "coder_gap",
                "issue": "Coder reported an unspecified case and stopped. This requires Architect or user input, not a retry.",
                "convention_ref": ".agents/plugins/backend-plugin/agents/coder.txt § When You Encounter an Unspecified Case",
            }],
            "gap_report": gap["raw_gap_report"],
            "retry_prompt": None,
        }
        print(json.dumps(result, indent=2))
        sys.exit(2)  # distinct exit code — orchestrator must route to decision-gap handling, not retry

    # --- Run checks ---
    all_errors = []
    handoff_errors, handoff = check_handoff_present(coder_output, log_path)
    all_errors += handoff_errors

    if handoff:
        all_errors += check_files_declared(handoff, log_path)
        all_errors += check_files_exist_on_disk(handoff, project_root, log_path)
        all_errors += check_no_files_outside_backend(handoff, log_path)
        all_errors += check_python_syntax(handoff, project_root, log_path)
        all_errors += check_migrations_consistent(handoff, project_root, log_path)

    # Django check always runs regardless of handoff parse success — catches
    # broken state even if the handoff block itself was malformed.
    all_errors += check_django_system_check(project_root, log_path)

    elapsed = round(time.time() - start_time, 3)
    passed = len(all_errors) == 0
    retry_count = plugin_state.get("retry_counts", {}).get(HOOK_NAME, 0)
    will_hard_stop = not passed and retry_count >= MAX_RETRIES

    result = {
        "passed": passed,
        "hook_name": HOOK_NAME,
        "max_retries": MAX_RETRIES,
        "retry_count": retry_count,
        "will_hard_stop": will_hard_stop,
        "execution_time_seconds": elapsed,
        "errors": all_errors,
        "retry_prompt": (
            "Fix the above issues in the implementation and resubmit."
            if not passed else None
        ),
    }

    log(log_path, "--- RESULT ---")
    log(log_path, f"Passed:           {passed}")
    log(log_path, f"Error count:      {len(all_errors)}")
    log(log_path, f"Will hard stop:   {will_hard_stop}")
    log(log_path, f"Execution time:   {elapsed}s")
    log(log_path, f"=== {HOOK_NAME.upper()} END ===")

    print(json.dumps(result, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()