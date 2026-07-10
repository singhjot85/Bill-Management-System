"""
context_builder.py — BMA Backend Pipeline Context Assembler
"""

import re
import argparse
import json
import sys
import yaml
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(".")
CONTEXT_DIR = Path(".agents/plugins/backend-plugin/context")
AGENTS_DIR = Path(".agents/plugins/backend-plugin/agents")

STANDARD_HEADERS = [
    "## Purpose",
    "## Quick Start",
    "## Key Concepts",
    "## Configuration",
    "## Testing",
    "## Related Documentation",
]

NON_STANDARD_DOCS = {
    "Readme.md": "doc_hub",
    "README.md": "doc_hub",
    "docs/README.md": "doc_index",
    "docs/Readme.md": "doc_index",
    "documentation/Readme.md": "doc_index",
}


class ContextExtractionError(Exception):
    """Raised when a hard_stop pointer entry's source/section cannot be resolved."""
    pass


@dataclass
class ExtractionResult:
    found: bool
    content: str = ""
    warning: str = ""


# =============================================================================
# 1. POINTER FILE PARSING
# =============================================================================

def parse_pointer_file(pointer_path: Path) -> list[dict]:
    if not pointer_path.exists():
        return []
    with open(pointer_path, "r") as f:
        content = f.read()
        
    pattern = r'##\s+(Source|Domain):\s*`?([^`\n]+)`?\s*\n(.*?)(?=##\s+(Source|Domain):|$)'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    blocks = []
    for m in matches:
        kind = m.group(1).lower()
        label = m.group(2).strip()
        body = m.group(3)
        
        yaml_match = re.search(r'```yaml\s*\n(.*?)\n```', body, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            try:
                data = yaml.safe_load(yaml_content)
                if not isinstance(data, dict):
                    data = {}
                data["source_label"] = label
                data["kind"] = kind
                blocks.append(data)
            except Exception as e:
                print(f"Error parsing YAML in {pointer_path}: {e}", file=sys.stderr)
    return blocks


def resolve_pointer_blocks_for_invocation(
    pointer_blocks: list[dict], agent_type: str, stage: str
) -> list[dict]:
    filtered = []
    for block in pointer_blocks:
        stages = block.get("inject_for_stages", [])
        agents = block.get("inject_for_agents", [])
        
        stage_ok = False
        if isinstance(stages, list):
            if "ALL" in stages or "all" in stages or stage in stages:
                stage_ok = True
        elif isinstance(stages, str):
            if stages.upper() == "ALL" or stages == stage:
                stage_ok = True
                
        agent_ok = False
        if isinstance(agents, list):
            if "ALL" in agents or "all" in agents or agent_type in agents:
                agent_ok = True
        elif isinstance(agents, str):
            if agents.upper() == "ALL" or agents == agent_type:
                agent_ok = True
                
        if stage_ok and agent_ok:
            filtered.append(block)
    return filtered


# =============================================================================
# 2. SECTION EXTRACTION — STANDARD DOCS
# =============================================================================

def extract_section_standard(doc_path: Path, section_name: str, required: str, missing_caveat: str = "") -> ExtractionResult:
    if not doc_path.exists():
        if required == "hard_stop":
            raise ContextExtractionError(f"Required file {doc_path} is missing.")
        else:
            return ExtractionResult(found=False, warning=missing_caveat)
            
    with open(doc_path, "r") as f:
        content = f.read()
        
    if section_name.lower() == "all sections":
        return ExtractionResult(found=True, content=content)
        
    header_to_look_for = section_name
    if not header_to_look_for.startswith("##"):
        header_to_look_for = f"## {section_name}"
        
    if header_to_look_for not in STANDARD_HEADERS:
        msg = f"Section '{section_name}' is not a recognized standard header for this doc. This pointer file may be using a pre-standardization section name — check against current STANDARD_HEADERS."
        if required == "hard_stop":
            raise ContextExtractionError(msg)
        else:
            return ExtractionResult(found=False, warning=missing_caveat if missing_caveat else msg)
            
    lines = content.splitlines()
    header_indices = []
    for idx, line in enumerate(lines):
        if line.startswith("## ") or line.startswith("##\t"):
            h_name = line[3:].strip()
            if h_name.lower() == section_name.lower():
                header_indices.append(idx)
                
    if len(header_indices) == 0:
        msg = f"Header '{section_name}' not found in {doc_path}."
        if required == "hard_stop":
            raise ContextExtractionError(msg)
        else:
            return ExtractionResult(found=False, warning=missing_caveat if missing_caveat else msg)
    elif len(header_indices) > 1:
        msg = f"ambiguous: header '{section_name}' appears {len(header_indices)} times in {doc_path}."
        if required == "hard_stop":
            raise ContextExtractionError(msg)
        else:
            return ExtractionResult(found=False, warning=msg)
            
    start_idx = header_indices[0]
    end_idx = len(lines)
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].startswith("## ") or lines[idx].startswith("##\t") or lines[idx].startswith("# "):
            end_idx = idx
            break
            
    section_content = "\n".join(lines[start_idx:end_idx]).strip()
    return ExtractionResult(found=True, content=section_content)


