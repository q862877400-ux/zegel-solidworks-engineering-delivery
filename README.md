# SolidWorks 工程交付系统（DeepSeek 能力库）

把**中国机械设计的规范、判据与建模方法**编译成 DeepSeek 能调用、能被机器验收的能力，
使一条指令产出的 SolidWorks 模型达到机械工程师的可交付水准：
全约束 · 参数化可重建 · 特征树可编辑 · 装配自由度闭合 · 图样合规 · 工艺可行 · 结论可溯源。

关键词是「编译成能力」，不是「提供工具」。工具是末端执行器；规范与判据才是本体。
完整定义见 [`docs/PROJECT-CHARTER.md`](docs/PROJECT-CHARTER.md)，
路线与施工顺序见 [`docs/ENGINEERING-PATH.md`](docs/ENGINEERING-PATH.md)。

```text
本项目 = 规范层（L2）· 方法层（L3）· 工具层（MCP/Skill/CLI）· 验收层（E1–E7 采集器与判定器）
这不是上游 skill 的镜像，而是一个独立的工程交付仓库；
上游与本项目的来源关系、四家外部项目的许可口径，见 [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)。
```

## 一、状态与边界（先看这一段，别把 pilot 当交付）

| 项 | 当前口径 |
|---|---|
| 真机基线 | **SolidWorks 2024**、**SolidWorks 2026 SP01.1**、**AutoCAD 2024** |
| 兼容目标（未回归） | SolidWorks 2025 及其它未回归组合 |
| 能力真源 | [`capabilities.yaml`](capabilities.yaml)：`verified` 有自有运行证据，`stitched` 只是移植+静态核对，`not_implemented` 明确没做 |
| 模型可见工具面 | **543** 条 MCP 工具（498 条声明式 + 45 条手写），真握手 `tools/list` 实测 |
| 工具语义出处 | 其中 **523** 条有「官方 API 页 + 逐字锚点」的依据台账（`docs/tool-official-claims/`），其余 20 条是已登记缺陷（`specs/353-mcp-tool-official-audit/defects.md`） |

★ 没验证过的能力**不会**被包装成「已完成」。受控 `pilot` 的域（配置族、钣金 U 型轮廓法兰/展开 DXF、
HSS 矩形焊接框架/切割清单、Simulation/FEA、Routing、复杂曲面、模具）在 `capabilities.yaml` 里逐条标注，
不能冒充原生完整交付。

## 二、三个入口

三个入口平级，共用同一套能力与脚本。

| 入口 | 是什么 | 启动 |
|---|---|---|
| **MCP Server** | 本地 `stdio` MCP，暴露 SolidWorks COM 白名单工具与无 CAD 的开放格式工具 | `python mcp-server\server.py`（由 MCP 客户端作为子进程拉起） |
| **Skill** | 支持 skill 导入的客户端直接加载本仓库根目录 | 见 [`SKILL.md`](SKILL.md) |
| **桌面端** | CAD Studio 图形界面：项目 / 对话 / 任务 / 预览 / 交付 | [`apps/desktop`](apps/desktop)、[`apps/workbench-ui`](apps/workbench-ui) |

### 最小可跑（MCP）

```powershell
# 1. 依赖
pip install -r mcp-server\requirements.txt

# 2. 环境自检（缺什么、影响哪个格式、怎么装，都会列出来）
python scripts\cad_doctor.py

# 3. MCP 客户端里加一条（以 DSH 为例；Claude Code / Cursor 等同理，路径换成你的克隆位置）
```

```json
{
  "mcpServers": {
    "solidworks": {
      "command": "python",
      "args": ["D:/path/to/this/repo/mcp-server/server.py"]
    }
  }
}
```

调用 `solidworks_health_check` 可以确认本机是否连得上 SolidWorks。
**SolidWorks 是 Windows 桌面 COM 应用**，本 server 默认 `stdio` 并在内部用全局锁串行执行，
不要在同一台机器上同时起多个 SolidWorks MCP（多进程抢同一 COM 连接会死锁）。

## 三、仓库结构（主要部分）

