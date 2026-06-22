# Troubleshooting

## Tuist Cannot Find Root

Symptom:

```text
Couldn't locate the root directory ... closest directory that contains a Tuist or a .git directory
```

Fix:

- Ensure `Tuist/Package.swift` exists, or initialize Git if the user asked for Git.

## Tuist Invalid Source Globs

Symptom:

```text
invalid source files globs ... directory does not exist
```

Fix:

- Create the source directory before running `tuist generate`.
- The script writes `ProjectName/Sources/**`, tests, and resources before generation.

## iOS Simulator Destination Missing

Symptom:

```text
Unable to find a destination matching the provided destination specifier
```

Fix:

- Run `xcrun simctl list devices available`.
- Update only the destination string in `scripts/verify.sh`.

## GitHub Push Rejected For Workflow Scope

If this skill repo later adds `.github/workflows`, verify GitHub CLI auth has `workflow` scope before pushing. Without it, GitHub rejects workflow file updates.
