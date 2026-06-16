"""
pre_coder.py — BMA Backend Pipeline Hook
Validates Architect subagent output before the Coder is invoked.

MAX_RETRIES: 3
Scope: Architect output validation only. Does not touch source files.

Invoked by: orchestrator, after Architect handoff, before Coder invocation.
Input:      Path to architect output (text file written by orchestrator from
            Architect's response), path to plugin_state.json.
Output:     Structured JSON to stdout. Orchestrator parses this — do not print
            anything else to stdout. Use stderr for debug output only.
Log:        .agents/logs/<feature_slug>/<timestamp>_pre_coder.log

POST-PASS ORCHESTRATOR RESPONSIBILITY (not done by this hook):
On a passing result, the orchestrator must write the validated
domains_touched and apps_touched lists (already parsed here via
extract_architect_summary) into plugin_state.json's domains_touched and
apps_touched fields, via checkpoint.py, BEFORE invoking the Coder. This
hook only validates — it does not mutate state. context_builder.py's
resolve_app_readme_sections() and the reference:{{domains}} injection
marker both depend on those fields being populated by this point.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
HOOK_NAME = "pre_coder"

VALID_PIPELINE_STAGES = {
    "architecture",
    "documentation",
    "dependency_setup",
    "service_validation",
    "happy_path",
    "happy_path_tests",
    "full_implementation",
    "full_implementation_tests",
    "final_documentation",
}

VALID_DOMAINS = {
    "async_tasks",
    "payments",
    "tenants",
    "customers",
    "notifications",
    "setup_and_config",
    "seeders",
    "architecture_index",
}

KNOWN_APPS = {
    "customer_management",
    "notifications",
    "payments_management",
    "services",
    "setup",
    "tasks",
    "tenants",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def init_logger(feature_slug: str, logs_root: Path) -> Path:
    """
    Creates the log file for this hook run.
    Returns the log file path.
    Format: .agents/logs/<feature_slug>/<timestamp>_pre_coder.log
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

def extract_architect_summary(architect_output: str) -> dict | None:
    """
    Extracts the === ARCHITECT SUMMARY === block from the Architect's output.
    Returns a dict of parsed fields, or None if the block is missing/malformed.
    """
    pattern = r"=== ARCHITECT SUMMARY ===(.*?)=== END ARCHITECT SUMMARY ==="
    match = re.search(pattern, architect_output, re.DOTALL)
    if not match:
        return None

    raw = match.group(1).strip()
    parsed = {}

    # Extract list fields
    for field in ["domains_touched", "apps_touched", "pipeline"]:
        list_match = re.search(rf"{field}:\s*\[([^\]]*)\]", raw)
        if list_match:
            items = [i.strip() for i in list_match.group(1).split(",") if i.strip()]
            parsed[field] = items
        else:
            parsed[field] = None

    # Extract inter_plugin_contracts
    contract_match = re.search(r"inter_plugin_contracts:\s*(\S+)", raw)
    parsed["inter_plugin_contracts"] = contract_match.group(1) if contract_match else None

    # Presence checks
    parsed["has_decision_gaps_section"] = "decision_gaps:" in raw
    parsed["has_architect_notes"] = "architect_notes_append:" in raw

    return parsed


# ---------------------------------------------------------------------------
# Validation Steps
# ---------------------------------------------------------------------------

def check_summary_present(architect_output: str, log_path: Path) -> list[dict]:
    """Step 1 — Architect summary block must be present and parseable."""
    errors = []
    log(log_path, "CHECK: Architect summary block presence")
    summary = extract_architect_summary(architect_output)
    if summary is None:
        errors.append({
            "check": "summary_block_present",
            "issue": "=== ARCHITECT SUMMARY === block is missing or malformed in Architect output.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/architect.txt § Step 6",
        })
        log(log_path, "  FAIL: Summary block missing or malformed")
    else:
        log(log_path, "  PASS: Summary block found and parseable")
    return errors


