# Backend Plugin — Conventions Context

This file is read by `context_builder.py` at runtime. It defines WHAT to extract,
FROM WHERE, and WHEN to inject it into a subagent prompt.

`context_builder.py` must:
1. Read each source pointer below.
2. Extract only the listed sections (never the full file).
3. Inject extracted content under a clearly labelled header in the subagent prompt.
4. If a source file is missing, inject a CONTEXT WARNING instead of the section.
   Never silently skip. Never hard-stop unless marked `required: hard_stop`.

---

## Source: `backend/Readme.md`

```yaml
required: hard_stop
reason: >
  This is the primary backend convention source. If it is missing, the agent
  has no grounding for any backend work. Do not proceed without it.
sections:
  - "Purpose"
  - "Key Concepts"
  - "Testing"
inject_for_stages:
  - architecture
  - dependency_setup
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
```

---

## Source: `backend/tests/Readme.md`

```yaml
required: warn_and_continue
missing_caveat: >
  backend/tests/Readme.md is missing. Testing conventions are unknown.
  Follow Django/DRF standard testing patterns strictly. Do not invent
  project-specific test structures. Flag this gap in architect_notes.
sections:
  - "Purpose"
  - "Quick Start"
  - "Key Concepts"
  - "Testing Conventions"
  - "Configuration"
  - "Testing"
  - "Related Documentation"
inject_for_stages:
  - happy_path_tests
  - full_implementation_tests
inject_for_agents:
  - tester
```

---

## Source: `backend/apps/<app_name>/Readme.md`

```yaml
required: warn_and_continue
resolution: >
  context_builder.py must resolve <app_name> dynamically from the list of
  apps the Coder or Tester subagent declares it will touch. This list comes
  from plugin_state.json → architect_notes (the Architect must declare
  affected apps explicitly).
missing_caveat_template: >
  [CONTEXT WARNING] backend/apps/{app_name}/Readme.md is missing.
  Conventions for this app are unknown. Do not make assumptions about its
  internal structure. Stick strictly to project-wide conventions from
  backend/Readme.md until this file exists.
sections:
  - "Purpose"
  - "Quick Start"
  - "Key Concepts"
  - "API Reference"
  - "Configuration"
  - "Testing"
  - "Related Documentation"
inject_for_stages:
  - happy_path
  - happy_path_tests
  - full_implementation
  - full_implementation_tests
inject_for_agents:
  - coder
  - tester
known_apps:
  - name: customer_management
    readme_present: false
  - name: notifications
    readme_present: true
  - name: payments_management
    readme_present: false
  - name: services
    readme_present: true
  - name: setup
    readme_present: false
  - name: tasks
    readme_present: true
  - name: tenants
    readme_present: false
```

> NOTE: `readme_present` is a hint for `context_builder.py` to skip the filesystem
> check and immediately emit the caveat for known-missing Readmes. Update this list
> as Readmes are added. When `readme_present` becomes `true`, remove the entry or
> flip the flag — context_builder.py will then read the actual file.

---

## Source: `docs/architecture/data-models.md`

```yaml
required: warn_and_continue
missing_caveat: >
  docs/architecture/data-models.md is missing. Data model conventions are unknown.
  Do not introduce new models or fields without user confirmation.
sections:
  - All sections (this file is already concise — inject in full)
inject_for_stages:
  - architecture
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
```

---

## Injection Format

`context_builder.py` must wrap each injected block in a labelled section so the
subagent knows what it is reading:

```
=== CONVENTIONS: backend/Readme.md § "URL Patterns" ===
<extracted content here>
=== END CONVENTIONS ===
```

For warnings:
```
=== CONTEXT WARNING: backend/apps/customer_management/Readme.md ===
Conventions for this app are unknown. Do not make assumptions about its
internal structure. Stick strictly to project-wide conventions from
backend/Readme.md until this file exists.
=== END WARNING ===
```
