"""
context_builder.py — BMA Backend Pipeline Context Assembler

Given (agent_type, stage, plugin_state), produces the fully-assembled prompt
string for a subagent by:
  1. Reading the agent template (architect.txt / coder.txt / tester.txt)
  2. Resolving every [INJECT: *] marker in it against the pointer files
     (conventions.md, constraints.md, reference.md)
  3. Extracting only the relevant sections from the actual source docs the
     pointers reference, using the project's standardized header set
  4. Substituting {{placeholder}} values from plugin_state / session_state
  5. Returning one final prompt string ready to send to the subagent

This is a LOGIC OUTLINE, not a full implementation. Function bodies are
sketched with comments. You implement the actual logic.

---

IMPORTANT — KNOWN INCONSISTENCY AT TIME OF WRITING:

The project has since standardized ALL documentation files to use this fixed
header set:

    ## Purpose
    ## Quick Start
    ## Key Concepts
    ## Configuration
    ## Testing
    ## Related Documentation

The pointer files this builder reads from (conventions.md, constraints.md,
reference.md, all under plugins/backend-plugin/context/) were written BEFORE
this standardization and still reference old, non-standard section names like
"URL Patterns", "Views", "Tenants (Public Schema)". These will NOT be found
under the new header set.

This builder does NOT silently work around that. Per the `required` field on
each pointer entry:
  - required: hard_stop      -> raise ContextExtractionError immediately
  - required: warn_and_continue -> emit the section's missing_caveat and continue

Do not add fuzzy/partial header matching to paper over this. A loud, exact
failure here is the correct signal that the pointer files need updating to
the new header set — that work is intentionally left to the project owner.

Two real exceptions to the standard header set, both confirmed by the project
owner, must be handled explicitly rather than guessed at:
  - project_root/Readme.md   -> NOT standardized. It is the top-level
                                 "Documentation Hub" — a hand-written index
                                 page linking to centralized architecture docs
                                 and distributed app READMEs. Extract by simple
                                 link-list parsing, not by the standard headers.
  - documentation/Readme.md  -> NOT using the plain header set either. It has
                                 YAML-style frontmatter (title, type, app,
                                 last_updated, tags) followed by tables, not
                                 ## Purpose / ## Quick Start sections. Extract
                                 by frontmatter + table parsing, not standard
                                 header regex.
  All other docs (documentation/*.md, backend/Readme.md, backend/apps/*/Readme.md,
  backend/tests/Readme.md, frontend/Readme.md) DO follow the standard header set.
"""

import re
import sys
from dataclasses import dataclass, field
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

# Files that do NOT follow STANDARD_HEADERS — require a different parse strategy.
NON_STANDARD_DOCS = {
    "Readme.md": "doc_hub",              # project_root/Readme.md
    "documentation/Readme.md": "doc_index",  # frontmatter + tables
}


class ContextExtractionError(Exception):
    """Raised when a hard_stop pointer entry's source/section cannot be resolved."""
    pass


@dataclass
class ExtractionResult:
    found: bool
    content: str = ""
    warning: str = ""  # populated when found=False but required=warn_and_continue


# =============================================================================
# 1. POINTER FILE PARSING
# =============================================================================

def parse_pointer_file(pointer_path: Path) -> list[dict]:
    """
    Parses one of conventions.md / constraints.md / reference.md.

    These files are markdown documents containing embedded YAML blocks
    (```yaml ... ```) under "## Source: <path>" or "## Domain: <name>" headers.
    Each block describes one extraction unit: required mode, sections to pull,
    which stages/agents it applies to, and missing_caveat text.

    Must:
      - Find every ```yaml fenced block in the file.
      - Parse each with a YAML parser (pip install pyyaml --break-system-packages).
      - Attach the preceding "## Source: ..." or "## Domain: ..." header text
        as metadata so the caller knows what file/domain this block describes.
      - Return a list of dicts, one per block, e.g.:
            {
              "source_label": "backend/Readme.md",       # from the header
              "required": "hard_stop" | "warn_and_continue",
              "sections": [...],
              "inject_for_stages": [...],
              "inject_for_agents": [...],
              "missing_caveat": "...",          # if present
              "missing_caveat_template": "...", # if present (app-readme case)
              "known_apps": [...],              # only present in conventions.md's app block
            }
      - Do NOT attempt to interpret or validate section names against
        STANDARD_HEADERS here — that happens later, in extract_section().
        This function's only job is structural parsing of the pointer file
        itself.
    """
    pass  # TODO: implement


