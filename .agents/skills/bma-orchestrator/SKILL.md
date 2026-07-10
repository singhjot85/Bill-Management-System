---
name: bma-orchestrator
description: "Run the BMA Orchestrator pipeline to coordinate feature development (architecture, coding, testing, and validation) for the Bill Management Application."
---

## When to Use

Invoke this skill when the user requests to:
1. "Run the orchestrator" or "start the BMA pipeline".
2. "Build a new feature X" or "implement Y" under the custom plugin pipeline.
3. "Resume the pipeline" or "check current pipeline status".

## Instructions for the Agent

You will act as the **BMA Orchestrator** to run and coordinate the agentic pipeline for the Bill Management Application (BMA).

### Step 1: Read the Orchestrator Instructions
Locate and read the full runtime instructions in [.agents/orchestrator.md](../../orchestrator.md). You must adhere strictly to the boundaries, state machine transition rules, and hook validation contracts specified in that document.

### Step 2: Orient Yourself and Read State
1. Read the global session state in [.agents/session_state.json](../../session_state.json).
2. If a plugin is active, read its corresponding `plugin_state.json` file (e.g., [.agents/plugins/backend-plugin/plugin_state.json](../../plugins/backend-plugin/plugin_state.json)).
3. Determine whether you are starting a new pipeline or resuming an existing one.

### Step 3: Present the Confirmation Prompt
Before running any hooks or spawning subagents, output the confirmation prompt to the user exactly as specified in Section 9 of the Orchestrator manual:
```text
Starting: <feature_name>
Plugin(s): <list>
Pipeline: <stage_list>
Proceed? [yes / no]
```
Wait for user confirmation before proceeding.

### Step 4: Execute the Pipeline
Follow the Stage Execution Rules in the manual:
1. Load subagent system prompts from `.agents/plugins/<plugin>/agents/` (e.g., `architect.txt`, `coder.txt`, `tester.txt`).
2. Interpolate standard placeholders (`{{feature}}`, `{{context}}`, etc.) using context built by the custom script `context_builder.py`.
3. Spawn subagents using the `invoke_subagent` tool.
4. Run validation hooks (e.g., `pre_coder.py`, `pre_tester.py`, `pre_commit.py`) via the `run_command` tool.
5. Parse the exit codes and structured JSON output from the hooks to handle successes, retryable failures, or non-retryable routing.
