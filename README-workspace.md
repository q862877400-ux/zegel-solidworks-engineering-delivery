# ⚠ 本文件是**合并前**的工作区 README（历史存档）

> ★ 2026-10-03：`D:\AI\SW` 与 `C:\swprojects\sw-skill-fork` 已合并为一个仓库，
> 故下面这段原文里「代码本体在 `C:\swprojects\sw-skill-fork\`（独立 git 仓库）」**已过时** ——
> 现在**代码与本工作区在同一个仓库里**。原文保留，作为当时的设计记录。

---

# D:\AI\SW — SolidWorks 自动化 skill 工作区

> **这是工作日志，不是产品。** 代码本体在 `C:\swprojects\sw-skill-fork\`（独立 git 仓库）。
> 本仓库存在的唯一理由：**把「做过什么、怎么做的、结果如何」版本化**，
> 免得上下文一压缩就忘了自己做过什么。

## 三处路径（别搞混）

| 路径 | 是什么 | git |
|---|---|---|
| `D:\AI\SW\` | **本仓库** —— 工作区 + 草稿 + 日志 + 报告 | ← 你在这里 |
| `C:\swprojects\sw-skill-fork\` | **代码工作副本** —— 唯一改代码的地方 | 独立 git（origin = 上游，只读锚点） |
| `D:\AI\SW\AI Solidworks\` | 官方 API 文档（CHM 解包，285 MB） | 已 gitignore（第三方、只读） |

## 本仓库的内容

| 目录/文件 | 是什么 |
|---|---|
| `AGENTS.md` | ★ 任务唯一开工入口（任务定义、铁律、验收判据、已知事实） |
| `*.py`（约 700 个） | **草稿脚本 —— 根目录就是草稿区**。命名规律：`fx*` = 修复尝试，`dbg*` = 调试，`jlc*` = 嘉立创，`live*` = 实测 |
| `*.log` | 运行日志（如 `final12g.log` = 12 件抽查的完整过程） |
| `*.json` | 结果报告（`batch_report.json` = 抽查结果，`toolsets.json` = 五家 MCP 工具清单） |
| `research/` `explore/` | 调研与探索产物 |
| `evidence/` `batch_evidence/` | **失败/成功的截图取证**（12/12 抽查的证据在这里） |
| `docs/` | 文档与生成物 |
| `tools/` | ★ **正式工具**（`gen_*.py` 生成器、`audit_*.py` 审计、`eval-*.ps1`）。**一次性量测脚本不要放这里** |
| `commit-messages/` | ★ **提交信息草稿**（`_msg*.txt` / `_commitmsg*.txt`）。2026-10-01 从根目录归档，共 63 个 |

**分类规矩**（2026-10-01 立）：

| 东西 | 去哪 |
|---|---|
| 一次性量测 / 调试 / 修复尝试的脚本 | **根目录**（草稿区，与既有的 ~700 个同类一致） |
| 正式、会被反复用的工具 | `tools/` |
| 提交信息草稿 | `commit-messages/` |
| 截图证据 | `evidence/` / `batch_evidence/` |

⚠ 反面教材：`desc_caliber.py`（量 MCP 工具描述的三个口径）被 `cordis.patch.yml` 的注释
按 `D:\AI\SW\desc_caliber.py` 引用 ⇒ **它必须留在根目录**，挪走要同步改那处引用。
**有外部引用的草稿，路径就是它的契约。**

## 已排除（`.gitignore`）

- `AI Solidworks/` — 第三方官方文档 314 MB，只读，可重新解包
- `_raw/` — 反射原始转储 22 MB，结论已固化进代码副本的 `sw_api_*.py`
- `shots/` — 探索期截图 50 MB（关键证据在 `evidence/`）
- `cadir/` — CAD 保真数据 10.7 MB，可重新导出
- `__pycache__/` — 可再生产物

## 当前任务状态（随进展更新）

任务：把 `wzyn20051216/solidworks-automation-skill`（1010★, MIT）补成**官方 API 全覆盖 + 集众家之所长**。

方向演进（2026-09-30）：
1. ~~官方 API 全覆盖缝合~~（已达成：881 族 / 12,859 成员索引完整）
2. **集大成**：把 4 个 MIT/Apache MCP 项目的广度并入，一家替代所有
3. **护城河**：拓扑优化（经核实全网无工程实现）

详见 Hindsight 知识页：
- `SolidWorks skill 官方 API 全覆盖缝合`（原任务）
- `集大成：把 4 个 MIT/Apache 项目的广度并入本仓库 + 拓扑优化护城河`（新方向）

## 红线（来自 AGENTS.md）

- 不碰注册表 / 全局环境变量 / 系统层
- `C:\swprojects\.misumi.env` 永不回显、永不提交
- AGPL / GPL / 无许可项目**只读思想，不抄代码**
- 未经批准不 `git push`、不建 fork、不发布

## 一条给未来自己的提醒

**本仓库里的 `.py` 大多是草稿，不是产品。** 有用的结论应该沉淀到
`C:\swprojects\sw-skill-fork\scripts\` 里，带来源头注释和测试。
草稿留在这里是为了「记得当时怎么试的」，不是为了复用。
