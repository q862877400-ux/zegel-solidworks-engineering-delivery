# 顶层目录实况登记（32 个白名单外目录的逐个说明）

> 从 `AGENTS.md` 铁律 3 搬出（2026-10-24）。原文逐字保留；
> `AGENTS.md` 只留结论与链接（根指令文件只放 1–3 行常驻项）。

**★★ 顶层目录实况登记（★ 2026-10-18 · ★ 落实 §九 停止条件 #5「以实际仓库为准并更新本文件」）**

★ 实测：★ 本仓**实际有 39 个顶层目录**（不含 `.git`、**不含 3 个工具缓存**），★ 而上面白名单只有 **14** 个 ⇒ ★★ **结构与白名单不符** ✗。
★★ **2026-10-21 复核更正**：★ 原先记作 **40**，是把 `.pytest_cache`（**工具缓存、gitignore、不入库**）也当成仓库目录算进去了 ✗。
★ 正确口径：★ **磁盘顶层 = 39 个仓库目录 + 3 个工具缓存**（`.pytest_cache` / `.codebase-memory` / `.ruff_cache`，★ 三者均已 gitignore ✓）。
★ 复核命令：`python -c "import pathlib;[print(d.name) for d in pathlib.Path('.').iterdir() if d.is_dir() and d.name!='.git']"` ✓
★ 逐个登记**多出的 25 个**（★ 每个一句"是什么 / 为什么放不进已有目录" ✓）：

| ★ 目录 | ★ 是什么 | ★ 为什么放不进已有目录 |
|---|---|---|
| `.specify/` | ★ Spec Kit **1.0.13** 集成（commands/templates/scripts/workflows/memory ✓）| ★ 是**第三方工具的检出态**：★ 有它自己的 `.gitignore` 与目录约定 ⇒ ★ 塞进 `tools/` 会破坏它的自更新 ✗ |
| `.dsh/` | ★ DSH 宿主侧项目配置（★ 角色表等 ✓）| ★ **宿主约定目录**（★ 名字由宿主定，★ 不能改 ✗）|
| `.workbuddy-ai/` | ★ 旧宿主留下的**历史开发记忆**（★ 4 份 memory · 420 KB ✓）| ★ 是**史料**不是活代码；★ 已登记在 `output/LEGACY_LOOP_REFERENCES.md` ✓ |
| `AI Solidworks/` | ★ SolidWorks 官方文档/手册/模型/截图（★ **29749 文件** ✓）| ★ **只读外部素材**（★ 与 `references/`＝本仓知识文档**性质不同** ✗）· ★ **不得写入** ✗ |
| `specs/` | ★★ **Spec Kit 规格**（★ 规格数与编号范围见 docs/state/facts/H-specs.md H-01/H-02）| ★ **规格的落点**（★ 不是代码、★ 不是 `docs/` 知识文档、★ 不是 `output/` 产物 ✗）—— ★★ **且门禁 `check_spec_acceptance_paths` 读它们的 `→ 验收:` 行（处数见 docs/state/facts/H-specs.md H-03）** ⇒ ★ **删了会断门禁** ✗ |

★ **产物 / 证据 / 侦察类（★ 均不承载活代码；★ 应 gitignore 或已 ignore ✓）**：
`_proof` · `_raw` · `audit` · `batch_evidence` · `cadir` · `commit-messages` · `corpus` ·
`evidence` · `explore` · `mcp-tool-draft` · `MCP_CALIB` · `metadata` · `net-guard` ·
`research` · `shots` · `solidpilot-salvage` · `swpublished` · `.api-signatures` · `output` · `.pytest_cache`

★★ **结论**：★★ 本节的**白名单数字（14）已不反映实际** ✗ —— ★ **以实际 39 个仓库目录为准** ✓（出处：`docs/state/facts/A-structure.md` A-01 与 `docs/state/inventory-a.json` 的顶层目录清单；复核命令 `python docs\state\probes\probe_structure.py`）；
★★ **新增白名单外的顶层目录，仍须按本节规矩「先登记、再动手」** ✓
