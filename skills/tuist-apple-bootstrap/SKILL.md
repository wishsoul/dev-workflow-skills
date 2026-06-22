---
name: tuist-apple-bootstrap
description: Bootstrap Apple platform app projects with Tuist. Use when the user asks to initialize, scaffold, or recreate a Tuist-based iOS or macOS Xcode project, especially from an empty PRD/BMAD repository, and wants a generated app target, tests, verify script, .gitignore, and optional BMAD status updates.
---

# Tuist Apple Bootstrap

Use this skill to create a minimal, verifiable Tuist project for iOS or macOS without hand-rewriting the Xcode scaffold.

## Defaults

- Ask for `project_name`, `platform` (`macOS` or `iOS`), and `bundle_id_prefix`; do not assume a private bundle prefix.
- Default deployment target to `26.0`, mapped to `.macOS("26.0")` or `.iOS("26.0")`.
- Default unit tests to Swift Testing.
- Default UI launch smoke tests to XCTest.
- Default iOS destination to iPhone only.
- Do not initialize Git or commit unless the user explicitly asks.
- Do not add codebase-memory files or run indexing unless the user explicitly asks.
- If `_bmad` exists, update BMAD config/status; if it does not exist, do not create BMAD.

## Workflow

1. Preflight the target directory:
   - Run `pwd`, `git status --short` if Git exists, `tuist version`, and `xcodebuild -version`.
   - If `Project.swift` already exists, inspect it before overwriting. Ask before replacing a real project.
2. Collect missing required inputs:
   - `project_name`
   - `platform`
   - `bundle_id_prefix`
3. Generate files with `scripts/bootstrap_tuist_apple.py`.
4. Run verification:
   - `tuist generate --no-open`
   - `scripts/verify.sh`
5. If `_bmad` exists, confirm BMAD status now points to the real generate/build/test/smoke commands.
6. Report exact commands run and any local warnings.

## Script Usage

Use the bundled script from the skill directory:

```bash
python3 <skill>/scripts/bootstrap_tuist_apple.py \
  --project-name PastePop \
  --platform macOS \
  --bundle-id-prefix com.example \
  --deployment-target 26.0 \
  --target-dir /path/to/repo
```

Useful options:

- `--platform macOS` or `--platform iOS`
- `--no-ui-tests` to skip the UI launch smoke target
- `--update-bmad auto` to update existing BMAD files only when present
- `--update-bmad never` to skip BMAD updates
- `--dry-run` to print planned files without writing
- `--force` to overwrite generated scaffold files

## Generated Shape

For `ProjectName`, generate:

```text
Project.swift
Tuist/Package.swift
ProjectName/Sources/ProjectNameApp.swift
ProjectName/Sources/ContentView.swift
ProjectName/Sources/ProductIdentity.swift
ProjectName/Resources/Assets.xcassets/Contents.json
ProjectNameTests/ProductIdentityTests.swift
ProjectNameUITests/ProjectNameLaunchTests.swift
scripts/verify.sh
.gitignore
```

If UI tests are disabled, omit `ProjectNameUITests`.

## Verification Rules

Do not claim the scaffold is ready until verification has run in the target repository and passed.

The default `scripts/verify.sh` must run:

```bash
tuist generate --no-open
xcodebuild build -scheme <ProjectName> -destination '<destination>'
xcodebuild test -scheme <ProjectName> -only-testing:<ProjectName>Tests -destination '<destination>'
xcodebuild test -scheme <ProjectName> -only-testing:<ProjectName>UITests -destination '<destination>'
```

For `macOS`, use `platform=macOS`.

For `iOS`, use `platform=iOS Simulator,name=iPhone 16`.

If the requested simulator is unavailable, inspect `xcrun simctl list devices available` and update only the destination string, not the project structure.

## References

- Read `references/troubleshooting.md` when Tuist or Xcode generation/build/test fails.
- Read `references/bmad-update-template.md` when `_bmad` exists and BMAD files need manual adjustment.
- Read `references/project-swift-template.md` only if the script needs to be patched or a user asks to see the generated template.