def check_domains_valid(summary: dict, log_path: Path) -> list[dict]:
    """Step 2 — All declared domains must be known to the reference context."""
    errors = []
    log(log_path, "CHECK: Declared domains validity")
    domains = summary.get("domains_touched")

    if not domains:
        errors.append({
            "check": "domains_declared",
            "issue": "domains_touched is empty or missing. Architect must declare at least one domain.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/architect.txt § Step 1",
        })
        log(log_path, "  FAIL: domains_touched is empty")
        return errors

    unknown = [d for d in domains if d not in VALID_DOMAINS]
    if unknown:
        errors.append({
            "check": "domains_valid",
            "issue": f"Unknown domains declared: {unknown}. Valid domains: {sorted(VALID_DOMAINS)}",
            "convention_ref": ".agents/plugins/backend-plugin/context/reference.md",
        })
        log(log_path, f"  FAIL: Unknown domains: {unknown}")
    else:
        log(log_path, f"  PASS: All domains valid: {domains}")
    return errors


def check_apps_exist(summary: dict, backend_root: Path, log_path: Path) -> list[dict]:
    """Step 3 — All declared apps must exist under backend/apps/."""
    errors = []
    log(log_path, "CHECK: Declared apps existence on disk")
    apps = summary.get("apps_touched")

    if not apps:
        errors.append({
            "check": "apps_declared",
            "issue": "apps_touched is empty or missing. Architect must declare which apps are affected.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/architect.txt § Step 1",
        })
        log(log_path, "  FAIL: apps_touched is empty")
        return errors

    apps_root = backend_root / "apps"
    for app in apps:
        app_path = apps_root / app
        if not app_path.exists():
            errors.append({
                "check": "app_exists",
                "issue": f"Declared app '{app}' does not exist at {app_path}.",
                "convention_ref": "backend/Readme.md § Directory Structure",
            })
            log(log_path, f"  FAIL: App not found on disk: {app}")
        elif app not in KNOWN_APPS:
            errors.append({
                "check": "app_known",
                "issue": (
                    f"App '{app}' exists on disk but is not in KNOWN_APPS. "
                    "If this is a new app, it must be discussed with the user before proceeding. "
                    "Update KNOWN_APPS in this hook and add the app Readme before retrying."
                ),
                "convention_ref": "constraints.md § Data Model Invariants",
            })
            log(log_path, f"  FAIL: App '{app}' not in KNOWN_APPS")
        else:
            log(log_path, f"  PASS: App '{app}' exists")
    return errors


def check_pipeline_valid(summary: dict, log_path: Path) -> list[dict]:
    """Step 4 — Pipeline stages must be valid enum values and non-empty."""
    errors = []
    log(log_path, "CHECK: Pipeline stage validity")
    pipeline = summary.get("pipeline")

    if not pipeline:
        errors.append({
            "check": "pipeline_declared",
            "issue": "pipeline is empty or missing. Architect must declare at least one stage.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/architect.txt § Step 2",
        })
        log(log_path, "  FAIL: pipeline is empty")
        return errors

    invalid = [s for s in pipeline if s not in VALID_PIPELINE_STAGES]
    if invalid:
        errors.append({
            "check": "pipeline_stages_valid",
            "issue": f"Invalid pipeline stages declared: {invalid}. Valid stages: {sorted(VALID_PIPELINE_STAGES)}",
            "convention_ref": ".agents/plugins/backend-plugin/agents/architect.txt § Step 2",
        })
        log(log_path, f"  FAIL: Invalid stages: {invalid}")
    else:
        log(log_path, f"  PASS: All pipeline stages valid: {pipeline}")
    return errors


