# Feature 149 · 真缺口批量挂柜台（24 小时计划 v2）

> 状态与进度**不写这里**（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> ★ 本特性的**作业单**是 **`docs/plan-24h-v2.md`**；本文件是它的 Spec Kit 规格。

## 一、要解决的问题

`tools/audit_real_gaps.py` 刚给出**已核实的口径**：**真缺口 101 条**
（公开 202 · 有我们工具 86 · 被上游 `server.py` 调 22）。
⇒ ★ 这 101 条里，**真正该挂成 MCP 工具的只是一部分** —— 混着内部件、返回值不可靠的族、
需要新注入键的。**没人分过诊**。
⇒ ★★ 所以本轮要解决的问题是：**把这 101 条变成"该挂的挂上（带真机证据）、不该挂的写清原因"**，
并且**在 24 小时内全自动推进**。

## 二、§5.0：先找（★ 按关键词，不按我打算起的名字）

```
★ 搜 `audit_real_gaps` / `真缺口` / `挂柜台` ⇒ ★ **已有**：`tools/audit_real_gaps.py`（口径脚本）·
  `docs/union-gap-evidence-based.md`（逐条判定表）· `docs/plan-24h.md`（第一轮 24h 计划，已收口）
★ 搜四家有没有现成的"批量挂工具"套路 ⇒ ★ **没有**（四家都是手写 `@mcp.tool`，无分诊层）
⇒ ★ 结论：★ **分诊层要自己搓**（★ 而"挂工具"的**实现**照官方签名 + 既有模块包装 —— 那是缝合，不是发明）。
```

## 三、需求（各带来源）

| # | 需求 | 来源 | 验收 |
|---|---|---|---|
| R1 | 101 条**先分诊**：① 该挂 ② 内部件不挂 ③ 不做（+原因） | 硬约束⑧「只做**已核实**的真缺口」；★ 反面教材：事实 40（`IModeler.Create*Surface` 返回值跨次都变） | `tools/triage_real_gaps.py` 产出三类清单 + 计数 |
| R2 | 每个**新挂**的工具必须有**真机 pass** | 硬约束③「每件声称完成的事必须有 `output/*-evidence.json` 的 `verdict: pass`」 | 每个工具一个探针 + evidence.json |
| R3 | 判据**先找后搓** | `AGENTS.md` §5.0（强制第一步） | 每段动手前的搜索记录写进该段结论 |
| R4 | 数字**全部来自生成物** | 硬约束②（不手改 `docs/metrics.md`） | 收敛报告的数字与 `metrics.md` / `audit_real_gaps` 零偏差 |
| R5 | 每批一个 commit（**仅本地**）· 两个仓库 clean | 红线（不 push / 不建远端 / 不发 release）+ Git 规则 | `git status --porcelain` 空 |
| R6 | **不做的东西写清原因** | 硬约束⑥「验不过的回退、不许留在柜台上」的反面：**该说不做的要说不做** | `docs/union-gap-evidence-based.md` + `plan-24h-v2.md` §四 |
| R7 | 新文件带**六字段来源块** | 硬约束⑨（`release_check` 的出处门禁会拦） | `check_python_syntax.py` + `release_check.py` 绿 |
| R8 | 改运行时文件后**重跑** `sync_bundled_skill.py` | 硬约束⑩（事实 55） | `release_check.py` 的「桌面内嵌 Skill 一致性」段 |
| R9 | 高风险写操作**不碰** | 硬约束⑦ | 段内自查：不出现保存/另存/删除调用 |
| R10 | 判据**先找后搓**且**来源行带 license** | 铁律 6 + 宪法 | 来源表逐行 `owner/repo` + 许可 |

### 来源与许可（★ 每行带 license —— 宪法要求）