# =============================================================================
# 3. SECTION EXTRACTION — NON-STANDARD DOCS
# =============================================================================

def extract_from_doc_hub(doc_hub_path: Path, link_label: str) -> ExtractionResult:
    if not doc_hub_path.exists():
        return ExtractionResult(found=False, warning="project_root/Readme.md is missing.")
    with open(doc_hub_path, "r") as f:
        content = f.read()
        
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    exact_matches = []
    substring_matches = []
    
    for text, path in matches:
        text_clean = text.strip().lower()
        label_clean = link_label.strip().lower()
        if text_clean == label_clean:
            exact_matches.append((text, path))
        elif label_clean in text_clean:
            substring_matches.append((text, path))
            
    if exact_matches:
        if len(exact_matches) > 1:
            return ExtractionResult(found=False, warning=f"ambiguous: multiple exact matches for link label '{link_label}'")
        return ExtractionResult(found=True, content=exact_matches[0][1])
    elif substring_matches:
        if len(substring_matches) > 1:
            return ExtractionResult(found=False, warning=f"ambiguous: multiple substring matches for link label '{link_label}'")
        return ExtractionResult(found=True, content=substring_matches[0][1])
    else:
        return ExtractionResult(found=False, warning=f"Link label '{link_label}' not found in Documentation Hub.")


def extract_from_doc_index(doc_index_path: Path, query: dict) -> ExtractionResult:
    if not doc_index_path.exists():
        return ExtractionResult(found=False, warning=f"{doc_index_path} not found")
        
    with open(doc_index_path, "r") as f:
        content = f.read()
        
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            for line in fm_text.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if v.startswith("[") and v.endswith("]"):
                        v = [x.strip() for x in v[1:-1].split(",")]
                    frontmatter[k] = v
                    
    link_pattern = r'\[\s*\**([^*\]]+)\**\s*\]\(([^)]+)\)'
    links = re.findall(link_pattern, body)
    
    by = query.get("by")
    val = query.get("value", "").lower().strip()
    
    if by == "tag":
        tags = frontmatter.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        tags = [t.lower() for t in tags]
        if val in tags:
            return ExtractionResult(found=True, content=str(doc_index_path))
        else:
            return ExtractionResult(found=False, warning=f"Tag '{val}' not found in frontmatter")
    elif by == "title":
        for title, path in links:
            if title.strip().lower() == val:
                resolved_path = Path("docs") / path.lstrip("./")
                return ExtractionResult(found=True, content=str(resolved_path))
        return ExtractionResult(found=False, warning=f"Title '{val}' not found in documentation index")
    else:
        return ExtractionResult(found=False, warning=f"Unknown query by type '{by}'")


def get_doc_parse_strategy(doc_relative_path: str) -> str:
    norm_path = doc_relative_path.replace("\\", "/").lstrip("./")
    if norm_path in ["Readme.md", "README.md"]:
        return "doc_hub"
    elif norm_path in ["docs/README.md", "docs/Readme.md", "documentation/Readme.md"]:
        return "doc_index"
    else:
        return "standard"


# =============================================================================
# 4. APP-README RESOLUTION
# =============================================================================

def resolve_app_readme_sections(
    app_names: list[str], known_apps_block: dict, sections: list[str]
) -> dict[str, ExtractionResult]:
    results = {}
    known_apps = known_apps_block.get("known_apps", [])
    known_dict = {app["name"]: app.get("readme_present", False) for app in known_apps}
    
    missing_template = known_apps_block.get("missing_caveat_template", "")
    if not missing_template:
        missing_template = "[CONTEXT WARNING] backend/apps/{app_name}/Readme.md is missing."
        
    for app in app_names:
        present = known_dict.get(app, False)
        if not present:
            warning = missing_template.format(app_name=app)
            results[app] = ExtractionResult(found=False, warning=warning)
        else:
            doc_path = PROJECT_ROOT / f"backend/apps/{app}/Readme.md"
            app_contents = []
            for sec in sections:
                res = extract_section_standard(doc_path, sec, "warn_and_continue", missing_caveat=f"Section {sec} in {app} Readme missing")
                if res.found:
                    app_contents.append(res.content)
                else:
                    app_contents.append(res.warning)
            results[app] = ExtractionResult(found=True, content="\n\n".join(app_contents))
    return results


# =============================================================================
# 5. AGENT TEMPLATE RESOLUTION
# =============================================================================

def load_agent_template(agent_type: str) -> str:
    filename = f"{agent_type}.txt"
    filepath = AGENTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Agent prompt template '{filepath}' does not exist.")
    with open(filepath, "r") as f:
        return f.read()


def find_inject_markers(template_text: str) -> list[dict]:
    pattern = r'\[INJECT:\s*([^\]]+)\]'
    matches = re.finditer(pattern, template_text)
    results = []
    for m in matches:
        raw = m.group(0)
        spec = m.group(1).strip()
        kind = spec
        param = None
        if ":" in spec:
            kind, param = spec.split(":", 1)
            kind = kind.strip()
            param = param.strip()
        results.append({
            "raw_marker": raw,
            "kind": kind,
            "param": param
        })
    return results


