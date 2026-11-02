# L3 任务书 · SolidWorks × Agent 三个月增量调研（2026-08-01 → 2026-11-02）

> 档位：**L3 大规模多线**（候选池 > 10，跨 5 个技术层）。
> 依据：`research-protocol` 技能 `references/l3-brief.md` —— 「没有任务书不许开搜」。
> 业主 2026-11-02 指令：主渠道 GitHub，其他渠道酌情；找两样东西——聪明的技术路径、已做得很好的完整体。
> 业主已确认三项口径：双轨时间窗（2026-08-01 后首次公开 **或** 近 90 天仍活跃）· clone 读码 + 跑非 SolidWorks 部分 · 卡片追加到 `docs/survey/cards/` + 主报告。

---

## L3.1 要回答的问题（一句话）

**2026-08-01 以来，「让 Agent 在 SolidWorks 里建模」这条线上，有没有出现 (a) 能改变我们技术路径的机制，或 (b) 一个已经做得够好、让我们可以停止自研的完整体？**

反例（不许这么问）：「市面上有哪些 SolidWorks MCP」——那只是清单，不是判断。

---

## L3.2 具体问题（按重要性排序，每条都要给结论句）

| # | 问题 | 为什么它排这个位置 |
|---|---|---|
| **Q1** | 有没有项目能通过「几何正确性独立验证」？ | **这是唯一能决定「停止自研」的问题。** 判据：自带数值断言 / 第三方复现 / oracle 比对，且我们本机能复现。跑不动就写跑不动，不许拿 README 宣称顶替 |
| **Q2** | 有没有解掉我们已知最贵四个问题的机制：持久引用（几何变更后选择失效）· 回读验证 · 事务式建模 · 单源 COM 互斥？ | 决定技术路径。我们的 `docs/dead-ends.md` 与已知事实 24 都在这四件事上卡过 |
| **Q3** | 三条路线（Skill 包 / MCP 服务端 / CLI+脚本）在三个月内的证据里，哪条成功率更高、成本更低？ | 决定我们该把力气放哪。当前本仓是 MCP 服务端路线（439 个工具） |
| **Q4** | 不用 SolidWorks 的路线（开源参数化 CAD + agent / 直接读写 SLDPRT）到什么水平了？ | 「换底座」可能是比「继续补工具」更省的答案 |
| **Q5** | DSH / Codex 系 skill 包这三个月集中涌现（中文生态），有真东西还是重复造轮子？ | 数量最多的新增，最可能是噪声，也最可能藏着便宜的真货 |
| **Q6** | 我们的台账（50 卡 + 21 项目）哪些假设被这三个月的新证据推翻或加强？ | 防止把「已登记」当「已知」，也防止漏掉老项目的新突破 |

---

## L3.3 对照基线（所有结论都是拿别人跟它比）

### 我方现状（带日期的一手读数）

| 项 | 读数 | 来源 |
|---|---|---|
| 能力条数 | **117 条**（verified 105 / stitched 10 / not_implemented 2） | `capabilities.yaml`，2026-10-06 读数 |
| 注册 MCP 工具 | **439 个**（92 个批次文件）+ 上游 `server.py` 45 个 | 2026-10-06 读数 |
| 已有逐项目卡片 | **50 张** | `docs/survey/cards/`，2026-10-24 |
| 仓库外克隆 | **26 个目录**（25 git 检出 / 23 有 LICENSE） | `docs/state/facts/N-external.md`，2026-10-24 |
| 已知死路 | 68 条涉及 39 个能力 | `docs/dead-ends.md`，2026-10-06 读数 |

### 已有结论里必须被复核的三条

1. **50 家里只有 4 家真跑过自带单测**（fusion360 367 passed / blender 494 / cadam 36 / mcp-cadquery 7 failed+80 passed），其余标「读码」——来源 `docs/survey/README.md` §7 已知偏差。
2. **SolidPilot 自述「持久引用解析器」是 make-or-break module still ahead** —— 这是它自己承认没解决的事，三个月里有没有补上，是本轮必答。
3. **四家 SolidWorks MCP 都没有 `operation` 分派**（一动词一工具）—— 本轮要验：新出的有没有改这条路。

---

## L3.4 固定产出格式

### 卡片（追加到 `docs/survey/cards/<slug>.md`，必须过 `scripts/check_survey_cards.py`）

沿用现有 9 节结构（照 `docs/survey/cards/sw-slacker-llc.md` 抄格式）：

```
# <owner>/<repo>
<!-- survey: class=?; repr=?; orchestration=?; verify=?; deliver=?; evidence=实测|读码|元数据 -->
| 字段 | 值 |  （仓库/许可/元数据/克隆/证据等级）
## 1. 一句话定位
## 2. 技术路径（输入→中间表示→生成→编排→执行→验证→交付）
## 3. 技术方案要点（可迁移的机制）
## 4. 运行条件与依赖
## 5. 失败模式与已知坑
## 6. 对我方目标的可用处（能学 / 不能学）
## 7. 许可与红线
## 8. 证据清单（文件:行）
## 9. 未确认事项
```

枚举（`docs/survey/README.md` §4 R7）：
`class`=A 代码单发·B 代码回环·C 多智能体·D 序列/DSL·E 网格·F 逆向·G 模板+规则·H GUI/API 代理·I 知识助手·J 世界模型；
`repr`=code·sequence·dsl·feature-tree·mesh·constraint·params·none；
`orchestration`=single·loop·multi-agent·template·human-approve·none；
`verify`=none·run-only·geometry-gate·numeric·visual·solver·dfm-rules·export-readback；
`deliver`=STEP·mesh·drawing·gcode·none；`evidence`=实测·读码·元数据。

