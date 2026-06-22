# Development Workflow Skills

[English](README.md)

这是一个用于沉淀可复用开发工作流的 skills 集合。

它不只是 Codex skills 仓库。Codex 是其中一种使用入口；仓库里的脚本、模板和参考文档也可以直接在终端运行，被其他 AI coding agent 复用，或者接入团队自己的项目初始化流程。

## 为什么需要它

很多工程初始化工作本身不难，但很容易每次做得不一致：

- 不同仓库的项目脚手架细节逐渐漂移。
- 一开始没有可执行的验证命令，后面才发现项目跑不起来。
- `.xcodeproj`、`.xcworkspace`、`Derived/` 这类生成物容易被误提交。
- 只有 PRD / BMAD 的规划仓库，需要一条明确路径变成可运行工程。
- AI coding agent 每次都要重新理解同一套初始化约定。
- 测试 target、UI smoke、build/test 命令这类小决策容易变成隐性知识。

这个仓库的目标是把这些工作流沉淀成可执行、可检查、可复用的资产，而不是依赖记忆或每次复制一大段 prompt。

## 当前 Skills

### `tuist-apple-bootstrap`

用于创建一个最小、可验证的 Tuist Apple 平台工程，支持 macOS 和 iOS。

它会生成：

- Tuist `Project.swift`
- `Tuist/Package.swift`
- App target
- SwiftUI app shell
- Swift Testing 单元测试 target
- 可选 XCTest UI launch smoke target
- `scripts/verify.sh`
- `.gitignore`
- 如果仓库已经存在 `_bmad`，可更新已有 BMAD 状态文件

它不会默认做：

- 固定私人 bundle identifier 前缀
- 初始化 Git 或创建 commit
- 从零创建 BMAD
- 集成 codebase-memory
- 在项目真正需要前添加第三方依赖

## 直接使用脚本

不通过 Codex 也可以直接运行生成器：

```bash
python3 skills/tuist-apple-bootstrap/scripts/bootstrap_tuist_apple.py \
  --project-name SampleApp \
  --platform macOS \
  --bundle-id-prefix com.example \
  --deployment-target 26.0 \
  --target-dir /path/to/repo
```

然后验证生成出来的工程：

```bash
cd /path/to/repo
tuist generate --no-open
scripts/verify.sh
```

iOS 示例：

```bash
python3 skills/tuist-apple-bootstrap/scripts/bootstrap_tuist_apple.py \
  --project-name SampleApp \
  --platform iOS \
  --bundle-id-prefix com.example \
  --target-dir /path/to/repo
```

默认 iOS destination 是 `platform=iOS Simulator,name=iPhone 16`。如果本机没有这个模拟器，只改 `scripts/verify.sh` 里的 destination 字符串即可。

## Codex 使用方式

发布到 GitHub 后，可以用 skill installer 安装到 Codex：

```bash
python3 /path/to/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path skills/tuist-apple-bootstrap
```

然后重启 Codex，让它重新发现 skill。

示例 prompt：

```text
Use $tuist-apple-bootstrap to initialize a Tuist macOS project in this repo.
```

## GitHub 发布检查

发布前请检查 [docs/github-release-checklist.md](docs/github-release-checklist.md)。

关键检查项：

- 确认 GitHub remote 和安装示例使用同一个 owner 与仓库名。
- 用 `gh auth status` 确认 GitHub owner。
- 用 `quick_validate.py` 验证每个 skill。
- 在临时目录中 smoke-test 所有 bundled scripts。
- 确认模板里没有私人 bundle identifier 前缀或本机路径。
- 如果后续添加 GitHub Actions workflow，第一次 push 前确认 GitHub token 有 `workflow` scope。

## 开发

验证 skill：

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  skills/tuist-apple-bootstrap
```

Smoke-test 生成器：

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

MIT
