
# Development Workflow Skills

[简体中文](README.zh-CN.md)

Reusable, verified development workflows extracted from real project setup work.

This repository is a place to preserve repeatable engineering workflows as skills, scripts, and references. Some skills are packaged for Codex, but the repository is not limited to Codex: the bundled scripts can also run directly in the terminal, be reused by other AI coding agents, or be integrated into team processes.

## Why Use This

Many engineering tasks are not hard once, but they are easy to repeat inconsistently:

- Project scaffolding steps drift between repos.
- Verification commands are forgotten until much later.
- Generated files accidentally get committed.
- Planning-first repositories need a clean path into runnable software.
- AI coding agents repeatedly rediscover the same setup rules.
- Small local decisions, such as test target shape or build commands, become hidden team knowledge.

This repository turns those workflows into reusable, inspectable assets. The goal is to make each workflow executable, documented, and verifiable instead of relying on memory or long prompts.

## Current Skills

### `tuist-apple-bootstrap`

Creates a minimal, verifiable Tuist project for macOS or iOS.

It generates:

- Tuist `Project.swift`
- `Tuist/Package.swift`
- App target
- SwiftUI app shell
- Swift Testing unit test target
- Optional XCTest UI launch smoke target
- `scripts/verify.sh`
- `.gitignore`
- Optional updates to existing BMAD files, only when `_bmad` already exists

It intentionally does not:

- Assume a private bundle identifier prefix
- Initialize Git or commit files
- Create BMAD from scratch
- Add codebase-memory integration
- Add third-party dependencies before the app needs them

## Direct Script Usage

Use the generator without Codex:

```bash
python3 skills/tuist-apple-bootstrap/scripts/bootstrap_tuist_apple.py \
  --project-name SampleApp \
  --platform macOS \
  --bundle-id-prefix com.example \
  --deployment-target 26.0 \
  --target-dir /path/to/repo
```

Then verify the generated project:

```bash
cd /path/to/repo
tuist generate --no-open
scripts/verify.sh
```

For iOS:

```bash
python3 skills/tuist-apple-bootstrap/scripts/bootstrap_tuist_apple.py \
  --project-name SampleApp \
  --platform iOS \
  --bundle-id-prefix com.example \
  --target-dir /path/to/repo
```

The default iOS destination is `platform=iOS Simulator,name=iPhone 16`. If that simulator is unavailable, update only the destination string in `scripts/verify.sh`.

## Codex Usage

After publishing this repository to GitHub, install a skill into Codex with the skill installer:

```bash
python3 /path/to/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/tuist-apple-bootstrap
```

Then restart Codex so it can discover the skill.

Example prompt:

```text
Use $tuist-apple-bootstrap to initialize a Tuist macOS project in this repo.
```

## GitHub Release Checks

Before publishing, run through [docs/github-release-checklist.md](docs/github-release-checklist.md).

Key checks:

- Confirm the repository remote and install examples use the same owner and repository name.
- Confirm the GitHub owner with `gh auth status`.
- Validate every skill with `quick_validate.py`.
- Smoke-test bundled scripts in temporary directories.
- Ensure no private bundle identifier prefixes or local paths are baked into templates.
- If adding GitHub Actions workflows, confirm the GitHub token has `workflow` scope before the first push.

## Development

Validate the skill:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/tuist-apple-bootstrap
```

Smoke-test the bundled generator:

```bash
tmpdir=$(mktemp -d)
python3 skills/tuist-apple-bootstrap/scripts/bootstrap_tuist_apple.py \
  --project-name SampleApp \
  --platform macOS \
  --bundle-id-prefix com.example \
  --target-dir "$tmpdir"
cd "$tmpdir"
tuist generate --no-open
scripts/verify.sh
```

## License

[MIT](LICENSE)