def check_decision_gaps_resolved(architect_output: str, plugin_state: dict, log_path: Path) -> list[dict]:
    """Step 5 — All decision gaps must be resolved before the Coder starts."""
    errors = []
    log(log_path, "CHECK: Decision gaps resolution")

    gap_pattern = r"=== ARCHITECT SUMMARY ===(.*?)=== END ARCHITECT SUMMARY ==="
    match = re.search(gap_pattern, architect_output, re.DOTALL)
    if not match:
        return errors

    raw = match.group(1)
    gap_questions = re.findall(r'question:\s*"([^"]+)"', raw)

    if not gap_questions:
        log(log_path, "  PASS: No decision gaps declared")
        return errors

    architect_notes = plugin_state.get("architect_notes", "").strip()
    if not architect_notes:
        errors.append({
            "check": "decision_gaps_resolved",
            "issue": (
                f"{len(gap_questions)} decision gap(s) declared but architect_notes is empty. "
                "Orchestrator must collect user answers and write them to architect_notes before "
                "invoking the Coder. Gaps: " + "; ".join(gap_questions)
            ),
            "convention_ref": "orchestrator.md § 4. Decision Gaps vs. Prerequisite Gaps",
        })
        log(log_path, f"  FAIL: {len(gap_questions)} unresolved gap(s), architect_notes empty")
    else:
        log(log_path, f"  PASS: {len(gap_questions)} gap(s) declared, architect_notes populated")
    return errors


def check_handoff_block_present(architect_output: str, log_path: Path) -> list[dict]:
    """Step 6 — Architect handoff block must be present."""
    errors = []
    log(log_path, "CHECK: Architect handoff block presence")
    if "=== ARCHITECT HANDOFF ===" not in architect_output:
        errors.append({
            "check": "handoff_block_present",
            "issue": "=== ARCHITECT HANDOFF === block is missing. Architect did not complete its handoff.",
            "convention_ref": ".agents/plugins/backend-plugin/agents/architect.txt § Handoff",
        })
        log(log_path, "  FAIL: Handoff block missing")
    else:
        log(log_path, "  PASS: Handoff block present")
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
                "issue": f"Expected 4 arguments: architect_output_path, plugin_state_path, backend_root, logs_root. Got {len(sys.argv) - 1}.",
                "convention_ref": "hooks/pre_coder.py",
            }],
            "retry_prompt": "Fix hook invocation arguments.",
        }))
        sys.exit(1)

    architect_output_path = Path(sys.argv[1])
    plugin_state_path = Path(sys.argv[2])
    backend_root = Path(sys.argv[3])
    logs_root = Path(sys.argv[4])

    architect_output = architect_output_path.read_text(encoding="utf-8")
    plugin_state = json.loads(plugin_state_path.read_text(encoding="utf-8"))
    feature_slug = plugin_state.get("feature", "unknown-feature").replace(" ", "-").lower()

    log_path = init_logger(feature_slug, logs_root)
    log(log_path, f"=== {HOOK_NAME.upper()} START ===")
    log(log_path, f"Feature:            {plugin_state.get('feature')}")
    log(log_path, f"Current stage:      {plugin_state.get('current_stage')}")
    log(log_path, f"Architect output:   {architect_output_path}")
    log(log_path, f"Max retries:        {MAX_RETRIES}")
    log(log_path, f"Retry count so far: {plugin_state.get('retry_counts', {}).get(HOOK_NAME, 0)}")

    all_errors = []
    all_errors += check_summary_present(architect_output, log_path)

    summary = extract_architect_summary(architect_output)
    if summary:
        all_errors += check_domains_valid(summary, log_path)
        all_errors += check_apps_exist(summary, backend_root, log_path)
        all_errors += check_pipeline_valid(summary, log_path)
        all_errors += check_decision_gaps_resolved(architect_output, plugin_state, log_path)

    all_errors += check_handoff_block_present(architect_output, log_path)

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
        "parsed_domains_touched": summary.get("domains_touched") if summary else None,
        "parsed_apps_touched": summary.get("apps_touched") if summary else None,
        "retry_prompt": (
            "Fix the above issues in the Architect output and resubmit."
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