| 路径 | 内容 |
|---|---|
| `mcp-server/` | MCP Server 与工具声明（`server.py`、`tool_registry.py`、`tool_specs_batch*.py`） |
| `scripts/` | 能力层与全部门禁（`sw_*.py` 能力模块、`check_*.py` 门禁、`release_check.py`） |
| `tools/` | 真机护栏（`guard_run.py`）、探针、生成器、收尾链（`round_chain.ps1`） |
| `docs/` | 章程、路线、计划、知识条目、实测台账（`docs/state/`）、规格外的历史归档（`docs/history/`） |
| `specs/` | 按 Spec Kit 组织的逐项规格（spec / plan / tasks / 验收读数） |
| `tests/` | 契约测试与门禁自证（负例） |
| `apps/` | 桌面端（Tauri + Web 前端） |
| `references/` · `subskills/` · `examples/` | 参考资料、子技能、可复现示例 |
| `AI Solidworks/` | 本机官方文档/模型/截图工作区（**不入库**，见 `.gitignore`） |

## 四、质量与验收（不是「我觉得没问题」）

```powershell
# 全量门禁（65 道：五统一、签名、单位、证据、门禁接线、工具契约、官方依据台账 …）
python -B scripts\release_check.py

# 一轮收尾链（生成器 + release_check + 聚焦测试，约 3–5 分钟）
pwsh -File tools\round_chain.ps1 -Tests tests\<改过的>.py

# 真机命令一律走护栏（自动识别并处置模态弹窗，结束必打 VERDICT 行）
python -B tools\guard_run.py --timeout 300 -- <你的命令>
```

判据口径：

- **验收判据是 charter 的 E1–E7**，不是工具条数；采集器从实际产物取数，判定器对冻结要求判断。
- **单位纪律**：任何带量纲的形参，名字里必须有单位后缀（`_mm` / `_m` / `_deg` …），换算只在边界做一次。
- **官方依据**：动任何 COM 成员前先读官方页（签名 + Remarks + Example）；工具说明必须能指回官方页的逐字锚点，
  门禁 `scripts/check_tool_official_claims.py` 会拒掉编造引文、指错页与漏查成员。

## 五、文档入口

| 想知道 | 去哪 |
|---|---|
| 项目为什么存在、成功长什么样 | [`docs/PROJECT-CHARTER.md`](docs/PROJECT-CHARTER.md) |
| 怎么做到（路线与 S0–S6） | [`docs/ENGINEERING-PATH.md`](docs/ENGINEERING-PATH.md) |
| 现在该做什么 | [`docs/PLAN.md`](docs/PLAN.md) |
| 各项读数与复现命令 | [`docs/state/INDEX.md`](docs/state/INDEX.md) |
| 操作纪律（给人与 AI 都适用） | [`AGENTS.md`](AGENTS.md) |
| 已知事实 / 死路 / 踩过的坑 | [`docs/known-facts.md`](docs/known-facts.md) · [`docs/dead-ends.md`](docs/dead-ends.md) |

## 六、来源与许可

- 本仓库以 **MIT** 发布，见 [`LICENSE`](LICENSE)。
- 与上游 `wzyn20051216/solidworks-automation-skill` 有代码与文档层面的来源关系；
  上游 README 原文归档在 [`docs/history/README-upstream.md`](docs/history/README-upstream.md)，
  **安装与使用以本仓库本文档为准**。
- 四家外部 MCP 项目的取用范围与义务（MIT / Apache-2.0 保留 NOTICE / AGPL 只读思想不抄代码）见
  [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)。破解类站点零接触。

## 七、维护规则（改这个仓库之前先读）

- 提交走 `python tools/commit_mine.py -m <信息文件> <路径…>`（不要裸 `git commit -m "<多行>"`，PowerShell 会把引号当 pathspec）。
- 推送远端、建立新仓库、发 release 属需要业主批准的动作；本地提交不需要。
- 每轮收尾：`round_chain` 绿 + 按路径提交；状态写进 `capabilities.yaml` 与 `docs/` 台账，不写进对话。
