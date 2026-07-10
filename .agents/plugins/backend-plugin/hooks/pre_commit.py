"""
pre_commit.py — BMA Backend Pipeline Hook
Final gate before a stage is considered done. Validates Tester output,
runs the project's existing pre-commit suite scoped to touched files, and
confirms state integrity before the orchestrator marks the stage complete.

MAX_RETRIES: 1
Scope: Tester output validation, pre-commit suite (scoped), state consistency.
       Does NOT duplicate checks pre-commit already owns (formatting, print
       statements, complexity, secrets) — those run via the real
       `poetry run pre-commit` invocation, scoped to files_touched.

Invoked by: orchestrator, after Tester handoff, before marking stage complete.
Input:      Path to tester output, path to plugin_state.json, project root,
            logs root, backend dir (for poetry run cwd).
Output:     Structured JSON to stdout. Orchestrator parses this — do not print
            anything else to stdout. Use stderr for debug output only.
Log:        .agents/logs/<feature_slug>/<timestamp>_pre_commit.log
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

MAX_RETRIES = 1
HOOK_NAME = "pre_commit"

PRECOMMIT_TIMEOUT = 180  # pre-commit suite (black, flake8, xenon, etc.) can be slow on first run

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def init_logger(feature_slug: str, logs_root: Path) -> Path:
    """
    Creates the log file for this hook run.
    Format: .agents/logs/<feature_slug>/<timestamp>_pre_commit.log
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

def extract_tester_handoff(tester_output: str) -> dict | None:
    """
    Extracts the === TESTER HANDOFF === block from the Tester's output.

    Expected format:
        === TESTER HANDOFF ===
        Stage complete: happy_path_tests
        Tests written: 4
        Tests passing: 4
        Ready for orchestrator to run: pre_commit
        Files created or modified:
          - backend/apps/tasks/tests/test_invoice_tasks.py: created
        Test run output:
        <pytest output>
        === END TESTER HANDOFF ===
    """
    pattern = r"=== TESTER HANDOFF ===(.*?)=== END TESTER HANDOFF ==="
    match = re.search(pattern, tester_output, re.DOTALL)
    if not match:
        return None

    raw = match.group(1)
    parsed = {}

    stage_match = re.search(r"Stage complete:\s*(\S+)", raw)
    parsed["stage_complete"] = stage_match.group(1) if stage_match else None

    written_match = re.search(r"Tests written:\s*(\d+)", raw)
    parsed["tests_written"] = int(written_match.group(1)) if written_match else None

    passing_match = re.search(r"Tests passing:\s*(\d+)", raw)
    parsed["tests_passing"] = int(passing_match.group(1)) if passing_match else None

    file_entries = re.findall(r"-\s*([^\s:][^:]*?):\s*(created|modified)", raw)
    parsed["files"] = [{"path": p.strip(), "operation": op} for p, op in file_entries]

    output_match = re.search(r"Test run output:\s*\n(.*)", raw, re.DOTALL)
    parsed["test_run_output"] = output_match.group(1).strip() if output_match else ""

    return parsed


def extract_bug_report(tester_output: str) -> dict | None:
    """
    Checks if the Tester reported a === TESTER BUG REPORT === instead of a
    clean handoff. This means the implementation has a bug — not a Tester
    failure. Must route back to the Coder, not retry the Tester.
    """
    pattern = r"=== TESTER BUG REPORT ===(.*?)=== END TESTER BUG REPORT ==="
    match = re.search(pattern, tester_output, re.DOTALL)
    if not match:
        return None
    return {"raw_bug_report": match.group(1).strip()}


# ---------------------------------------------------------------------------
# Validation Steps
# ---------------------------------------------------------------------------

def check_handoff_present(tester_output: str, log_path: Path) -> tuple[list[dict], dict | None]:
    """Step 1 — Tester handoff block must be present and parseable."""
    errors = []
    log(log_path, "CHECK: Tester handoff block presence")
    handoff = extract_tester_handoff(tester_output)
    if handoff is None:
        errors.append({
            "check": "handoff_block_present",
            "issue": "=== TESTER HANDOFF === block is missing or malformed in Tester output.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/tester.txt § Handoff",
        })
        log(log_path, "  FAIL: Handoff block missing or malformed")
    else:
        log(log_path, f"  PASS: Handoff found — {handoff.get('tests_passing')}/{handoff.get('tests_written')} tests passing")
    return errors, handoff


