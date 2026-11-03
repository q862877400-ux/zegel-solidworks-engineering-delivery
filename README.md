# Zegel-SWE · SolidWorks 工程交付系统（DeepSeek 能力库）

[中文](README.md) · [English](README.en.md)

把中国机械设计的规范、判据与建模方法编译成 DeepSeek 能调用、能被机器验收的能力，让一条指令产出的 SolidWorks 模型达到机械工程师的可交付水准：全约束、参数化可重建、特征树可编辑、装配自由度闭合、图样合规、工艺可行、结论可溯源。

这里做的是把规范编译成能力，工具只是末端执行器。完整定义见 [docs/PROJECT-CHARTER.md](docs/PROJECT-CHARTER.md)，路线与施工顺序见 [docs/ENGINEERING-PATH.md](docs/ENGINEERING-PATH.md)。

```text
规范层（L2） · 方法层（L3） · 工具层（MCP / Skill / CLI） · 验收层（E1–E7 采集器与判定器）
```

## 一、状态与边界

| 项 | 当前口径 |
|---|---|
| 真机基线 | SolidWorks 2024、SolidWorks 2026 SP01.1、AutoCAD 2024 |
| 兼容目标（未回归） | SolidWorks 2025 及其它未回归组合 |
| 能力真源 | [capabilities.yaml](capabilities.yaml)。`verified` 有自有运行证据，`stitched` 是移植加静态核对，`not_implemented` 是明确没做 |
| 模型可见工具面 | 544 条 MCP 工具（499 条声明式 + 45 条手写），用真握手 `tools/list` 实测（`python -B tools/probe_mcp_stdio_handshake.py` 得到 531 条 `solidworks_*` 加 13 条 `cadstudio_*`） |
| 工具语义出处 | 其中 524 条有「官方 API 页加逐字锚点」的依据台账（[docs/tool-official-claims/](docs/tool-official-claims/)），其余 20 条是已登记缺陷（[specs/353-mcp-tool-official-audit/](specs/353-mcp-tool-official-audit/)） |

没验证过的能力不会被包装成已完成。受控 `pilot` 的域（配置族、钣金 U 型轮廓法兰与展开 DXF、HSS 矩形焊接框架与切割清单、Simulation/FEA、Routing、复杂曲面、模具）在 `capabilities.yaml` 里逐条标注，不当作原生完整交付。

## 二、四个入口

四个入口平级，共用同一套能力与脚本。

| 入口 | 是什么 | 启动 |
|---|---|---|
| MCP Server | 本地 `stdio` MCP，暴露 SolidWorks COM 白名单工具与无 CAD 的开放格式工具 | `python mcp-server\server.py`（由 MCP 客户端作为子进程拉起） |
| Skill | 支持 skill 导入的客户端直接加载本仓库根目录 | 见 [SKILL.md](SKILL.md) |
| 桌面端 | CAD Studio 图形界面：项目、对话、任务、预览、交付 | [apps/desktop](apps/desktop)、[apps/workbench-ui](apps/workbench-ui) |
| DSH preset（可选） | 让 DSH 会话直接拿到全部 544 个工具的模式「Lean 模式（SW工程师）」。插件与安装器都在仓库里，换机器不用手改 profile | `python -B tools\dsh-preset\install_preset.py --apply`，见 [docs/dsh-preset-sw-engineer.md](docs/dsh-preset-sw-engineer.md) |

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

SolidWorks 是 Windows 桌面 COM 应用，本 server 默认 `stdio` 并在内部用全局锁串行执行。不要在同一个机器上同时起多个 SolidWorks MCP，多进程抢同一 COM 连接会死锁。

## 三、仓库结构

