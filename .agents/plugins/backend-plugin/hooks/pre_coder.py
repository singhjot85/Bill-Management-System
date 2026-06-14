"""
pre_coder.py — BMA Backend Plugin Hook
=======================================
Validates Architect subagent output before the Coder is invoked.

Position in pipeline: architecture stage exit → before coder stage entry
Max retries: 3
On exceed: hard-stop, set plugin_state.json → blocked_on

Logs to: .agents/logs/<feature_slug>/<timestamp>_pre_coder.log
Stdout:   Structured JSON (read by orchestrator)

Usage:
    python .agents/plugins/backend-plugin/hooks/pre_coder.py \
        --architect-output <path_to_architect_output_file> \
        --plugin-state <path_to_plugin_state_json> \
        --log-dir <path_to_feature_log_dir>
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

MAX_RETRIES = 3

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

VALID_FEATURE_TYPES = {
    "new_feature",
    "bug_fix",
    "refactor",
    "infra_change",
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

# ── Logging Setup ─────────────────────────────────────────────────────────────


class HookLogger:
    """
    Writes structured, human-readable logs to a per-run log file.
    Each log entry is timestamped. Timing is tracked from hook start.

    Log file naming: <ISO8601_timestamp>_pre_coder.log
    Example:         2026-06-14T10-32-00_pre_coder.log
    """

    def __init__(self, log_dir: Path, hook_start_time: float):
        self.hook_start_time = hook_start_time
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        self.log_path = log_dir / f"{timestamp}_pre_coder.log"
        self._lines = []
        self._write_header()

    def _write_header(self):
        self._append("=" * 70)
        self._append("BMA BACKEND PLUGIN — pre_coder HOOK")
        self._append(f"Run started : {datetime.now(timezone.utc).isoformat()}")
        self._append(f"Log file    : {self.log_path}")
        self._append("=" * 70)
        self._append("")

    def _append(self, line: str):
        self._lines.append(line)
        # Write immediately so partial logs survive crashes
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

    def write_footer(self, passed: bool, error_count: int, total_elapsed: float):
        self._append("")
        self._append("=" * 70)
        self._append(f"Result      : {'PASSED' if passed else 'FAILED'}")
        self._append(f"Errors      : {error_count}")
        self._append(f"Total time  : {total_elapsed:.3f}s")
        self._append(f"Run ended   : {datetime.now(timezone.utc).isoformat()}")
        self._append("=" * 70)


# ── Validation Checks ─────────────────────────────────────────────────────────


def check_summary_block_present(
    architect_output: str, logger: HookLogger
) -> tuple[bool, dict]:
    """
    Check 1: Architect output contains a parseable ARCHITECT SUMMARY block.
    This block is the machine-readable contract between Architect and orchestrator.
    Without it, no downstream state can be updated reliably.
    """
    logger.section("Check 1 — ARCHITECT SUMMARY block")

    pattern = r"=== ARCHITECT SUMMARY ===(.*?)=== END ARCHITECT SUMMARY ==="
    match = re.search(pattern, architect_output, re.DOTALL)

    if not match:
        logger.error("ARCHITECT SUMMARY block not found in output.")
        logger.error(
            "Architect must end output with a correctly formatted summary block."
        )
        return False, {}

    raw = match.group(1).strip()
    logger.info("ARCHITECT SUMMARY block found.")
    logger.info(f"Raw block ({len(raw)} chars):\n{raw}")

    # Attempt to parse key fields from the YAML-like block
    # context_builder.py does full parsing; we do a structural check here only
    parsed = {}
    for field in [
        "domains_touched",
        "apps_touched",
        "pipeline",
        "feature_type",
        "inter_plugin_contracts",
    ]:
        field_match = re.search(rf"^{field}:\s*(.+)$", raw, re.MULTILINE)
        if field_match:
            parsed[field] = field_match.group(1).strip()
            logger.info(f"  Found field: {field} = {parsed[field]}")
        else:
            logger.error(f"  Missing required field in summary block: {field}")

    missing = [
        f
        for f in ["domains_touched", "apps_touched", "pipeline", "feature_type"]
        if f not in parsed
    ]
    if missing:
        return False, parsed

    logger.info("ARCHITECT SUMMARY block is structurally valid.")
    return True, parsed


def check_domains_valid(
    parsed_summary: dict, logger: HookLogger
) -> tuple[bool, list[str]]:
    """
    Check 2: All declared domains exist in the known domain registry (reference.md).
    An unknown domain means context_builder.py will silently skip it,
    producing a Coder with missing context.
    """
    logger.section("Check 2 — Domain validity")

    raw_domains = parsed_summary.get("domains_touched", "[]")
    # Parse list-like string: [async_tasks, payments] or async_tasks, payments
    domains = re.findall(r"[\w_]+", raw_domains)
    logger.info(f"Declared domains: {domains}")

    invalid = [d for d in domains if d not in VALID_DOMAINS]
    if invalid:
        for d in invalid:
            logger.error(
                f"  Unknown domain: '{d}'. Valid domains: {sorted(VALID_DOMAINS)}"
            )
        return False, domains

    logger.info(f"All {len(domains)} domains are valid.")
    return True, domains


def check_apps_exist(
    parsed_summary: dict, project_root: Path, logger: HookLogger
) -> bool:
    """
    Check 3: All declared apps exist under backend/apps/.
    A declared app that doesn't exist means the Coder will try to write to
    a non-existent directory and produce broken paths.
    """
    logger.section("Check 3 — App existence")

    raw_apps = parsed_summary.get("apps_touched", "[]")
    apps = re.findall(r"[\w_]+", raw_apps)
    logger.info(f"Declared apps: {apps}")

    all_exist = True
    for app in apps:
        app_path = project_root / "backend" / "apps" / app
        if not app_path.exists():
            logger.error(f"  App directory not found: {app_path}")
            all_exist = False
        else:
            readme_path = app_path / "Readme.md"
            if not readme_path.exists():
                # Warn only — not a hard failure (matches warn_and_continue policy)
                logger.warn(
                    f"  App '{app}' exists but Readme.md is missing. "
                    f"Coder will receive a CONTEXT WARNING for this app."
                )
            else:
                logger.info(f"  App '{app}': exists, Readme.md present.")

    return all_exist


def check_pipeline_stages_valid(parsed_summary: dict, logger: HookLogger) -> bool:
    """
    Check 4: All declared pipeline stages are valid enum values.
    Invalid stage names will cause the orchestrator to try to invoke
    a subagent that doesn't exist.
    """
    logger.section("Check 4 — Pipeline stage validity")

    raw_pipeline = parsed_summary.get("pipeline", "[]")
    stages = re.findall(r"[\w_]+", raw_pipeline)
    logger.info(f"Declared pipeline: {stages}")

    if not stages:
        logger.error("Pipeline is empty. Architect must declare at least one stage.")
        return False

    invalid = [s for s in stages if s not in VALID_PIPELINE_STAGES]
    if invalid:
        for s in invalid:
            logger.error(
                f"  Invalid stage: '{s}'. Valid stages: {sorted(VALID_PIPELINE_STAGES)}"
            )
        return False

    logger.info(f"All {len(stages)} pipeline stages are valid.")
    return True


def check_decision_gaps_resolved(
    architect_output: str, plugin_state: dict, logger: HookLogger
) -> bool:
    """
    Check 5: No unresolved decision gaps remain.
    If the Architect declared decision gaps, the orchestrator must have
    collected user answers and written them into architect_notes before
    this hook runs. If gaps are still open, the Coder will be missing
    critical decisions.
    """
    logger.section("Check 5 — Decision gap resolution")

    gap_pattern = (
        r"decision_gaps:(.*?)(?:architect_notes_append:|=== END ARCHITECT SUMMARY ===)"
    )
    gap_match = re.search(gap_pattern, architect_output, re.DOTALL)

    if not gap_match:
        logger.info("No decision_gaps field found in summary. Assuming none declared.")
        return True

    gap_block = gap_match.group(1).strip()
    if gap_block in ("none", "[]", ""):
        logger.info("No decision gaps declared by Architect.")
        return True

    # Gaps were declared — check architect_notes contains answers
    architect_notes = plugin_state.get("architect_notes", "")
    if not architect_notes:
        logger.error("Decision gaps were declared but architect_notes is empty.")
        logger.error(
            "Orchestrator must collect user answers and write them to "
            "plugin_state.json → architect_notes before re-running this hook."
        )
        return False

    logger.info("Decision gaps declared and architect_notes is populated.")
    logger.info(
        "Assuming gaps are resolved — orchestrator is responsible for verifying answers."
    )
    return True


def check_handoff_block_present(architect_output: str, logger: HookLogger) -> bool:
    """
    Check 6: Architect output contains a ARCHITECT HANDOFF block.
    Without an explicit handoff, the Architect may not have completed its task —
    the output could be truncated or abandoned mid-generation.
    """
    logger.section("Check 6 — ARCHITECT HANDOFF block")

    if "=== ARCHITECT HANDOFF ===" not in architect_output:
        logger.error("ARCHITECT HANDOFF block not found.")
        logger.error("Architect output may be incomplete or truncated.")
        return False

    logger.info("ARCHITECT HANDOFF block present.")
    return True


def check_feature_type_valid(
    parsed_summary: dict, plugin_state: dict, logger: HookLogger
) -> bool:
    """
    Check 7: feature_type in summary matches plugin_state.json.
    If they disagree, the orchestrator and Architect are operating on
    different assumptions about what kind of work this is.
    """
    logger.section("Check 7 — Feature type consistency")

    summary_type = parsed_summary.get("feature_type", "").strip()
    state_type = plugin_state.get("feature_type", "").strip()

    logger.info(f"Summary declares feature_type: '{summary_type}'")
    logger.info(f"plugin_state.json has feature_type: '{state_type}'")

    if summary_type not in VALID_FEATURE_TYPES:
        logger.error(
            f"feature_type '{summary_type}' is not a valid value. "
            f"Must be one of: {sorted(VALID_FEATURE_TYPES)}"
        )
        return False

    if state_type and summary_type != state_type:
        logger.error(
            f"feature_type mismatch: summary says '{summary_type}', "
            f"plugin_state.json says '{state_type}'."
        )
        logger.error("Architect must match the feature_type set at session start.")
        return False

    logger.info("feature_type is valid and consistent.")
    return True


# ── Output Builder ────────────────────────────────────────────────────────────


def build_output(passed: bool, errors: list[dict], domains: list[str]) -> dict:
    """
    Builds the structured JSON output the orchestrator reads from stdout.
    Format matches the hook output contract defined in orchestrator.md.
    """
    output = {
        "passed": passed,
        "hook_name": "pre_coder",
    }

    if passed:
        output["validated_domains"] = domains
    else:
        output["errors"] = errors
        output["retry_prompt"] = (
            "The Architect output failed validation. "
            "Re-invoke the Architect subagent with these errors as context. "
            "The Architect must fix its output and re-produce the ARCHITECT SUMMARY "
            "and ARCHITECT HANDOFF blocks correctly."
        )

    return output


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    hook_start = time.time()

    parser = argparse.ArgumentParser(
        description="pre_coder hook — validates Architect output"
    )
    parser.add_argument(
        "--architect-output",
        required=True,
        help="Path to file containing Architect subagent output",
    )
    parser.add_argument(
        "--plugin-state", required=True, help="Path to plugin_state.json"
    )
    parser.add_argument(
        "--log-dir",
        required=True,
        help="Path to feature log directory (.agents/logs/<feature_slug>/)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to project root (default: current directory)",
    )
    args = parser.parse_args()

    log_dir = Path(args.log_dir)
    project_root = Path(args.project_root).resolve()
    logger = HookLogger(log_dir, hook_start)

    logger.section("Inputs")
    logger.info(f"Architect output file : {args.architect_output}")
    logger.info(f"Plugin state file     : {args.plugin_state}")
    logger.info(f"Project root          : {project_root}")

    # ── Load inputs ───────────────────────────────────────────────────────────
    try:
        architect_output = Path(args.architect_output).read_text(encoding="utf-8")
        logger.info(f"Architect output loaded ({len(architect_output)} chars).")
    except Exception as e:
        logger.error(f"Failed to read architect output: {e}")
        output = build_output(
            False,
            [
                {
                    "issue": f"Cannot read architect output file: {e}",
                    "convention_ref": "orchestrator.md#subagent-invocation",
                }
            ],
            [],
        )
        logger.write_footer(False, 1, time.time() - hook_start)
        print(json.dumps(output, indent=2))
        sys.exit(1)

    try:
        plugin_state = json.loads(Path(args.plugin_state).read_text(encoding="utf-8"))
        logger.info("plugin_state.json loaded.")
    except Exception as e:
        logger.error(f"Failed to read plugin_state.json: {e}")
        output = build_output(
            False,
            [
                {
                    "issue": f"Cannot read plugin_state.json: {e}",
                    "convention_ref": "orchestrator.md#state-files",
                }
            ],
            [],
        )
        logger.write_footer(False, 1, time.time() - hook_start)
        print(json.dumps(output, indent=2))
        sys.exit(1)

    # ── Run checks ────────────────────────────────────────────────────────────
    errors = []
    domains = []

    summary_ok, parsed_summary = check_summary_block_present(architect_output, logger)
    if not summary_ok:
        errors.append(
            {
                "file": args.architect_output,
                "issue": "ARCHITECT SUMMARY block missing or incomplete.",
                "convention_ref": "agents/architect.txt#step-6-summarise-for-state",
            }
        )

    if parsed_summary:
        domains_ok, domains = check_domains_valid(parsed_summary, logger)
        if not domains_ok:
            errors.append(
                {
                    "file": args.architect_output,
                    "issue": "One or more declared domains are not in the known domain registry.",
                    "convention_ref": "context/reference.md#domain-registry",
                }
            )

        apps_ok = check_apps_exist(parsed_summary, project_root, logger)
        if not apps_ok:
            errors.append(
                {
                    "file": args.architect_output,
                    "issue": "One or more declared apps do not exist under backend/apps/.",
                    "convention_ref": "backend/Readme.md#directory-structure",
                }
            )

        pipeline_ok = check_pipeline_stages_valid(parsed_summary, logger)
        if not pipeline_ok:
            errors.append(
                {
                    "file": args.architect_output,
                    "issue": "One or more pipeline stages are not valid enum values.",
                    "convention_ref": "plugins/backend-plugin/plugin_state.schema.json#pipeline",
                }
            )

        feature_type_ok = check_feature_type_valid(parsed_summary, plugin_state, logger)
        if not feature_type_ok:
            errors.append(
                {
                    "file": args.architect_output,
                    "issue": "feature_type in ARCHITECT SUMMARY does not match plugin_state.json.",
                    "convention_ref": "orchestrator.md#state-files",
                }
            )

    gaps_ok = check_decision_gaps_resolved(architect_output, plugin_state, logger)
    if not gaps_ok:
        errors.append(
            {
                "file": args.plugin_state,
                "issue": "Decision gaps declared but architect_notes is empty. "
                "Orchestrator must collect user answers before Coder is invoked.",
                "convention_ref": "orchestrator.md#decision-gaps-vs-prerequisite-gaps",
            }
        )

    handoff_ok = check_handoff_block_present(architect_output, logger)
    if not handoff_ok:
        errors.append(
            {
                "file": args.architect_output,
                "issue": "ARCHITECT HANDOFF block missing. Output may be incomplete.",
                "convention_ref": "agents/architect.txt#handoff",
            }
        )

    # ── Result ────────────────────────────────────────────────────────────────
    passed = len(errors) == 0
    total_elapsed = time.time() - hook_start

    logger.section("Summary")
    logger.info(f"Checks run    : 7")
    logger.info(f"Errors found  : {len(errors)}")
    logger.info(f"Result        : {'PASSED' if passed else 'FAILED'}")
    logger.write_footer(passed, len(errors), total_elapsed)

    output = build_output(passed, errors, domains)
    print(json.dumps(output, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