# =============================================================================
# 6. TOP-LEVEL ASSEMBLY
# =============================================================================

def build_context(agent_type: str, stage: str, plugin_state: dict, retry_errors: str | None = None) -> str:
    template = load_agent_template(agent_type)
    markers = find_inject_markers(template)
    
    prompt = template
    
    for m in markers:
        raw = m["raw_marker"]
        kind = m["kind"]
        param = m["param"]
        
        replacement = ""
        
        if kind == "constraints":
            c_blocks = parse_pointer_file(CONTEXT_DIR / "constraints.md")
            filtered = resolve_pointer_blocks_for_invocation(c_blocks, agent_type, stage)
            content_pieces = []
            for b in filtered:
                # constraints are wildcards, read the file in full
                path = PROJECT_ROOT / b["source_label"]
                if path.exists():
                    with open(path, "r") as f:
                        content_pieces.append(f.read())
            if content_pieces:
                replacement = "=== CONSTRAINTS: Non-negotiable project boundaries ===\n" + "\n\n".join(content_pieces) + "\n=== END CONSTRAINTS ==="
                
        elif kind == "conventions":
            cv_blocks = parse_pointer_file(CONTEXT_DIR / "conventions.md")
            filtered = resolve_pointer_blocks_for_invocation(cv_blocks, agent_type, stage)
            content_pieces = []
            for b in filtered:
                label = b["source_label"]
                if "<app_name>" in label:
                    apps = plugin_state.get("apps_touched", [])
                    res = resolve_app_readme_sections(apps, b, b["sections"])
                    for app, val in res.items():
                        if val.found:
                            content_pieces.append(f"=== CONVENTIONS: backend/apps/{app}/Readme.md ===\n{val.content}\n=== END CONVENTIONS ===")
                        else:
                            content_pieces.append(f"=== CONTEXT WARNING: backend/apps/{app}/Readme.md ===\n{val.warning}\n=== END WARNING ===")
                else:
                    doc_path = PROJECT_ROOT / label
                    for sec in b["sections"]:
                        res = extract_section_standard(doc_path, sec, b.get("required", "warn_and_continue"), b.get("missing_caveat", ""))
                        if res.found:
                            content_pieces.append(f"=== CONVENTIONS: {label} § \"{sec}\" ===\n{res.content}\n=== END CONVENTIONS ===")
                        else:
                            content_pieces.append(f"=== CONTEXT WARNING: {label} § \"{sec}\" ===\n{res.warning}\n=== END WARNING ===")
            replacement = "\n\n".join(content_pieces)
            
        elif kind == "reference":
            # param could be {{domains}}
            domains = plugin_state.get("domains_touched", [])
            # if architecture stage, domains_touched is empty, reference.md says inject ALL
            ref_blocks = parse_pointer_file(CONTEXT_DIR / "reference.md")
            filtered = resolve_pointer_blocks_for_invocation(ref_blocks, agent_type, stage)
            content_pieces = []
            for b in filtered:
                domain_name = b["source_label"]
                if not domains or domain_name in domains:
                    for src in b.get("sources", []):
                        file_path = PROJECT_ROOT / src["file"]
                        sections_list = src.get("sections", ["All sections"])
                        for sec in sections_list:
                            res = extract_section_standard(file_path, sec, src.get("required", "warn_and_continue"), src.get("missing_caveat", ""))
                            if res.found:
                                content_pieces.append(f"=== REFERENCE: {domain_name} ===\n{res.content}\n=== END REFERENCE ===")
                            else:
                                content_pieces.append(f"=== REFERENCE WARNING: {domain_name} ===\n{res.warning}\n=== END REFERENCE ===")
            replacement = "\n\n".join(content_pieces)
            
        elif kind == "retry_errors":
            if retry_errors:
                replacement = f"=== RETRY: Previous attempt failed ===\n{retry_errors}\n=== END RETRY ==="
            else:
                replacement = ""
                
        prompt = prompt.replace(raw, replacement)
        
    # substitute placeholders
    prompt = prompt.replace("{{feature}}", plugin_state.get("feature", ""))
    prompt = prompt.replace("{{feature_type}}", plugin_state.get("feature_type", ""))
    prompt = prompt.replace("{{completed_stages}}", str(plugin_state.get("completed_stages", [])))
    prompt = prompt.replace("{{pending_stages}}", str(plugin_state.get("pending_stages", [])))
    prompt = prompt.replace("{{architect_notes}}", plugin_state.get("architect_notes", ""))
    prompt = prompt.replace("{{current_stage}}", plugin_state.get("current_stage", ""))
    prompt = prompt.replace("{{context}}", "") # default empty context placeholder if not handled
    
    return prompt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Context Builder")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--plugin-state", required=True)
    
    args = parser.parse_args()
    
    with open(args.plugin_state, "r") as f:
        p_state = json.load(f)
        
    res = build_context(args.agent, args.stage, p_state)
    print(res)