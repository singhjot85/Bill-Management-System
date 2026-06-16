"""
checkpoint.py — BMA Backend Pipeline State & Rollback Manager

Owns four responsibilities:
  1. Session lifecycle   — init / resume / complete a feature session
  2. State mutations      — advance_stage, record_file_touch, set_block, clear_block,
                             increment_retry, reset_retry
  3. Rollback              — selective, file-level undo. HUMAN-ONLY. See "Rollback
                             Safety Boundary" below — this is not negotiable.
  4. Schema validation     — every write is validated against the matching
                             .schema.json before being committed to disk

This is a LOGIC OUTLINE, not a full implementation. Function bodies are
sketched with comments describing what they must do. You implement the
actual logic — this is the learning exercise, per our agreement.

---

ROLLBACK SAFETY BOUNDARY (read before touching this file):

The orchestrator (and by extension, any subagent) must NEVER be able to trigger
rollback() programmatically. This script enforces that boundary structurally,
not just by convention:

  - rollback() is only reachable via the `if __name__ == "__main__"` CLI entrypoint,
    guarded by `cmd == "rollback"`.
  - It is NOT exported as an importable function with a stable public signature
    intended for orchestrator use. If you import this module elsewhere, the
    rollback logic should require constructing a RollbackConfirmation object
    that can only be created by reading an actual interactive terminal response
    (see _require_interactive_confirmation below) — there is no parameter that
    bypasses this, intentionally. Do not add a --yes, --force, or env var bypass.
  - The orchestrator's only sanctioned interaction with rollback is to TELL the
    user how to invoke it manually: "Run `python checkpoint.py rollback` to undo
    changes from this session." It never invokes the subprocess itself.

If you find yourself wanting to make rollback callable by the orchestrator for
convenience — stop. That convenience is exactly the failure mode this boundary
exists to prevent. Re-read orchestrator.md § 1 (Hard Boundaries) first.
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — adjust these paths to match actual repo layout at implementation time
# ---------------------------------------------------------------------------

AGENTS_ROOT = Path(".agents")
PLUGIN_NAME = "backend-plugin"
PLUGIN_ROOT = AGENTS_ROOT / "plugins" / PLUGIN_NAME

SESSION_STATE_PATH = AGENTS_ROOT / "session_state.json"
SESSION_STATE_SCHEMA_PATH = AGENTS_ROOT / "session_state.schema.json"
SESSION_STATE_TEMPLATE_PATH = AGENTS_ROOT / "session_state.template.json"

PLUGIN_STATE_PATH = PLUGIN_ROOT / "plugin_state.json"
PLUGIN_STATE_SCHEMA_PATH = PLUGIN_ROOT / "plugin_state.schema.json"
PLUGIN_STATE_TEMPLATE_PATH = PLUGIN_ROOT / "plugin_state.template.json"

PROJECT_ROOT = Path(".")  # checkpoint.py assumed to run from repo root


# =============================================================================
# 1. SESSION LIFECYCLE
# =============================================================================

def init_session(feature_name: str, feature_type: str, active_plugins: list[str]) -> None:
    """
    Starts a brand new feature session.

    Must:
      - Refuse to run if SESSION_STATE_PATH already exists with a non-empty
        active_feature — a session is already in progress. Direct the human to
        `resume` or `complete` it first. Do not silently overwrite.
      - Copy SESSION_STATE_TEMPLATE_PATH -> SESSION_STATE_PATH.
      - Populate active_feature, feature_type is NOT a session_state field —
        confirm that (see schema) — only plugin_state carries feature_type.
      - Populate active_plugins.
      - For each plugin in active_plugins: copy that plugin's
        plugin_state.template.json -> plugin_state.json, populate `feature`
        and `feature_type` fields.
      - Validate both resulting files against their schemas before considering
        init complete (see validate_against_schema below).
      - Print a confirmation summary to the human: feature name, plugins,
        and the path to both state files.

    Must NOT:
      - Touch any source file in backend/ or frontend/.
      - Run any git command.
    """
    pass  # TODO: implement


def resume_session() -> dict:
    """
    Resumes an existing in-progress session. Read-only — does not mutate state.

    Must:
      - Read SESSION_STATE_PATH. If missing or active_feature is empty, raise
        a clear error: "No active session found. Use init_session first."
      - For each plugin in active_plugins, read its plugin_state.json.
      - Validate both against their schemas. If validation fails, surface the
        exact schema violation — do not attempt to auto-repair a malformed
        state file. Malformed state is a signal something already went wrong;
        silently patching it hides that.
      - Return a structured summary dict the orchestrator can act on:
            {
              "feature": ...,
              "active_plugins": [...],
              "per_plugin": {
                "backend-plugin": {
                  "current_stage": ...,
                  "completed_stages": [...],
                  "pending_stages": [...],
                  "blocked_on": ... or None,
                }
              }
            }
      - This is the function the orchestrator calls per orchestrator.md § 3
        "Resuming a Partial Pipeline" — it must never infer completion from
        reading source files, only from this returned state.
    """
    pass  # TODO: implement


def complete_session() -> None:
    """
    Marks a feature session as finished and archives its state.

    Must:
      - Confirm plugin_state.json → pending_stages is empty and blocked_on is
        null for every active plugin. Refuse to complete otherwise — print
        exactly what's outstanding.
      - Move (not copy) session_state.json and each plugin_state.json into
        an archive location, e.g. .agents/logs/<feature_slug>/final_state/.
        This preserves history for later review without it being mistaken
        for a live, resumable session.
      - Reset session_state.json and plugin_state.json back to their
        templates (empty), ready for the next feature.
    """
    pass  # TODO: implement


# =============================================================================
# 2. STATE MUTATION HELPERS
# =============================================================================
# These are the small, frequent operations the orchestrator calls during a
# pipeline run. Each one: reads current state, applies one mutation, validates
# against schema, writes atomically (write to temp file, then rename — never
# leave plugin_state.json partially written if the process is interrupted
# mid-write), and logs the mutation.

def advance_stage(
    plugin_name: str, completed_stage: str, next_stage: str | None,
    domains_touched: list[str] | None = None, apps_touched: list[str] | None = None,
) -> None:
    """
    Moves a stage from pending to completed, advances current_stage.

    Special case: when completed_stage == "architecture", the orchestrator
    must pass domains_touched and apps_touched (the values pre_coder.py
    already parsed and returned as parsed_domains_touched / parsed_apps_touched
    in its JSON output) so this function writes them into plugin_state.json's
    domains_touched and apps_touched fields. For every other stage these
    parameters should be None and left untouched — domains/apps are set once,
    at architecture completion, not re-derived per stage.

    Must:
      - Assert completed_stage == current plugin_state["current_stage"] before
        mutating — refuses to advance a stage that isn't actually the active one.
      - Append completed_stage to completed_stages.
      - Remove completed_stage from pending_stages.
      - If completed_stage == "architecture" and domains_touched/apps_touched
        are provided: overwrite plugin_state["domains_touched"] and
        ["apps_touched"] with these values (full overwrite, not append —
        these reflect the Architect's final declared scope for the feature).
      - Set current_stage to next_stage (or to pending_stages[0] if next_stage
        is None and pending_stages is non-empty; if pending_stages is now
        empty, set current_stage to "" — pipeline is done).
      - Update last_validated_at to current UTC timestamp.
      - Validate full resulting state against plugin_state.schema.json.
      - Write atomically.
    """
    pass  # TODO: implement


def record_file_touch(plugin_name: str, path: str, operation: str, stage: str) -> None:
    """
    Appends one entry to files_touched. Called once per file declared in a
    subagent's handoff block (CODER HANDOFF / TESTER HANDOFF).

    Must:
      - operation must be exactly "created" or "modified" — validate against
        the schema's enum, reject anything else with a clear error.
      - Deduplicate: if the same path was already touched earlier in this
        session with operation "created", a later "modified" entry for the
        same path should NOT downgrade it back to "created" on rollback
        consideration — but should still be appended as a new timestamped
        entry, since the rollback manifest is a log, not a single current-state
        map. (Rollback logic in section 3 must read the FIRST entry per path
        to decide created-vs-modified, not the latest.)
      - Append entry with current UTC timestamp.
      - Validate and write atomically.
    """
    pass  # TODO: implement


def set_block(plugin_name: str, hook_name: str, stage: str, summary: str) -> None:
    """
    Sets blocked_on when a hook hard-stops (max retries exhausted).

    Must:
      - Construct the blocked_on object matching the schema's required shape
        (hook_name, stage, summary, blocked_at).
      - Refuse to advance any stage while blocked_on is set — this is enforced
        here by other functions checking blocked_on is None as a precondition,
        not just by orchestrator discipline.
      - Validate and write atomically.
    """
    pass  # TODO: implement


def clear_block(plugin_name: str) -> None:
    """
    Clears blocked_on. Per orchestrator.md, this should only happen after
    explicit user intervention — this function itself doesn't enforce WHO
    calls it (that's the orchestrator's responsibility per its own rules),
    but it should require a non-empty `resolution_note` argument so there's
    always a record of why the block was cleared.

    Must:
      - Require a resolution_note: str argument — refuse to clear with an
        empty string.
      - Append the resolution_note to architect_notes (append-only, per schema
        description) rather than discarding it.
      - Set blocked_on back to None.
      - Validate and write atomically.
    """
    pass  # TODO: implement


def increment_retry(plugin_name: str, hook_name: str) -> int:
    """
    Increments retry_counts[hook_name] by 1. Returns the new count.

    Must:
      - hook_name must be one of the three known hooks — validate against schema enum.
      - Validate and write atomically.
      - Return new count so the orchestrator can immediately compare against
        that hook's MAX_RETRIES without a second read.
    """
    pass  # TODO: implement


def reset_retry(plugin_name: str, hook_name: str, resolution_note: str) -> None:
    """
    Resets a retry count to 0. Per orchestrator.md § 5, this must only happen
    with explicit user instruction — same pattern as clear_block: require a
    resolution_note, never allow a silent reset.
    """
    pass  # TODO: implement


# =============================================================================
# 3. ROLLBACK — HUMAN-ONLY, INTERACTIVE-ONLY
# =============================================================================

class RollbackConfirmation:
    """
    Opaque token proving an interactive human confirmed the rollback.
    Cannot be constructed except by _require_interactive_confirmation().
    There is deliberately no alternate constructor, no classmethod that
    accepts a pre-supplied boolean, and no way to build this from a
    non-interactive context. This is the structural enforcement of the
    "human-only" boundary — not just a docstring promise.
    """
    def __init__(self, _sentinel: object):
        if _sentinel is not _CONFIRMATION_SENTINEL:
            raise RuntimeError(
                "RollbackConfirmation cannot be constructed directly. "
                "It may only be produced by an interactive terminal prompt."
            )


_CONFIRMATION_SENTINEL = object()


def _require_interactive_confirmation(files_to_affect: list[dict]) -> RollbackConfirmation:
    """
    Must:
      - Detect whether stdin is an actual interactive TTY
        (e.g. sys.stdin.isatty()). If not, refuse outright — print
        "Rollback requires an interactive terminal session." and exit
        nonzero. This blocks any attempt to pipe a "yes" into this script
        from an automated context, including from the orchestrator itself.
      - Print the full list of files_to_affect with their operation
        (created -> will be deleted, modified -> will be reverted to
        HEAD), so the human sees exactly what is about to happen.
      - Prompt: "Type the feature name exactly to confirm rollback: "
        and compare the typed input against plugin_state["feature"].
        Requiring the exact feature name (not just "y/n") makes an
        accidental keypress unable to trigger this.
      - Only after exact match, construct and return
        RollbackConfirmation(_CONFIRMATION_SENTINEL).
    """
    pass  # TODO: implement


def rollback(plugin_name: str, confirmation: RollbackConfirmation) -> None:
    """
    Selectively undoes every file change recorded in files_touched for the
    CURRENT session only. Never runs git reset or git clean — per the
    project's original constraint.

    Must:
      - Accept only a RollbackConfirmation instance — type-check it; if it's
        not actually an instance of that class, refuse. This is defense in
        depth on top of _require_interactive_confirmation already having run.
      - Read files_touched. For each unique path, find its FIRST recorded
        operation (see note in record_file_touch above):
          - if first operation == "created": delete the file from disk
            (Path.unlink). If the file doesn't exist, log and skip — don't
            error on an already-gone file.
          - if first operation == "modified": run
            `git checkout HEAD -- <path>` scoped to that single path only.
            Never call git checkout/reset without an explicit path argument.
      - Never touch any file NOT in files_touched, even if it looks related.
      - After processing all files, clear files_touched in plugin_state.json
        (the rollback consumed it) but leave completed_stages, pipeline, etc.
        untouched — rollback undoes file changes, not pipeline progress
        bookkeeping. (Open question for you to decide at implementation time:
        should a rollback also reset current_stage backward? Recommend: no —
        treat rollback as "undo the files, then decide manually whether to
        re-run a stage." Keeps the two concerns separate.)
      - Print a summary: N files deleted, N files reverted, any skips/errors.
    """
    pass  # TODO: implement


# =============================================================================
# 4. SCHEMA VALIDATION
# =============================================================================

def validate_against_schema(data: dict, schema_path: Path) -> tuple[bool, list[str]]:
    """
    Validates `data` against the JSON Schema at schema_path.

    Must:
      - Use the `jsonschema` package (pip install jsonschema --break-system-packages
        at implementation time) — do not hand-roll schema validation.
      - Return (True, []) on success, (False, [list of human-readable error
        messages]) on failure. Each message should include the failing field
        path so the orchestrator's error surfacing is precise, not generic.
      - This function is called before every write in sections 1 and 2 above.
        No state file write happens without passing this check first.
    """
    pass  # TODO: implement


def _atomic_write(path: Path, data: dict) -> None:
    """
    Writes `data` as JSON to `path` atomically: write to a temp file in the
    same directory, then os.replace() it over the target. Prevents a crash
    mid-write from leaving plugin_state.json truncated or invalid JSON.
    """
    pass  # TODO: implement


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    # Sketch only — implement actual argparse at build time.
    #
    # Subcommands:
    #   init       --feature "<name>" --type new_feature --plugins backend-plugin
    #   resume
    #   complete
    #   rollback   <plugin_name>     <-- the ONLY path that reaches rollback().
    #                                    Must call _require_interactive_confirmation()
    #                                    itself, here, inline. Do not refactor this
    #                                    into a function the orchestrator could import
    #                                    and call with a fabricated confirmation.
    #
    # Explicitly NOT supported, by design, ever:
    #   --yes / --force / -y flags on rollback
    #   an environment variable that skips the prompt
    #   a "rollback_async" or programmatic API for rollback
    pass  # TODO: implement argparse wiring