| 来源 | 用途 | 许可 | 能做什么 |
|---|---|---|---|
| SolidWorks 官方 API 文档（`C:\swapi\` + CHM 解包） | 签名与语义裁决 | 官方文档 | ★ 决定接口选型与参数顺序（铁律 4） |
| 出厂类型库反射（`D:\AI\SW\_raw\`） | 冲突时**裁决者** | 官方 | arity 与枚举数值 |
| `just1step/solidworks-mcp` · `Cai-aa/CAD-Agent-Hub` · `deloarts/pyswx` | 可抄实现 | **MIT** | ★ 可抄代码（保留版权声明） |
| `Eduardof0nt` / `andrewbartels1` / `vespo92` | 能力广度对照 | **MIT** | 可抄 + 保留声明 |
| `Slacker-LLC/solidworks-mcp` | 声明式 selection 等 | **Apache-2.0** | 可抄 + 保留 `NOTICE` + 声明改动文件 |
| `eyfel/mcp-server-solidworks`（SolidPilot）及其 fork | **只读思想** | **AGPL** | ★ **不抄代码、不抄文本** |
| 上游 `wzyn20051216/solidworks-automation-skill` | 基底之一 | MIT | 保留版权声明 |

## 四、24 小时分段（★ 详见 `docs/plan-24h-v2.md` §二）

```
段 0（0–3h）  分诊 101 条 + 造"挂一个工具"的模板
段 1（3–6h）  选择底座 sw_selection_spec（7）      ← 杠杆最高
段 2（6–9h）  草图图元 sw_part（6）
段 3（9–12h） 零件实体族 sw_part 余下（10）
段 4（12–15h）孔族 sw_hole_features（8）
段 5（15–18h）仿真载荷族 sw_simulation_loads（28）  ← 数量最大
段 6（18–21h）导出 6 + 焊件 4 + 拓扑 5
段 7（21–24h）objective② 收口（画图域 + hem）· 曲面族分诊 · 收敛报告
```

## 五、Tasks（★ 每条带 `→ 验收:`）

| # | 任务 | → 验收 |
|---|---|---|
| T0.1 | 写 `tools/triage_real_gaps.py`：把 101 条分三类 | 三类清单落盘 + 计数自洽（三类之和 = 101） |
| T0.2 | 造五件套模板（实现/ToolSpec/探针/capabilities/测试） | ★ 用**段 1 的第一个工具**试跑模板 ⇒ 一条命令走完 |
| T1.1 | 挂 `sw_selection_spec` 该挂的那几条 | 每条一个 evidence.json `verdict: pass` |
| T2.1 | 挂草图图元 6 条 | 同上 + 建出的几何**点数/尺寸**核对 |
| T3.1 | 挂零件实体族 10 条 | 同上 |
| T4.1 | 挂孔族 8 条 | 同上 + `inspect_hole_features` 回读直径/位置 |
| T5.1 | 挂仿真载荷族 28 条 | 同上 + 载荷计数回读 |
| T6.1 | 挂导出 6 + 焊件 4 + 拓扑 5 | 同上（★ 导出类判据是**产物文件存在且非空**） |
| T7.1 | objective② 收口（`balloon`/`datum`/`jog`/`hem`） | 有证据 或 **明确写"做不到 + 原因"** |
| T7.2 | 曲面族 16 条分诊（多为"不做"） | `docs/union-gap-evidence-based.md` 逐条带原因 |
| T7.3 | 收敛报告 `docs/plan-24h-v2-convergence.md` | 数字与生成物零偏差 + 每段注明证据文件 |

## 六、判据（★ 「应该有」必附核查命令）

| 应该有 | 核查命令 |
|---|---|
| 分诊三类之和 = 101 | `python tools/triage_real_gaps.py`（★ 它自己报计数） |
| 每个新工具真机 pass | `python -c "import json,glob;[print(f, json.load(open(f,encoding='utf-8')).get('verdict')) for f in glob.glob(r'D:\AI\SW\output\*evidence*.json')]"` |
| 门禁全绿 | `python scripts/release_check.py` ⇒ exit 0 |
| 全量回归（★ 只在 24h 收尾跑一次） | `python -m pytest -q` |
| 数字与生成物一致 | `python tools/gen_metrics.py && git diff --stat docs/metrics.md`（★ 应为空） |
| 两仓库 clean | `git -C C:\swprojects\sw-skill-fork status --porcelain` + `git -C D:\AI\SW status --porcelain` |

## 七、⚠ 不做的（★ 与需求同等重要）

★ 见 `docs/plan-24h-v2.md` §四：`IModeler.Create*Surface` 13 条（事实 40）· 纯内部件 ·
`InsertMoldShutOffSurface`（事实 309 已穷尽）· 高风险写操作 · 任何 push/远端/release。
