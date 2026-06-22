# BMAD Update Template

Only update BMAD when `_bmad` already exists. Do not create BMAD from this skill.

Update points:

- `_bmad/config.toml`: set or add `build_system = "tuist"` and source/test directories.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`: record generate/build/test/smoke/verify commands.
- `AGENTS.md`: add Tuist build and verification commands when the file exists.

Keep BMAD wording factual:

- Say that a Tuist scaffold exists only after `tuist generate --no-open` succeeds.
- Say that build/test pass only after `scripts/verify.sh` succeeds.
