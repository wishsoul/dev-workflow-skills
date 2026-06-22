#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def swift_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "", value)
    if not cleaned:
        raise SystemExit("project name must contain at least one alphanumeric character")
    if cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned


def write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"refusing to overwrite existing file: {path}")
    if dry_run:
        print(f"would write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def append_unique(path: Path, content: str, *, dry_run: bool) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    additions = []
    for line in content.splitlines():
        if line and line not in existing:
            additions.append(line)
    if not additions:
        return
    if dry_run:
        print(f"would append {path}: {', '.join(additions)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = "" if not existing else ("\n" if existing.endswith("\n") else "\n\n")
    path.write_text(existing + prefix + "\n".join(additions) + "\n", encoding="utf-8")


def project_swift(args: argparse.Namespace, name: str) -> str:
    platform = ".mac" if args.platform == "macOS" else ".iPhone"
    deployment = ".macOS" if args.platform == "macOS" else ".iOS"
    ui_target = ""
    ui_scheme = ""
    if args.ui_tests:
        ui_target = f"""
        .target(
            name: "{name}UITests",
            destinations: [{platform}],
            product: .uiTests,
            bundleId: "{args.bundle_id_prefix}.{name}.UITests",
            deploymentTargets: {deployment}("{args.deployment_target}"),
            infoPlist: .default,
            sources: ["{name}UITests/**"],
            dependencies: [
                .target(name: "{name}"),
            ]
        ),"""
        ui_scheme = f', "{name}UITests"'
    return f"""import ProjectDescription

let project = Project(
    name: "{name}",
    options: .options(
        automaticSchemesOptions: .enabled(),
        defaultKnownRegions: ["en", "zh-Hans"],
        developmentRegion: "en"
    ),
    targets: [
        .target(
            name: "{name}",
            destinations: [{platform}],
            product: .app,
            bundleId: "{args.bundle_id_prefix}.{name}",
            deploymentTargets: {deployment}("{args.deployment_target}"),
            infoPlist: .extendingDefault(with: [
                "CFBundleDisplayName": .string("{name}"),
                "LSApplicationCategoryType": .string("public.app-category.productivity"),
            ]),
            sources: ["{name}/Sources/**"],
            resources: ["{name}/Resources/**"]
        ),
        .target(
            name: "{name}Tests",
            destinations: [{platform}],
            product: .unitTests,
            bundleId: "{args.bundle_id_prefix}.{name}.Tests",
            deploymentTargets: {deployment}("{args.deployment_target}"),
            infoPlist: .default,
            sources: ["{name}Tests/**"],
            dependencies: [
                .target(name: "{name}"),
            ]
        ),{ui_target}
    ],
    schemes: [
        .scheme(
            name: "{name}",
            shared: true,
            buildAction: .buildAction(targets: ["{name}"]),
            testAction: .targets(["{name}Tests"{ui_scheme}]),
            runAction: .runAction(configuration: .debug),
            archiveAction: .archiveAction(configuration: .release)
        ),
    ]
)
"""


def app_file(name: str) -> str:
    return f"""import SwiftUI

@main
struct {name}App: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
        }}
    }}
}}
"""


def content_view() -> str:
    return """import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(ProductIdentity.repositoryName)
                .font(.title)
                .fontWeight(.semibold)

            Text(ProductIdentity.positioning)
                .foregroundStyle(.secondary)
        }
        .padding(24)
        .frame(minWidth: 420, minHeight: 240)
    }
}

#Preview {
    ContentView()
}
"""


def product_identity(name: str, platform: str) -> str:
    return f"""enum ProductIdentity {{
    static let repositoryName = "{name}"
    static let productName = "{name}"
    static let positioning = "Native {platform} app scaffolded with Tuist"
}}
"""


def unit_test(name: str, platform: str) -> str:
    return f"""import Testing
@testable import {name}

@Test func productIdentityKeepsProjectNameAndPositioning() {{
    #expect(ProductIdentity.repositoryName == "{name}")
    #expect(ProductIdentity.productName == "{name}")
    #expect(ProductIdentity.positioning == "Native {platform} app scaffolded with Tuist")
}}
"""


def ui_test(name: str) -> str:
    return f"""import XCTest

final class {name}LaunchTests: XCTestCase {{
    func testAppLaunches() {{
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(app.wait(for: .runningForeground, timeout: 5))
    }}
}}
"""


def verify_script(name: str, platform: str, include_ui: bool) -> str:
    destination = "platform=macOS" if platform == "macOS" else "platform=iOS Simulator,name=iPhone 16"
    ui_line = ""
    if include_ui:
        ui_line = f"xcodebuild test -scheme {name} -only-testing:{name}UITests -destination '{destination}'\n"
    return f"""#!/usr/bin/env bash
set -euo pipefail

tuist generate --no-open
xcodebuild build -scheme {name} -destination '{destination}'
xcodebuild test -scheme {name} -only-testing:{name}Tests -destination '{destination}'
{ui_line}"""


def update_bmad(root: Path, args: argparse.Namespace, name: str) -> None:
    if args.update_bmad == "never" or not (root / "_bmad").exists():
        return
    config = root / "_bmad" / "config.toml"
    if config.exists():
        config_lines = [
            'build_system = "tuist"',
            f'source_dir = "{name}/Sources"',
            f'test_dir = "{name}Tests"',
        ]
        if args.ui_tests:
            config_lines.append(f'ui_test_dir = "{name}UITests"')
        append_unique(
            config,
            "\n".join(config_lines),
            dry_run=args.dry_run,
        )
    status = root / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
    if status.exists():
        destination = "platform=macOS" if args.platform == "macOS" else "platform=iOS Simulator,name=iPhone 16"
        smoke = (
            f'  smoke_command: "xcodebuild test -scheme {name} -only-testing:{name}UITests -destination \'{destination}\'"'
            if args.ui_tests
            else "  smoke_command: null"
        )
        append_unique(
            status,
            f"""verification_commands:
  generate_command: "tuist generate --no-open"
  build_command: "xcodebuild build -scheme {name} -destination '{destination}'"
  test_command: "xcodebuild test -scheme {name} -only-testing:{name}Tests -destination '{destination}'"
{smoke}
  verify_command: "scripts/verify.sh\"""",
            dry_run=args.dry_run,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap a Tuist Apple app scaffold.")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--platform", choices=["macOS", "iOS"], required=True)
    parser.add_argument("--bundle-id-prefix", required=True)
    parser.add_argument("--deployment-target", default="26.0")
    parser.add_argument("--target-dir", default=".")
    parser.add_argument("--no-ui-tests", action="store_true")
    parser.add_argument("--update-bmad", choices=["auto", "never"], default="auto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    args.ui_tests = not args.no_ui_tests

    name = swift_identifier(args.project_name)
    root = Path(args.target_dir).expanduser().resolve()
    files = {
        root / "Project.swift": project_swift(args, name),
        root / "Tuist" / "Package.swift": """// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ProjectDependencies",
    dependencies: []
)
""",
        root / name / "Sources" / f"{name}App.swift": app_file(name),
        root / name / "Sources" / "ContentView.swift": content_view(),
        root / name / "Sources" / "ProductIdentity.swift": product_identity(name, args.platform),
        root / name / "Resources" / "Assets.xcassets" / "Contents.json": """{
  "info": {
    "author": "xcode",
    "version": 1
  }
}
""",
        root / f"{name}Tests" / "ProductIdentityTests.swift": unit_test(name, args.platform),
        root / "scripts" / "verify.sh": verify_script(name, args.platform, args.ui_tests),
    }
    if args.ui_tests:
        files[root / f"{name}UITests" / f"{name}LaunchTests.swift"] = ui_test(name)

    for path, content in files.items():
        write_file(path, content, force=args.force, dry_run=args.dry_run)

    append_unique(
        root / ".gitignore",
        """# Tuist/Xcode generated files
*.xcodeproj
*.xcworkspace

# Xcode user state
xcuserdata/
*.xcuserstate
*.xcscmblueprint

# Build outputs
Derived/
DerivedData/
.build/
build/

# macOS
.DS_Store""",
        dry_run=args.dry_run,
    )

    update_bmad(root, args, name)

    verify_path = root / "scripts" / "verify.sh"
    if not args.dry_run and verify_path.exists():
        mode = verify_path.stat().st_mode
        verify_path.chmod(mode | 0o755)

    print(f"Tuist {args.platform} scaffold prepared for {name} in {root}")
    print("Next: run 'tuist generate --no-open' and 'scripts/verify.sh' in the target directory.")


if __name__ == "__main__":
    main()