def resolve_pointer_blocks_for_invocation(
    pointer_blocks: list[dict], agent_type: str, stage: str
) -> list[dict]:
    """
    Filters the full list of parsed pointer blocks down to only those that
    apply to this specific (agent_type, stage) combination.

    Must:
      - Keep a block if "ALL" is in inject_for_stages OR stage is in it,
        AND ("ALL" is in inject_for_agents OR agent_type is in it).
      - Preserve original order from the pointer file — this determines
        injection order in the final prompt (constraints first, by file
        convention, since constraints.md blocks are always inject_for_stages: ALL).
    """
    pass  # TODO: implement


# =============================================================================
# 2. SECTION EXTRACTION — STANDARD DOCS
# =============================================================================

def extract_section_standard(doc_path: Path, section_name: str) -> ExtractionResult:
    """
    Extracts one named section from a doc following STANDARD_HEADERS.

    Must:
      - Read doc_path. If the file does not exist at all, return
        ExtractionResult(found=False) immediately — caller decides hard_stop
        vs warn based on the pointer block's `required` field.
      - section_name must match one of STANDARD_HEADERS exactly (e.g.
        "## Key Concepts"). If the pointer file passes an old-style name like
        "URL Patterns" that does not match any STANDARD_HEADERS entry, this
        is exactly the known inconsistency described in the module docstring.
        Do NOT fuzzy-match. Return ExtractionResult(found=False) — let the
        caller raise ContextExtractionError (hard_stop) or emit the caveat
        (warn_and_continue) accordingly. The error message must explicitly
        say: "Section '<name>' is not a recognized standard header for this
        doc. This pointer file may be using a pre-standardization section
        name — check against current STANDARD_HEADERS."
      - If section_name == "All sections" (literal, case-insensitive) or
        similar wildcard convention used in reference.md / constraints.md —
        return the entire file content, all headers included.
      - Otherwise: regex-split the file content on lines matching
        r'^## .+$', find the chunk whose header line exactly equals
        section_name, return everything from that header up to (but not
        including) the next ## header or end of file.
      - If exactly one match: return ExtractionResult(found=True, content=...).
      - If the header text exists but appears more than once in the file:
        treat this as ambiguous — return found=False with a distinct error
        message ("ambiguous: header appears N times"), do not silently pick
        the first one.
    """
    pass  # TODO: implement


# =============================================================================
# 3. SECTION EXTRACTION — NON-STANDARD DOCS (the two confirmed exceptions)
# =============================================================================

def extract_from_doc_hub(doc_hub_path: Path, link_label: str) -> ExtractionResult:
    """
    Parses project_root/Readme.md ("Documentation Hub").

    This file is a hand-written index: a short intro paragraph, then grouped
    markdown links under headings like "Centralized Documentation Hub" and
    "Distributed Implementation Guides" (e.g. "- [Async Task System](...)").

    Must:
      - Parse markdown links: r'\\[([^\\]]+)\\]\\(([^)]+)\\)'.
      - `link_label` is matched against the link TEXT (e.g. "Async Task System"),
        case-insensitive, exact match preferred — only fall back to substring
        match if no exact match exists, and if substring match is itself
        ambiguous (multiple hits), return found=False with an "ambiguous" error
        rather than guessing.
      - On match, return ExtractionResult(found=True, content=<the resolved
        relative path from the link target>) — NOTE: this function returns a
        PATH, not document content. The caller is expected to then resolve
        that path and call extract_section_standard() on it (since the linked
        docs DO follow the standard header set — only the Hub itself doesn't).
      - This two-step indirection (Hub link -> path -> standard extraction)
        is intentional: the Hub is a router, not a content source.
    """
    pass  # TODO: implement