### 主报告 `docs/research/sw-agent-2026Q4/report.md`

顺序固定：**结论先行 → 逐个点评 → 对不上的地方 → 待核清单 → 反证检索记录 → 两本账**。

### JSONL 侧车 `docs/research/sw-agent-2026Q4/projects.jsonl`

每对象一行，最小必填 6 字段：`id` `url` `verdict` `evidence_url` `fetched` `depth`。
`verdict` 只许四值：`借鉴`／`可选`／`不适用`／`待核`。
`depth` 只许：`metadata`／`readme`／`source`／`fulltext`／`tested`。

---

## L3.5 证据分档（四档，写进每张卡）

| 档 | 判据 |
|---|---|
| 【实测】 | 本机跑过，附命令 + 输出 |
| 【一手】 | 读到官方文档/源码/仓库文件/论文原文，附 URL 或 `文件:行` + 日期 |
| 【转述】 | 中文技术号、CSDN、知乎、公众号一律此档 |
| 【推断】 | 判断，无实验支持 |

**四条硬规矩**：数字写清「谁说的、在哪、哪天抓的」；只读 README 就写「只读到 README」；**字段描述 ≠ 运行时行为**；严禁把聚合对比文章当一手。

---

## L3.6 已判死清单（不要再提，除非新反证）

来自 `docs/dead-ends.md` 与 `docs/survey/README.md` §5：

1. **不做多智能体辩论**（arXiv 2502.08788，5 种 MAD × 9 基准 × 4 模型，未超过单 agent 基线）。
2. **不把「一个万能工具 + operation 枚举」当解法** —— 四家 SolidWorks MCP 都没走这条路。
3. **不碰破解**：`DefinetlyNotAI/Solidworks-Crack`、`ruralnymph/SOLIDWORKS-License-2026-Full-Unlock`、`xdu-aero-association/SolidWorks_2020_Crack` 零接触（铁律 2 红线）。
4. **AGPL/GPL 只读思想**：`eyfel/mcp-server-solidworks`、`q3ds-solidworks-mcp`、`Robusr/Vulcan`、`tian-yu200/dsh-solidworks`、`coleas33/smart_SW`、`Peak-Design/CADder` —— 不抄代码。
5. **不重复调研已登记对象**：`docs/survey/cards/` 50 张 + `docs/sources.md` 21+ 项目，只查增量。

---

## L3.7 分线 + 交叉规则

| 线 | 范围 | 代表候选（初筛） |
|---|---|---|
| **A** | 驱动 SolidWorks 的 MCP 服务端 / agent 服务 | `hjbaard/SolidWorks-MCP` · `soheil-mp/solidworks-mcp` · `aiforyouself/solidworks-mcp-server` · `infei12306/solidworks-bridge` · `qdaia/Auto-SolidWorks` · `HarrierPigeon/Solidworks-MCP-Server` · `alisamsam/Solidworks-MCP` · `kumar1441/forge_ai` · `raylanlin/Millwright` · `arthurle3210/SwpilotCLI` · `Robusr/Vulcan` · `Erfouni/solidworks-GPT-plugin` · `muerus/SolidWorks-Python` · `monozukuri-ai/sldkit` |
| **B** | Skill 包路线（Codex / Claude / DSH） | `delancy827/solidworks-skills` · `GaoFei-Max/*` · `LTGOz/solidworks-agent-skill` · `panp20469-png/*` · `ZiChen-Ni/*` · `capwitf/mechanical-cad-skills` · `27painter/dsh-sw-cad` · `tian-yu200/dsh-solidworks` · `fyjgtddco/DSH-SW-and-CAD` · `wLj924/*` · `tsy7-7/*` · `djlex83/*` |
| **C** | 换底座（开源参数化 CAD + agent） | `tangency-labs/solidcraft` · `Peak-Design/CADder` |
| **D** | 不装 SolidWorks 读写 SLDPRT | `schwitters/openswx` · `blussyya/sldprt-format-research` · `XRTC5/sldprt-export` · `dsandall/sld2step` · `hxyulin/sw-rs` · `djbarrow/freecad_solidworks_plugin` |
| **E** | 已有台账增量复核 | `eyfel/mcp-server-solidworks`（SolidPilot 持久引用）· `q3ds-solidworks-mcp` · `just1step/solidworks-mcp` · `vespo92/SolidworksMCP-TS` · `andrewbartels1/SolidworksMCP-python` · `Slacker-LLC/solidworks-mcp` · `Cai-aa/CAD-Agent-Hub` · `wzyn20051216/solidworks-automation-skill`（上游本体） |

**交叉规则（写死）**：同一条事实只在一线写细，其它线写「见 X 线」。**不许两线重复评同一对象。**

---

## 覆盖证明（交付时必须给）

1. **三重账本对账**：检索命中数 == 我登记数 + 具名剔除数，无重复。
2. **失败具名**：抓不到的照样进清单标 `fetch_failed`，不许静默跳过。
3. **每条带复核方法**：`文件:行` 或完整命令。

---

## 边界声明

- 不保证运行时行为都验过（静态检查验不了跑起来会怎样）。
- 不保证大文件内容都读过（只检结构，抽样，**写明是抽样**）。
- SolidWorks 真机不跑（业主选的是 clone 读码 + 跑非 SolidWorks 部分）⇒ 一切「建模能力」结论最高到 `source`，到不了 `tested`。
