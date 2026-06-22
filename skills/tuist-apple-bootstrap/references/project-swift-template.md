# Project.swift Template Notes

The bootstrap script generates a single Tuist `Project.swift` with:

- One app target.
- One Swift Testing unit test target.
- Optional XCTest UI test target.
- One shared scheme named after the project.
- No external dependencies.

Platform mapping:

| Input | Destination | Deployment target |
| --- | --- | --- |
| `macOS` | `.mac` | `.macOS("26.0")` by default |
| `iOS` | `.iPhone` | `.iOS("26.0")` by default |

Do not commit generated `.xcodeproj`, `.xcworkspace`, or `Derived/` output.