def extract_from_doc_index(doc_index_path: Path, query: dict) -> ExtractionResult:
    """
    Parses documentation/Readme.md (the "BMA Documentation Index").

    This file has YAML-style frontmatter (title, type, app, last_updated, tags)
    followed by one or more markdown tables indexing the architecture docs.

    Must:
      - Split frontmatter from body. Frontmatter convention here appears to be
        key\\tvalue pairs or a small table at the top — confirm the EXACT
        format against a real file before implementing; do not assume it's
        standard YAML `---` fenced frontmatter without checking, since the
        example given ("title  BMA Documentation Index  type  architecture...")
        reads as a rendered table, not raw YAML.
      - Parse the markdown table(s) in the body into structured rows.
      - `query` lets the caller ask either:
          {"by": "tag", "value": "async"}      -> rows matching that tag
          {"by": "title", "value": "..."}      -> exact row match
      - Return found=True with the matched row's data (likely a path to the
        actual doc) on success, found=False otherwise.
      - Same indirection principle as the Hub: this index points TO docs,
        it does not itself contain the architecture content.
    """
    pass  # TODO: implement


def get_doc_parse_strategy(doc_relative_path: str) -> str:
    """
    Returns "standard", "doc_hub", or "doc_index" for a given doc path,
    using NON_STANDARD_DOCS as the lookup, defaulting to "standard".

    Must:
      - Normalize path separators before lookup so this works regardless of
        how the pointer file wrote the path (e.g. "Readme.md" vs "./Readme.md").
    """
    pass  # TODO: implement


# =============================================================================
# 4. APP-README RESOLUTION (the dynamic <app_name> case from conventions.md)
# =============================================================================

def resolve_app_readme_sections(
    app_names: list[str], known_apps_block: dict, sections: list[str]
) -> dict[str, ExtractionResult]:
    """
    Handles conventions.md's "Source: backend/apps/<app_name>/Readme.md" block,
    which is dynamic per-feature. app_names should be passed by the caller as
    plugin_state["apps_touched"] (structured field, populated by the
    orchestrator at architecture-stage completion — see plugin_state.schema.json
    and checkpoint.advance_stage()). Not scraped from architect_notes free text.

    Must:
      - For each app_name in app_names:
          - Check known_apps_block["known_apps"] for a matching entry's
            readme_present flag FIRST (cheap shortcut, per conventions.md's
            own documented intent) before touching the filesystem.
          - If readme_present is False (or app not in known_apps_block at all,
            meaning it's not yet registered) -> immediately build the
            missing_caveat_template with app_name substituted in, return
            ExtractionResult(found=False, warning=<formatted caveat>).
          - If readme_present is True -> actually read
            backend/apps/<app_name>/Readme.md and run extract_section_standard()
            for each requested section, since app Readmes follow the standard
            header set per the project's stated standardization.
      - Return a dict keyed by app_name so the caller can report per-app
        results distinctly (one app's Readme might be present, another's not,
        in the same invocation).
    """
    pass  # TODO: implement


# =============================================================================
# 5. AGENT TEMPLATE RESOLUTION
# =============================================================================

def load_agent_template(agent_type: str) -> str:
    """
    Reads architect.txt / coder.txt / tester.txt from AGENTS_DIR.
    Must raise a clear error if agent_type is not one of the three known values
    — do not guess a filename.
    """
    pass  # TODO: implement