def check_tests_all_passing(handoff: dict, log_path: Path) -> list[dict]:
    """Step 2 — Declared tests_written must equal tests_passing. No partial passes allowed at this gate."""
    errors = []
    log(log_path, "CHECK: All declared tests passing")
    written = handoff.get("tests_written")
    passing = handoff.get("tests_passing")

    if written is None or passing is None:
        errors.append({
            "check": "test_counts_declared",
            "issue": "Tests written / Tests passing counts missing from handoff.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/tester.txt § Handoff",
        })
        log(log_path, "  FAIL: Test counts not declared")
        return errors

    if written == 0:
        errors.append({
            "check": "tests_written",
            "issue": "Zero tests were written for this stage. A test stage must produce at least one test.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/tester.txt § Your Task",
        })
        log(log_path, "  FAIL: Zero tests written")
        return errors

    if passing != written:
        errors.append({
            "check": "tests_all_passing",
            "issue": f"{passing}/{written} tests passing. All declared tests must pass before proceeding.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/tester.txt § Handoff",
        })
        log(log_path, f"  FAIL: {passing}/{written} passing")
    else:
        log(log_path, f"  PASS: {passing}/{written} passing")
    return errors


def check_test_output_no_errors(handoff: dict, log_path: Path) -> list[dict]:
    """
    Step 3 — Sanity-check the raw pytest output for failure/error markers,
    independent of the self-reported counts. Catches a Tester misreporting
    its own results.
    """
    errors = []
    log(log_path, "CHECK: Raw test output sanity check")
    output = handoff.get("test_run_output", "")

    if not output:
        errors.append({
            "check": "test_output_present",
            "issue": "No raw test run output included in handoff. Cannot verify self-reported pass count.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/tester.txt § Handoff",
        })
        log(log_path, "  FAIL: No raw output to verify against")
        return errors

    failure_markers = re.findall(r"(\d+) failed", output)
    error_markers = re.findall(r"(\d+) error", output)

    if any(int(n) > 0 for n in failure_markers) or any(int(n) > 0 for n in error_markers):
        errors.append({
            "check": "test_output_clean",
            "issue": "Raw pytest output contains failures or errors, contradicting the self-reported passing count.",
            "convention_ref": "hooks/pre_commit.py § check_test_output_no_errors",
        })
        log(log_path, "  FAIL: Raw output contains failure/error markers despite reported pass count")
    else:
        log(log_path, "  PASS: No failure/error markers in raw output")
    return errors


def check_files_touched_complete(
    coder_files_touched: list[dict], tester_handoff_files: list[dict], log_path: Path
) -> list[dict]:
    """
    Step 4 — Cross-check that plugin_state.json → files_touched (accumulated
    across Coder + Tester stages) matches what was actually declared in
    handoffs. Catches silent state drift.
    """
    errors = []
    log(log_path, "CHECK: files_touched state completeness")

    declared_paths = {e["path"] for e in tester_handoff_files}
    recorded_paths = {e["path"] for e in coder_files_touched}

    missing_from_state = declared_paths - recorded_paths
    if missing_from_state:
        errors.append({
            "check": "files_touched_complete",
            "issue": f"Tester declared files not present in plugin_state.json files_touched: {sorted(missing_from_state)}",
            "convention_ref": "orchestrator.md § 7. Subagent Invocation",
        })
        log(log_path, f"  FAIL: Missing from state: {sorted(missing_from_state)}")
    else:
        log(log_path, "  PASS: All declared test files accounted for in state")
    return errors