| 路径 | 内容 |
|---|---|
| `mcp-server/` | MCP Server 与工具声明（`server.py`、`tool_registry.py`、`tool_specs_batch*.py`） |
| `scripts/` | 能力层与全部门禁（`sw_*.py` 能力模块、`check_*.py` 门禁、`release_check.py`） |
| `tools/` | 真机护栏（`guard_run.py`）、探针、生成器、收尾链（`round_chain.ps1`） |
| `docs/` | 章程、路线、计划、知识条目、实测台账（`docs/state/`）、历史归档（`docs/history/`） |
| `specs/` | 按 Spec Kit 组织的逐项规格（spec / plan / tasks / 验收读数） |
| `tests/` | 契约测试与门禁自证（含负例） |
| `apps/` | 桌面端（Tauri 加 Web 前端） |
| `references/`、`subskills/`、`examples/` | 参考资料、子技能、可复现示例 |
| `AI Solidworks/` | 本机官方文档、模型、截图工作区（不入库，见 `.gitignore`） |

## 四、质量与验收

```powershell
# 全量门禁（66 道：五统一、签名、单位、证据、门禁接线、工具契约、官方依据台账等）
python -B scripts\release_check.py

# 一轮收尾链（生成器 + release_check + 聚焦测试，约 3–5 分钟）
pwsh -File tools\round_chain.ps1 -Tests tests\<改过的>.py

# 真机命令一律走护栏（自动识别并处置模态弹窗，结束必打 VERDICT 行）
python -B tools\guard_run.py --timeout 300 -- <你的命令>
```

判据口径：

- 验收判据是 charter 的 E1–E7，不是工具条数。采集器从实际产物取数，判定器对冻结要求判断。
- 单位纪律：任何带量纲的形参，名字里必须有单位后缀（`_mm`、`_m`、`_deg` 等），换算只在边界做一次。
- 官方依据：动任何 COM 成员前先读官方页（签名、Remarks、Example）。工具说明要能指回官方页的逐字锚点，`scripts/check_tool_official_claims.py` 会拒掉编造引文、指错页与漏查成员。

## 五、文档入口

| 想知道 | 去哪 |
|---|---|
| 项目为什么存在、成功长什么样 | [docs/PROJECT-CHARTER.md](docs/PROJECT-CHARTER.md) |
| 怎么做到（路线与 S0–S6） | [docs/ENGINEERING-PATH.md](docs/ENGINEERING-PATH.md) |
| 现在该做什么 | [docs/PLAN.md](docs/PLAN.md) |
| 各项读数与复现命令 | [docs/state/INDEX.md](docs/state/INDEX.md) |
| 操作纪律（给人与 AI 都适用） | [AGENTS.md](AGENTS.md) |
| 已知事实、死路、踩过的坑 | [docs/known-facts.md](docs/known-facts.md)、[docs/dead-ends.md](docs/dead-ends.md) |

## 六、来源与许可

- 本仓库以 MIT 发布，见 [LICENSE](LICENSE)。
- 与上游 `wzyn20051216/solidworks-automation-skill` 有代码与文档层面的来源关系。上游 README 原文归档在 [docs/history/README-upstream.md](docs/history/README-upstream.md)，安装与使用以本文档为准。
- 四家外部 MCP 项目的取用范围与义务（MIT、Apache-2.0 保留 NOTICE、AGPL 只读思想不抄代码）见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)。破解类站点零接触。

## 七、参考资料与致谢

项目起步时对公开的 SolidWorks 自动化项目做过一轮通读和调研：读它们的接口封装、测试分层、错误处理和对官方 API 的理解，用来决定自己该怎么做、哪些路走不通。下面按用途列出调研过的项目。许可一栏是 2026-11 逐个读仓库里的 `LICENSE` 文件核出来的，不是看 README 徽章。

**实际用到了代码或设计**

| 项目 | 许可 | 参考了什么 |
|---|---|---|
| `wzyn20051216/solidworks-automation-skill` | MIT | 本项目的最初来源。`mcp-server/server.py` 原样保留（45 个工具实现），49 个 `scripts/*.py` 模块与 `subskills/` 在此基础上继续做 |
| `microsoft/UFO` | MIT | 配置驱动的 GUI 输入层设计（`input_text_api`、`input_text_enter`、`input_text_inter_key_pause` 那一套），用于 `sw_gui_input.py` 与 `sw_jlcfa_fill.py`。模式借自它，代码是自己写的 |
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | 模具域该有哪两个动作（分型线、补孔面）。它的方法名在官方反射里查不到，所以只取思路，实现照出厂反射写 |