def find_inject_markers(template_text: str) -> list[dict]:
    """
    Finds every [INJECT: *] marker in the template.

    Must:
      - Match patterns like:
            [INJECT: constraints]
            [INJECT: conventions]
            [INJECT: reference:{{domains}}]
            [INJECT: retry_errors]
      - For markers containing a {{placeholder}} (like reference's domains),
        keep the placeholder unresolved at this stage — return it as part of
        the marker's raw spec; substitution happens after domains are known
        from plugin_state (see assemble_prompt below). Order of operations
        matters: you cannot resolve "reference:{{domains}}" until you've
        already read plugin_state.architect_notes for the domain list.
      - Return list of {"raw_marker": "[INJECT: constraints]", "kind": "constraints",
        "param": None} style dicts, one per occurrence, preserving position
        in the text so substitution can happen via exact string replace.
    """
    pass  # TODO: implement


# =============================================================================
# 6. TOP-LEVEL ASSEMBLY
# =============================================================================

def build_context(agent_type: str, stage: str, plugin_state: dict, retry_errors: str | None = None) -> str:
    """
    The single public entrypoint. Produces the final prompt string.

    Must, in order:
      1. Load the agent template for agent_type.
      2. Find all [INJECT: *] markers in it.
      3. For the "constraints" marker: parse constraints.md, resolve blocks
         for (agent_type, stage) — though per its own pointer config this is
         always ALL/ALL — extract each block's full content (constraints.md
         blocks use "All sections" wildcard, not named sections), concatenate,
         substitute into the marker position.
      4. For the "conventions" marker: parse conventions.md, resolve blocks
         for (agent_type, stage), extract each named section via
         extract_section_standard() (or resolve_app_readme_sections() for the
         dynamic app-readme block), concatenate with clear
         "=== CONVENTIONS: <source> § <section> ===" headers per the agent
         template's own documented injection format, substitute.
      5. For the "reference:{{domains}}" marker: read
         plugin_state["domains_touched"] (a structured array field — see
         plugin_state.schema.json — populated by the orchestrator via
         checkpoint.advance_stage() at architecture-stage completion, sourced
         from pre_coder.py's parsed_domains_touched). Do NOT regex-scrape
         architect_notes free text for this — that was the original gap,
         now resolved by the schema patch. Parse reference.md, resolve only
         matching domain blocks, extract, substitute. If domains_touched is
         empty (e.g. called before architecture stage has completed, which
         should not happen in correct orchestrator usage), treat this as a
         caller error and raise rather than silently injecting nothing.
      6. For the "retry_errors" marker: if retry_errors is not None, substitute
         it formatted as the hook's error JSON pretty-printed under a
         "=== RETRY: Previous attempt failed ===" header. If None (first
         attempt, not a retry), substitute an empty string — remove the
         marker cleanly, don't leave a dangling label with nothing under it.
      7. Substitute all {{placeholder}} values (feature, feature_type,
         completed_stages, pending_stages, architect_notes, current_stage,
         context) from plugin_state / session_state as documented in
         orchestrator.md § 7 Placeholder Contract.
      8. Return the fully assembled string.

    Must NOT:
      - Cache anything across calls (per the no-caching decision — every call
        re-reads from disk).
      - Silently swallow a hard_stop ContextExtractionError — let it propagate
        to the orchestrator, which surfaces it as a prerequisite gap per
        orchestrator.md § 4.
    """
    pass  # TODO: implement


# =============================================================================
# CLI ENTRYPOINT (for manual testing / debugging during development)
# =============================================================================

if __name__ == "__main__":
    # Sketch only — implement actual argparse at build time.
    #
    # Usage during development:
    #   python context_builder.py --agent architect --stage architecture \
    #       --plugin-state .agents/plugins/backend-plugin/plugin_state.json
    #
    # Should print the assembled prompt to stdout so you can visually inspect
    # exactly what a subagent would receive, BEFORE wiring this into the
    # orchestrator. This is your primary debugging tool for catching stale
    # pointer-file section names (the known inconsistency above) before they
    # cause a runtime ContextExtractionError mid-pipeline.
    pass  # TODO: implement