def run_scoped_precommit(touched_files: list[str], backend_dir: Path, project_root: Path, log_path: Path) -> list[dict]:
    """
    Step 5 — Run the project's real pre-commit suite, scoped to files_touched
    for this session only. Never run --all-files here — that would flag
    pre-existing violations unrelated to this pipeline run and slow every cycle.

    Uses: poetry run pre-commit run --files <touched_files>
    (run from backend_dir, matching the existing Makefile's cwd convention)
    """
    errors = []
    log(log_path, "CHECK: Scoped pre-commit suite (black, flake8, isort, xenon, detect-secrets, etc.)")

    if not touched_files:
        log(log_path, "  SKIP: No files to scope pre-commit against")
        return errors

    relative_paths = []
    for f in touched_files:
        path_obj = Path(f)
        if path_obj.parts and path_obj.parts[0] == "backend":
            # Strip "backend" prefix
            rel_path = Path(*path_obj.parts[1:])
            relative_paths.append(str(rel_path))
        else:
            # Path is outside backend, reference it relative to backend_dir
            relative_paths.append(str(Path("..") / path_obj))

    cmd = ["poetry", "run", "pre-commit", "run", "--files"] + relative_paths
    log(log_path, f"  Running: {' '.join(cmd)} (cwd={backend_dir})")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=PRECOMMIT_TIMEOUT, cwd=str(backend_dir),
        )
        # pre-commit exits non-zero on failure, but also on auto-fix (e.g. black
        # reformatting a file). We surface both — orchestrator decides if an
        # auto-fix-only failure should count as a retry or be re-checked once more.
        if result.returncode != 0:
            errors.append({
                "check": "scoped_pre_commit",
                "issue": (
                    "pre-commit suite reported issues (or applied auto-fixes) on touched files. "
                    f"Output: {result.stdout.strip()[-1500:]}"
                ),
                "convention_ref": ".pre-commit-config.yaml",
            })
            log(log_path, "  FAIL: pre-commit suite reported issues — see error detail")
        else:
            log(log_path, "  PASS: pre-commit suite passed on all touched files")
    except subprocess.TimeoutExpired:
        errors.append({
            "check": "scoped_pre_commit",
            "issue": f"pre-commit suite timed out after {PRECOMMIT_TIMEOUT}s.",
            "convention_ref": "hooks/pre_commit.py § run_scoped_precommit",
        })
        log(log_path, "  FAIL: Timeout running pre-commit suite")
    except FileNotFoundError:
        errors.append({
            "check": "scoped_pre_commit",
            "issue": "poetry command not found on host. Cannot run pre-commit suite.",
            "convention_ref": "hooks/pre_commit.py § run_scoped_precommit",
        })
        log(log_path, "  FAIL: poetry not available on host")
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    start_time = time.time()

    # Expected: pre_commit.py <tester_output_path> <plugin_state_path> <project_root> <backend_dir> <logs_root>
    if len(sys.argv) != 6:
        print(json.dumps({
            "passed": False,
            "hook_name": HOOK_NAME,
            "errors": [{
                "check": "invocation",
                "issue": f"Expected 5 arguments: tester_output_path, plugin_state_path, project_root, backend_dir, logs_root. Got {len(sys.argv) - 1}.",
                "convention_ref": "hooks/pre_commit.py",
            }],
            "retry_prompt": "Fix hook invocation arguments.",
        }))
        sys.exit(1)

    tester_output_path = Path(sys.argv[1])
    plugin_state_path = Path(sys.argv[2])
    project_root = Path(sys.argv[3])
    backend_dir = Path(sys.argv[4])
    logs_root = Path(sys.argv[5])

    tester_output = tester_output_path.read_text(encoding="utf-8")
    plugin_state = json.loads(plugin_state_path.read_text(encoding="utf-8"))
    feature_slug = plugin_state.get("feature", "unknown-feature").replace(" ", "-").lower()

    log_path = init_logger(feature_slug, logs_root)
    log(log_path, f"=== {HOOK_NAME.upper()} START ===")
    log(log_path, f"Feature:            {plugin_state.get('feature')}")
    log(log_path, f"Current stage:      {plugin_state.get('current_stage')}")
    log(log_path, f"Tester output:      {tester_output_path}")
    log(log_path, f"Max retries:        {MAX_RETRIES}")
    log(log_path, f"Retry count so far: {plugin_state.get('retry_counts', {}).get(HOOK_NAME, 0)}")

    # --- Check for explicit bug report first — routes to Coder, not a hook retry ---
    bug_report = extract_bug_report(tester_output)
    if bug_report:
        elapsed = round(time.time() - start_time, 3)
        log(log_path, "TESTER BUG REPORT detected — routes to Coder, not a pre_commit retry")
        log(log_path, bug_report["raw_bug_report"][:500])
        log(log_path, f"Execution time: {elapsed}s")
        log(log_path, f"=== {HOOK_NAME.upper()} END (BUG REPORT) ===")
        result = {
            "passed": False,
            "hook_name": HOOK_NAME,
            "is_bug_report": True,
            "execution_time_seconds": elapsed,
            "errors": [{
                "check": "tester_bug_report",
                "issue": "Tests revealed an implementation bug. This must route back to the Coder stage, not retry pre_commit.",
                "convention_ref": ".agents/plugins/backend-plugin/agents/tester.txt § When Tests Fail",
            }],
            "bug_report": bug_report["raw_bug_report"],
            "retry_prompt": None,
        }
        print(json.dumps(result, indent=2))
        sys.exit(2)  # distinct exit code — same convention as pre_tester.py's Coder Gap

    # --- Run checks ---
    all_errors = []
    handoff_errors, handoff = check_handoff_present(tester_output, log_path)
    all_errors += handoff_errors

    touched_files_for_precommit = []

    if handoff:
        all_errors += check_tests_all_passing(handoff, log_path)
        all_errors += check_test_output_no_errors(handoff, log_path)

        coder_files_touched = plugin_state.get("files_touched", [])
        all_errors += check_files_touched_complete(coder_files_touched, handoff.get("files", []), log_path)

        # Scope pre-commit to everything touched this session, not just this stage's files
        touched_files_for_precommit = [e["path"] for e in coder_files_touched]

    all_errors += run_scoped_precommit(touched_files_for_precommit, backend_dir, project_root, log_path)

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
            "Fix the above issues and resubmit. This is the final gate — only one retry is allowed."
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