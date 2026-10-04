# DOX Framework

- DOX is the AGENTS.md instruction hierarchy for this repository.
- Agents must follow the applicable DOX chain before making edits.

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees.
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it.

## Read Before Editing

1. Read the root AGENTS.md.
2. Identify every file or folder you expect to touch.
3. Walk from the repository root to each target path.
4. Read every AGENTS.md found along each route.
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there.
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules.
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX.

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index.
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index.
- Each parent explains what its direct children cover and what stays owned by the parent.
- The closer a doc is to the work, the more specific and practical it must be.

## Child Doc Shape

- Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards.
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty.
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists.

Default section order:
- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

## Style

- Keep docs concise, current, and operational.
- Document stable contracts, not diary entries.
- Put broad rules in parent docs and concrete details in child docs.
- Prefer direct bullets with explicit names.
- Do not duplicate rules across many files unless each scope needs a local version.
- Delete stale notes instead of explaining history.
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist.

## Work Guidance

- Prefer Bash or the repository-documented shell on WSL/Linux projects; use PowerShell only when the project requires it or it is the practical path for Windows-specific work.
- If required tools, credentials, host details, or source material are missing, explain the gap and ask the user instead of guessing.
- Keep behavior configurable where configuration adds practical value without unnecessary complexity.
- Follow functional requirements and user-facing behavior documented in README.md unless a closer instruction overrides it.
- For UI-facing work, propose interface improvements when they are necessary to satisfy the documented requirements or materially improve usability.

## Closeout

1. Re-check changed paths against the DOX chain.
2. Update nearest owning docs and any affected parents or children.
3. Refresh every affected Child DOX Index.
4. Remove stale or contradictory text.
5. Run existing verification when relevant.
6. Report any docs intentionally left unchanged and why.

## User Preferences

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md.

## Coding Standards

- Source files should include a module-level comment or docstring describing the file purpose where prudent.
- Functions should include concise purpose/input/output comments or docstrings when they are not self-explanatory.
- Python: use type hints where practical, clear naming, and avoid unnecessary abstraction.
- TypeScript: prefer strict typing, avoid `any` unless unavoidable, and keep component logic readable.
- YAML: prefer modern Home Assistant syntax, use native `note:` fields where supported, and keep automations readable.

## Releases

- Every meaningful released change should have release notes and a version number.
- Use `.github/RELEASE_NOTES_TEMPLATE.md` as the release-notes template when the project has no more specific release process.
- Tag releases when the project release workflow calls for tags.

## Child DOX Index

- No child `AGENTS.md` files currently exist.
- This root contract owns the entire repository, including project documentation, versioned release notes, and the release-note template under `.github/`.
- Add a child `AGENTS.md` only when a durable source, test, documentation, or tooling boundary gains its own local contracts.
