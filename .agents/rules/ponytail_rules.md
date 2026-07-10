# Ponytail Coding Rules — Simplicity & YAGNI

This document defines the "Ponytail" guidelines for writing clean, minimal, and YAGNI-oriented code. It is shared across both backend and frontend coder agents.

---

## 1. Core Philosophy

You write the absolute simplest, shortest, most minimal code that solves the immediate problem. 
* **The best code is the code never written.** Question if the requirement or abstraction is necessary (YAGNI).
* **Deletion over addition.** A smaller, cleaner diff is always preferred.
* **No speculative engineering.** Do not write code, models, serializers, or CSS "for later."

---

## 2. The Simplicity Ladder

Before writing any new custom code, climb this ladder and stop at the first rung that holds:

1. **Does this need to exist?** If it is speculative, skip it entirely.
2. **Already in this codebase?** Reuse existing helpers, utilities, configurations, or patterns. Inspect the surrounding directories before writing new code.
3. **Standard library does it?** Use native Python (for backend) or JavaScript/Node (for frontend) standard APIs.
4. **Native platform feature covers it?** Use database constraints over app-level checks, native `<input type="date">` over external libraries, or CSS transitions over custom JS.
5. **Already-installed dependency solves it?** Utilize existing packages in `pyproject.toml` or `package.json`. Do not introduce new packages for what a few lines of code can do.
6. **Can it be one line?** Write a clean one-liner.
7. **Only then**: Implement the minimal custom code required.

---

## 3. Strict Rules

* **No Unrequested Abstractions**: Do not create interfaces with a single implementation, factories with a single product, or configurations for static values.
* **Shortest Diffs**: The smallest working diff in the correct place wins. Always locate the root cause rather than patching symptoms.
* **Boring Over Clever**: Avoid writing "clever" code that is hard to decode at 3 AM. Prefer standard, readable patterns.
* **Shortcut Comments**: When deliberately choosing a simple, naive shortcut (e.g. O(n²) scan instead of building an index, global lock), mark it with a `ponytail:` comment naming the shortcut and the future upgrade path:
  `// ponytail: simple O(n) search, upgrade to map index if size grows`
  `# ponytail: global lock, per-tenant locks if throughput matters`
* **Test Leaving**: Leave behind **one** minimal runnable check (e.g., an assertion-based `test_*.py` or a main execution demo) for non-trivial logic. No extra frameworks unless requested.
