"""
checkpoint.py — BMA Backend Pipeline State & Rollback Manager
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import jsonschema

# ---------------------------------------------------------------------------
# Configuration
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

PROJECT_ROOT = Path(".")

# =============================================================================
# 1. SESSION LIFECYCLE
# =============================================================================

def init_session(feature_name: str, feature_type: str, active_plugins: list[str]) -> None:
    if SESSION_STATE_PATH.exists():
        try:
            with open(SESSION_STATE_PATH, "r") as f:
                existing = json.load(f)
            if existing.get("active_feature"):
                print(f"Error: A session is already in progress ({existing.get('active_feature')}). Complete or rollback first.", file=sys.stderr)
                sys.exit(1)
        except Exception:
            pass
    
    with open(SESSION_STATE_TEMPLATE_PATH, "r") as f:
        session_data = json.load(f)
    session_data["active_feature"] = feature_name
    session_data["active_plugins"] = active_plugins
    session_data["symphony_mode"] = len(active_plugins) > 1
    
    ok, errs = validate_against_schema(session_data, SESSION_STATE_SCHEMA_PATH)
    if not ok:
        print(f"Error validating session state: {errs}", file=sys.stderr)
        sys.exit(1)
        
    _atomic_write(SESSION_STATE_PATH, session_data)
    
    for plugin in active_plugins:
        p_root = AGENTS_ROOT / "plugins" / plugin
        p_state_path = p_root / "plugin_state.json"
        p_template_path = p_root / "plugin_state.template.json"
        p_schema_path = p_root / "plugin_state.schema.json"
        
        with open(p_template_path, "r") as f:
            p_data = json.load(f)
        p_data["feature"] = feature_name
        p_data["feature_type"] = feature_type
        
        if plugin == "backend-plugin":
            if feature_type == "bug_fix":
                pipeline = ["happy_path", "happy_path_tests", "full_implementation", "full_implementation_tests"]
            elif feature_type == "refactor":
                pipeline = ["architecture", "documentation", "happy_path", "happy_path_tests", "full_implementation", "full_implementation_tests", "final_documentation"]
            elif feature_type == "infra_change":
                pipeline = ["dependency_setup", "service_validation", "full_implementation", "full_implementation_tests"]
            else: # new_feature
                pipeline = ["architecture", "documentation", "dependency_setup", "service_validation", "happy_path", "happy_path_tests", "full_implementation", "full_implementation_tests", "final_documentation"]
            p_data["pipeline"] = pipeline
            p_data["current_stage"] = pipeline[0]
            p_data["pending_stages"] = pipeline.copy()
            p_data["completed_stages"] = []
        elif plugin == "frontend-plugin":
            pipeline = ["DESIGN_DRAFT", "DESIGN_LINT", "DESIGN_REVIEW", "DESIGN_APPROVED", "CODE_GEN", "CODE_LINT", "CODE_SELF_CHECK", "MANUAL_QA_PENDING"]
            p_data["pipeline"] = pipeline
            p_data["current_stage"] = pipeline[0]
            p_data["pending_stages"] = pipeline.copy()
            p_data["completed_stages"] = []
            
        ok, errs = validate_against_schema(p_data, p_schema_path)
        if not ok:
            print(f"Error validating {plugin} state: {errs}", file=sys.stderr)
            sys.exit(1)
        _atomic_write(p_state_path, p_data)
        
    print(f"Initialized session: {feature_name}")


def resume_session() -> dict:
    if not SESSION_STATE_PATH.exists():
        raise FileNotFoundError("No active session found. Use init_session first.")
    with open(SESSION_STATE_PATH, "r") as f:
        session_data = json.load(f)
    if not session_data.get("active_feature"):
        raise ValueError("No active session found. Use init_session first.")
        
    ok, errs = validate_against_schema(session_data, SESSION_STATE_SCHEMA_PATH)
    if not ok:
        raise ValueError(f"Session state schema violation: {errs}")
        
    res = {
        "feature": session_data["active_feature"],
        "active_plugins": session_data["active_plugins"],
        "per_plugin": {}
    }
    
    for plugin in session_data["active_plugins"]:
        p_root = AGENTS_ROOT / "plugins" / plugin
        p_state_path = p_root / "plugin_state.json"
        p_schema_path = p_root / "plugin_state.schema.json"
        
        if not p_state_path.exists():
            raise FileNotFoundError(f"Missing state file for {plugin}")
        with open(p_state_path, "r") as f:
            p_data = json.load(f)
            
        ok, errs = validate_against_schema(p_data, p_schema_path)
        if not ok:
            raise ValueError(f"Plugin {plugin} state schema violation: {errs}")
            
        res["per_plugin"][plugin] = {
            "current_stage": p_data["current_stage"],
            "completed_stages": p_data["completed_stages"],
            "pending_stages": p_data["pending_stages"],
            "blocked_on": p_data.get("blocked_on")
        }
    return res


def complete_session() -> None:
    if not SESSION_STATE_PATH.exists():
        print("No active session to complete.", file=sys.stderr)
        return
    with open(SESSION_STATE_PATH, "r") as f:
        session_data = json.load(f)
        
    feature_name = session_data["active_feature"]
    feature_slug = feature_name.lower().replace(" ", "-")
    
    for plugin in session_data["active_plugins"]:
        p_root = AGENTS_ROOT / "plugins" / plugin
        p_state_path = p_root / "plugin_state.json"
        with open(p_state_path, "r") as f:
            p_data = json.load(f)
        if p_data["pending_stages"]:
            print(f"Cannot complete: plugin {plugin} still has pending stages: {p_data['pending_stages']}", file=sys.stderr)
            sys.exit(1)
        if p_data["blocked_on"]:
            print(f"Cannot complete: plugin {plugin} is blocked on: {p_data['blocked_on']}", file=sys.stderr)
            sys.exit(1)
            
    archive_dir = AGENTS_ROOT / "logs" / feature_slug / "final_state"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    shutil.move(str(SESSION_STATE_PATH), str(archive_dir / "session_state.json"))
    for plugin in session_data["active_plugins"]:
        p_root = AGENTS_ROOT / "plugins" / plugin
        p_state_path = p_root / "plugin_state.json"
        p_template_path = p_root / "plugin_state.template.json"
        shutil.move(str(p_state_path), str(archive_dir / f"{plugin}_state.json"))
        shutil.copy(str(p_template_path), str(p_state_path))
        
    shutil.copy(str(SESSION_STATE_TEMPLATE_PATH), str(SESSION_STATE_PATH))
    print(f"Completed session and archived states for: {feature_name}")


# =============================================================================
# 2. STATE MUTATION HELPERS
# =============================================================================

def advance_stage(
    plugin_name: str, completed_stage: str, next_stage: str | None,
    domains_touched: list[str] | None = None, apps_touched: list[str] | None = None,
) -> None:
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    if p_data.get("blocked_on"):
        raise ValueError(f"Cannot advance: state is blocked on {p_data['blocked_on']}")
        
    current = p_data.get("current_stage")
    if completed_stage != current:
        raise ValueError(f"Cannot advance: expected completed_stage to be '{current}', got '{completed_stage}'")
        
    p_data["completed_stages"].append(completed_stage)
    if completed_stage in p_data["pending_stages"]:
        p_data["pending_stages"].remove(completed_stage)
        
    if completed_stage == "architecture":
        if domains_touched is not None:
            p_data["domains_touched"] = domains_touched
        if apps_touched is not None:
            p_data["apps_touched"] = apps_touched
            
    if next_stage is not None:
        p_data["current_stage"] = next_stage
    elif p_data["pending_stages"]:
        p_data["current_stage"] = p_data["pending_stages"][0]
    else:
        p_data["current_stage"] = "completed"
        
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Advancing stage resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)


def record_file_touch(plugin_name: str, path: str, operation: str, stage: str) -> None:
    if operation not in ["created", "modified"]:
        raise ValueError("operation must be exactly 'created' or 'modified'")
        
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    p_data["files_touched"].append({
        "path": path,
        "operation": operation,
        "stage": stage,
        "touched_at": datetime.now(timezone.utc).isoformat()
    })
    
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Recording file touch resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)


def set_block(plugin_name: str, hook_name: str, stage: str, summary: str) -> None:
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    p_data["blocked_on"] = {
        "hook_name": hook_name,
        "stage": stage,
        "summary": summary,
        "blocked_at": datetime.now(timezone.utc).isoformat()
    }
    
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Setting block resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)


def clear_block(plugin_name: str, resolution_note: str) -> None:
    if not resolution_note:
        raise ValueError("resolution_note is required and cannot be empty")
        
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    p_data["blocked_on"] = None
    if p_data.get("architect_notes"):
        p_data["architect_notes"] += "\n" + resolution_note
    else:
        p_data["architect_notes"] = resolution_note
        
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Clearing block resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)


def increment_retry(plugin_name: str, hook_name: str) -> int:
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    if "retry_counts" not in p_data or p_data["retry_counts"] is None:
        p_data["retry_counts"] = {}
    if hook_name not in p_data["retry_counts"]:
        p_data["retry_counts"][hook_name] = 0
    p_data["retry_counts"][hook_name] += 1
    new_count = p_data["retry_counts"][hook_name]
    
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Incrementing retry resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)
    return new_count


def reset_retry(plugin_name: str, hook_name: str, resolution_note: str) -> None:
    if not resolution_note:
        raise ValueError("resolution_note is required and cannot be empty")
        
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    if "retry_counts" not in p_data or p_data["retry_counts"] is None:
        p_data["retry_counts"] = {}
    p_data["retry_counts"][hook_name] = 0
    if p_data.get("architect_notes"):
        p_data["architect_notes"] += "\n" + resolution_note
    else:
        p_data["architect_notes"] = resolution_note
        
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Resetting retry resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)


# =============================================================================
# 3. ROLLBACK — HUMAN-ONLY, INTERACTIVE-ONLY
# =============================================================================

class RollbackConfirmation:
    def __init__(self, _sentinel: object):
        if _sentinel is not _CONFIRMATION_SENTINEL:
            raise RuntimeError(
                "RollbackConfirmation cannot be constructed directly. "
                "It may only be produced by an interactive terminal prompt."
            )

_CONFIRMATION_SENTINEL = object()


def _require_interactive_confirmation(files_to_affect: list[dict], feature_name: str) -> RollbackConfirmation:
    if not sys.stdin.isatty():
        print("Rollback requires an interactive terminal session.", file=sys.stderr)
        sys.exit(1)
    print("\nWARNING: You are about to rollback the following file changes:")
    for f in files_to_affect:
        print(f"  - {f['path']} ({f['operation']})")
    val = input(f"\nType the feature name '{feature_name}' exactly to confirm rollback: ")
    if val != feature_name:
        print("Rollback cancelled. Feature name did not match.", file=sys.stderr)
        sys.exit(1)
    return RollbackConfirmation(_CONFIRMATION_SENTINEL)


def rollback(plugin_name: str, confirmation: RollbackConfirmation) -> None:
    if not isinstance(confirmation, RollbackConfirmation):
        raise TypeError("confirmation must be a RollbackConfirmation instance")
        
    p_root = AGENTS_ROOT / "plugins" / plugin_name
    p_state_path = p_root / "plugin_state.json"
    p_schema_path = p_root / "plugin_state.schema.json"
    
    with open(p_state_path, "r") as f:
        p_data = json.load(f)
        
    files = p_data.get("files_touched", [])
    if not files:
        print("No files touched to rollback.")
        return
        
    first_ops = {}
    for f in files:
        path = f["path"]
        if path not in first_ops:
            first_ops[path] = f["operation"]
            
    deleted_count = 0
    reverted_count = 0
    
    for path, operation in first_ops.items():
        p = Path(path)
        if operation == "created":
            if p.exists():
                try:
                    p.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting file {path}: {e}", file=sys.stderr)
        elif operation == "modified":
            try:
                subprocess.run(["git", "checkout", "HEAD", "--", path], check=True)
                reverted_count += 1
            except Exception as e:
                print(f"Error reverting file {path}: {e}", file=sys.stderr)
                
    p_data["files_touched"] = []
    p_data["last_validated_at"] = datetime.now(timezone.utc).isoformat()
    
    ok, errs = validate_against_schema(p_data, p_schema_path)
    if not ok:
        raise ValueError(f"Rollback resulted in invalid state: {errs}")
        
    _atomic_write(p_state_path, p_data)
    print(f"Rollback complete: {deleted_count} files deleted, {reverted_count} files reverted.")


# =============================================================================
# 4. SCHEMA VALIDATION
# =============================================================================

def validate_against_schema(data: dict, schema_path: Path) -> tuple[bool, list[str]]:
    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        path = " -> ".join([str(p) for p in e.path])
        return False, [f"Validation error at '{path}': {e.message}"]
    except Exception as e:
        return False, [f"Schema validation error: {str(e)}"]


def _atomic_write(path: Path, data: dict) -> None:
    temp_path = path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=4)
    temp_path.replace(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BMA State and Rollback Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--feature", required=True)
    init_parser.add_argument("--type", choices=["new_feature", "bug_fix", "refactor", "infra_change"], required=True)
    init_parser.add_argument("--plugins", nargs="+", required=True)
    
    resume_parser = subparsers.add_parser("resume")
    complete_parser = subparsers.add_parser("complete")
    
    rollback_parser = subparsers.add_parser("rollback")
    rollback_parser.add_argument("plugin_name")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_session(args.feature, args.type, args.plugins)
    elif args.command == "resume":
        res = resume_session()
        print(json.dumps(res, indent=4))
    elif args.command == "complete":
        complete_session()
    elif args.command == "rollback":
        p_root = AGENTS_ROOT / "plugins" / args.plugin_name
        p_state_path = p_root / "plugin_state.json"
        if not p_state_path.exists():
            print(f"Error: state file for {args.plugin_name} does not exist.", file=sys.stderr)
            sys.exit(1)
        with open(p_state_path, "r") as f:
            p_data = json.load(f)
        files = p_data.get("files_touched", [])
        confirm = _require_interactive_confirmation(files, p_data["feature"])
        rollback(args.plugin_name, confirm)