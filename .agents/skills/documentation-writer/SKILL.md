---
name: documentation-writer
description: "Add, modify and/or review documentation or scaffold of documentation written by user. Use when requested to add documentation, or when implementing new features that require documentation."
---

## When to Use

Invoke this skill when:

1. **Explicit request**: User asks to "document X", "write documentation for X", "write documentation".
2. **Code changes**: While doing code fix, code refactor or mere code change, also update the documentation of the code.

## Documentation flow

- If user provides a documentation file, and has already scaffolded the documentation use `Scaffold flow`, if the user asks for a new documentation use `New Documentation flow`.
- Create a markdown file for documentation.
- Add code and other documentation references wherever required.

### Scaffold flow

When the user provides an existing documentation file with scaffolded sections:

1. **Review the scaffold**: Analyze the existing structure, headings, and placeholder content.
2. **Fill in sections**: Expand each section with comprehensive, accurate content, emphasize the sections where you can find bookmarks like `_AGENT: .._`
3. **Preserve structure**: Maintain the original organization, tone, and formatting style.
4. **Validate completeness**: Ensure no placeholder text remains (no "TODO", "TBD", or empty sections).
5. **Add cross-references**: Link to related docs, API references, or code files where appropriate.
6. **Review with user**: Present the completed documentation for approval.

### New Documentation flow

When no existing documentation file exists and the user requests new documentation:

1. **Gather context**:
   - Review the codebase, feature, or topic to document.
   - Identify the audience (developers, end-users, API consumers, etc.).
   - Determine the documentation type (API docs, README, user guide, architecture doc, etc.).
2. **Propose structure**: Create a scaffold with logical sections based on the documentation type:
   - **README**: Overview, Installation, Usage, Configuration, Contributing, License
   - **API Docs**: Endpoint, Method, Parameters, Request/Response Examples, Error Codes
   - **Architecture Doc**: System Overview, Components, Data Flow, Dependencies, Diagrams
   - **User Guide**: Getting Started, Features, FAQs, Troubleshooting
3. **Get user approval**: Present the proposed scaffold structure and get confirmation before writing.
4. **Write documentation**: Fill in each section with detailed, accurate content.
5. **Add examples**: Include code snippets, usage examples, or diagrams where helpful.
6. **Review and finalize**: Check for completeness, accuracy, and clarity. Present the final doc for review.

## Validation Step

- After the documentation is completed, check if the documenration is healthy using `doc_health_check` script of this skill.
- Re-validate the document aligns to what is implemented and dsigned in code.