**评估过、未并入代码**

| 项目 | 许可 | 参考了什么 |
|---|---|---|
| `andrewbartels1/SolidworksMCP-python` | MIT | 工具分组与参数组织的对照 |
| `vespo92/SolidworksMCP-TS` | MIT | `mock-solidworks-adapter` 的测试分层、macro-generator、若干 `.vba` 样例 |
| `Slacker-LLC/solidworks-mcp` | Apache-2.0 | 工具面覆盖范围对照。当前未并入，故其 NOTICE 义务尚未触发 |

**调研与交叉验证**

| 项目 | 许可 | 参考了什么 |
|---|---|---|
| `xarial/codestack` | MIT | 建视图、文档操作、装配、导入导出，以及 troubleshooting 的故障分类 |
| `angelsix/solidworks-api` | MIT | SolidDNA 模板思路（免弹模板设置） |
| `deloarts/pyswx` | MIT | 类型库封装的组织方式 |
| `painezeng/CSharpAndSolidWorks` | MIT | 几何算法（自交、凸性、面积）与 `.SLDPRT` 测试件 |
| `alisamsam/Solidworks-MCP` | MIT | 27 个 `.vbs` 语料，用于核对 VBScript 侧写法 |
| `delancy827/solidworks-skills` | MIT | 交叉验证（「23 参数不是 17」的独立佐证） |
| `djlex83/solidworks-automation-skill` | MIT | `VARIANT(VT_DISPATCH, None)` 的简洁写法 |
| `Sakikooooo/solidworks-auto-modeling` | MIT | `Nothing`（标量 Dispatch）与 `Empty`（Variant）的区分 |
| `Mochaxgcc/solidworks-ai-bridge` | MIT | 裸传 23 个位置参数的佐证 |
| `guoleizhen717/solidworks-api-skill` | MIT | 反例：它说的「超过 12 个参数会失败」不成立，别采信 |
| `ZiChen-Ni/solidworks-com-automation-skill` | MIT | 最小 COM 封装与 Windows 安装脚本 |
| `just1step/solidworks-mcp` | MIT | 工具面覆盖对照 |
| `Cai-aa/CAD-Agent-Hub` | MIT | Agent 与 CAD 协作的组织方式 |
| `kalyanpi4/pySW` | GPL-2.0 | 只读思想，未抄代码 |
| `eyfel/mcp-server-solidworks`（产品名 SolidPilot） | AGPL | 只读思想，未抄代码。同源的 `Bennyco86/q3ds-solidworks-mcp` 亦为 AGPL |
| `pedropaulovc/offline-solidworks-api-docs` | 无许可 | 只读流水线思路。本机 `C:\swapi` 的整理方式受其启发，产物不随本仓库分发 |
| `pengxiaoan/solidworks-build-mechanical-models` | 无许可 | 只读思想 |
| `walterkken/doc-driven-engineering-software-skills` | 全版权保留 | 只借鉴「文档驱动目录结构」这一条方法论 |

另外两套官方离线源是日常依据：SolidWorks API 帮助（CHM 解包）与结构化 markdown 类型库，用来核对签名、Remarks 与官方示例的调用序。它们不是开源项目，此处只作说明。

以上项目的作者和维护者让这些经验可以被读到，这个项目因此少走了不少弯路，在此致谢。若发现上表的许可判定或归属有误，请提 issue，会按实际情况改正。

## 八、维护规则

- 提交走 `python tools/commit_mine.py -m <信息文件> <路径…>`。不要裸用 `git commit -m "<多行>"`，PowerShell 会把引号当 pathspec。
- 推送远端、建立新仓库、发 release 属于需要业主批准的动作，本地提交不需要。
- 每轮收尾：`round_chain` 绿，按路径提交；状态写进 `capabilities.yaml` 与 `docs/` 台账，不写进对话。
