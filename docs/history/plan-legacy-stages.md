# 旧阶段体系与支线记录（历史归档）

> **本文件不再维护，只作追溯。** 它装的是 `docs/PLAN.md` 里被新技术路径取代的部分：
> - `一·C` / `一·D`：Bunny 并行批量作业支线（已全部完成）
> - `一·B`：本轮新增的关键事实（已并入 `docs/known-facts.md`）
> - `二 阶段总览` / `三 阶段详情`：**P0–P9 旧阶段体系** —— 已被
>   [`../ENGINEERING-PATH.md`](../ENGINEERING-PATH.md) 的 **S0–S6** 取代
>
> 想知道「现在该做什么」看 [`../PLAN.md`](../PLAN.md) 与
> [`../ENGINEERING-PATH.md`](../ENGINEERING-PATH.md)。

---

## 一·C · 支线：Bunny 并行批量作业（规格 specs/203-bunny-sideline-batches）

> **这一节是支线的**（另一个对话在做，见 docs/kickoff-bunny-sideline.md）。
> 支线**只做可穷举、可逐条核、不需要判断力**的批量辅助；判据设计 / 真机 / 门禁 / 提交仍归主线。
> 主线只需要读**产物**，不必读支线的做法。

| 批 | 做什么 | 产物 | 实测读数 |
|---|---|---|---|
| — | 官方成员页抄录（上一批 A 任务） | docs/recon/iview-read-members.md · drawingdoc-read-members.md · isheet-read-members.md | IView 461（**149 废弃 / 45 指针 / 267 可用**）· IDrawingDoc 274（110/4/160）· ISheet 53（13/2/39） |
| — | 仓库 COM 成员名对账（B 任务） | docs/recon/member-inventory.md | 1429 调用点 / **744 去重** / 524 有官方页 / 220 只在反射清单 / **两源皆无 0** |
| — | docs/ 文档互相矛盾（C 任务） | docs/recon/doc-contradictions.md | 97 份 / 6390 claim → 6385 过引文核验 → 137 强候选**逐条判完，真矛盾 0** |
| **B1** ✅ | `capabilities.yaml` 的 `evidence` 回读 | `docs/recon/verified-evidence-audit-2.md` | 110 条 / 314 条 evidence / 64 yes · 42 no（**其中 34 条 `level=verified`**，已附**两形态**标注）/ 1 条证据路径不存在 / **98 条 evidence 其实是散文** |
| **B2** ✅ | 官方源自身的机械缺陷 | `docs/recon/official-source-defects-2.md` | 13086 页 / 964 条过闸（作废 6）/ **65 条真死链 + 50 条拼错接口名 + 58 条成员名不在**（文件系统事实）· 554 条同族两种拼法 |
| **B3+B4** ✅ | 官方示例的调用序 + 成员索引 | `docs/recon/member-to-example-index.md` | **2839 份示例全读** / 抽出 **3985 个成员名（3887 查得到）** / **2826 份带具体前置**（`*.sldprt must be open`、`must be selected` 那类） |
| **B5** ✅ | 全量接口台账 | `docs/recon/interface-ledger.md` | 566 目录 / **11557 成员** / 1642 废弃(严) / 520 指针(R) / 9395 可用 · **IView 回归 6 项全对** |

**三条实测出来的作业方式**（再派活请照做）：

1. **子代理只能是 Bunny**，且 provider 与 model **必须成对写**（opencode-zen + space-bunny-free）——
   只写 model 会**整批静默失败**（100 路回 
eturned: 0 且无报错）。
2. **一波 ≤ 60 路**，且**一份文档一路**（3 份合批的 8 个批次曾**全灭**；一份一路 38/38）。
3. **两道闸缺一不可**：① 每条 quote **逐字回查原文**（实测挡掉过 Bunny 的 5 条编造）；
   ② Lead **独立复核**（B1 里我把「目录」误判成「不存在」，留档在产物 §三）。

**支线不碰**：capabilities.yaml · scripts/ · 	ests/ · 	ools/ · 根 AGENTS.md · 门禁 · git。

## 一·D · 支线规格 204：Bunny 集群的六件「别人做不到」的事（全部完成）

> 接 §一·C（规格 203）。**六件全部产出、全部过三裁判门禁**。进度与全部门禁结论在
> `specs/204-bunny-moat-batches/goal-bar.md`。

| 件 | 做什么 | 产物 | 门禁改写了什么 |
|---|---|---|---|
| **C1** | 多路一致率（K 路交叉验证） | `docs/recon/multiway-agreement.md` | 我的头条一致率**虚高 4.5 个点**（把 L1 归一化叫成「原始」） |
| **C2** | 四家工具 × 官方签名对账 | `docs/recon/competitor-signature-crosscheck.md` | 名字数 **185 行 → 162 名**（185 是行数不是名字数） |
| **C3** | 官方示例前置 × 本仓 evidence | `docs/recon/precondition-vs-evidence.md` | 头部 **80 → 75**；V2 抓到 **3 个编造的示例文件名** |
| **C4** | 官方示例 ↔ 成员页 Remarks 冲突 | `docs/recon/official-internal-conflicts.md` | 真冲突 **544 → 约 250**（抽检 12 条只 4 条真互斥）；**漏报一整类**（官方幽灵成员名） |
| **C5** | 并集 349 个操作的三态澄清 | `docs/recon/union-gap-tristate.md` | **真缺 ≥5 → ≥2**；`why` 约三成是抽签产物（脚本 bug） |
| **C6** | 事实唯一家（6390 条 claim） | `docs/recon/fact-single-home.md` | **真分歧 4 → 0**（4 组全是时序更新） |

★★ **贯穿六件的一条**：**没有一件是门禁原样通过的**，六件的头条数**全部被改写**。
更正集中在三类，**每一类都可预先防住**：

1. **口径未写死**（C1 归一化层级 · C4 引文闸折叠口径 · C6 归一化配方 · C5 工具名 441/460）
   ⇒ ★ **判定式必须落成可复现的代码，不能只写在散文里。**
2. **判据比结论宽**（C4 把「示例没照文档做」算成矛盾 · C3 把示例运行环境算成 API 前置）
   ⇒ ★ **判据要写「不算什么」，不只是「算什么」。**
3. **稳定性没验**（C5 从 `set` 里取 `exact[0]` · C6 的公式漂移）
   ⇒ ★ **凡是从集合里「取一个」的地方，都要固定顺序。**

★ **V2 对抗者是最有价值的那一票**：它三次找到「编造/幽灵」（C3 的假文件名 · C4 的漏报 · C5 的抽签指向），
而它在第 3–5 轮因 `space-bunny-free` 路由故障缺席过三次。
⇒ ★ **三票不齐时我坚持记 `conditional_pass`、不写「完成」** —— 事后证明这个坚持是对的：
C5 一直是 conditional，而 V2 一回来就推翻了它的结论。

## 一·B 本轮新增的**关键事实**（写代码直接用，别重新推导）

| 事实 | 依据 |
|---|---|
| 官方 `Int32&` 出参**必须**传 `VARIANT(VT_BYREF\|VT_I4, 0)`（`sw_connect.out_i4()`）；裸值或省略都失败 | 真机五形态裁决 · `probe_outparam_convention.py` |
| 空 Dispatch 参数**要精确到哪一参**：`SelectByID2` 第 8 参、`AddRestraint` **第 3** 参须包 `VARIANT(VT_DISPATCH, None)`；`AddRestraint` 第 2 参传裸 `None` **可以** | 真机四形态裁决 · `probe_dispatch_variant.py` |
| `CreateNewStudy3(name, 13, 0, out_i4())` 能建成拓扑研究，`AnalysisType == 13` | 真机 · SW 2026 SP4.1 |
| 拓扑整链**未通**：`CreateFactorOfSafetyConstraint` 返回 None；`SetIterationOption` 抛 `0x80010105` | 同上 |
| 本机 Simulation **完整安装**：`Simulation\Topology\` 下有 `SMATsoFortranCoreCore/Prep/Opt.dll` 与 **`smatrtsmooth.dll`**（Export Smoothed Mesh 的实现） | 磁盘 + 真机 `GetAddInObject` ✓ |
| 嘉立创FA插件「卡住」= **预加载数百张分类缩略图**，不是文件锁、不是断网 | 其 `Logs\20261001.log`：`NetworkCheck Status OK 114ms` + `图片加载统计 累计150张 成功=150` |

**格式约定**：状态取值 `⬜ 未开始` / `🟡 进行中` / `✅ 完成` / `⏸️ 阻塞（写原因）`。
「最近三次交接」只留三条，滚动覆盖 —— 它给的是**时间感**，不是历史（历史在 git log）。

---

## 二 · 阶段总览

| # | 阶段 | 主要产出 | 对应验收判据 | 依赖 | 状态 |
|---|---|---|---|---|---|
| **P0** | 发布前置义务 | `THIRD-PARTY-NOTICES.md` | A6 | — | ✅ |
| **P1** | 拓扑结果读取 | `sw_topology.py` 补「看结果 / 导出」 | A9 | — | ✅ 看结果已达成；**导出**五源查不到 |
| **P2** | 拓扑真机实测 | `capabilities.yaml` 升 `verified` | A4 · A9 | P1 | ✅ **`verified`** |
| **P3** | 并入模板定型 | **原写「最小四个域 = 16」—— 该前提已证伪** | A1 · A2 · A10 | P0 | ✅ 判据已改 + 真缺口（模具）已并 |
| **P4** | ~~并入：中量域 69~~ | **前提已证伪**：那 69 是「MCP 暴露面」之差，**不是**能力缺口 | A1 · A2 · A10 | P3 | ⛔ 见调整记录 |
| **P5** | ~~并入：工程图 49~~ | 同上 | A1 · A2 · A10 | P4 | ⛔ 见调整记录 |
| **P6** | ~~并入：余下大域 205~~ | 同上 | A1 · A2 · A10 | P4 | ⛔ 见调整记录 |
| **P7** | 收口：审计与报告刷新 | `signature-audit.md` · `harvest-report.md` | A5 · A8 | P2 · P6 | ✅ |
| **P8** | 发布准备 | 自建仓库远端 + 推送 | A6 §七 | P7 + **用户批准** | ⛔ **只等用户输入** |
| **P9** | **用户视角覆盖面缺口** | `specs/202-user-coverage-gaps/` · 缺口项工具化 | A1 · A4 · A10 | — | 🟢 **批 1 已交付**（真机 3 项 · 覆盖率 **99/145**） |

**━━━━━━━━━ 调整记录（§二 同步，2026-10-01）━━━━━━━━━**

**原计划**：P3–P6 按「并入 **339** 个缺口操作」推进（P3=16 · P4=69 · P5=49 · P6=205）。

**证伪过程**：P3 原计划搬焊件域，动手第一步发现**本仓库早就有** `scripts/sw_weldment.py`
（666 行 / 20 函数），且 `capabilities.yaml` 里 `weldments` 是 **`verified`**。

**根因**：`tools/build_union_map.py` 的 `_our_tools()` **只数 `mcp-server/server.py` 的工具名**，
而本仓库的能力实现在 `scripts/` 里、**没暴露成 MCP 工具**（`AGENTS.md` 已知事实 25 记的正是这个交集为 0）。
**⇒「339」= 四家以 MCP 工具暴露、而本仓库没有以 MCP 工具暴露的操作数。
它不是「本仓库缺 339 个能力」。**

逐域核实（`python D:\AI\SW\capability_gap.py`，两口径**并存各标**）：

| 域 | 地图说缺 | 本仓库实际函数 |
|---|---|---|
| ⑧ 焊件 | 5 | **14**（且 `verified`） |
| ③ 草图 | 42 | **57** |
| ⑩ 装配 | 19 | **54** |
| ⑤ 零件特征 | 30 | **53** |
| ⑪ 工程图 | 49 | **44** |
| ⑥ 曲面 | 12 | **17** |
| ② 参考几何 | 4 | **22** |
| ⑨ **模具** | 3 | **1 ⇒ 唯一的真缺口** |

本仓库真实能力面：**72 个 `scripts/sw_*.py` 模块 / 814 个公开函数**。

**⇒ 处置（已执行）**：
1. **P4–P6 的「并入 N 个操作」作废** —— 那些域**本仓库已有实现**，
   盲目「并入」会**重复实现**并造出**第二份实现**（违「一个事实一个家」）。
2. **判据改为「按能力口径找真缺口」**（`capability_gap.py` 可重跑）。
   实测：**唯一真缺口是模具**（1 个函数）—— **已被 P3 并掉**（`scripts/sw_mold.py`，7 个入口）。
3. **旧数字保留**但必须带口径说明（「**MCP 暴露面**」）。地图 §二 已加「本仓库能力面」列，
   两列并排，`⚠` 标注「这不是能力缺口」。
4. **已更正长期记忆**（Correction 文档）与 §五 反模式（「拿一个口径不清的数字当计划前提」）。
5. **P3 的实际产出**从「并入 16 个操作」变为：**① 判据更正（可重跑）；
   ② 并入唯一真缺口（模具域生成侧）；③ 并入模板定型**
   （「思路取自来源，签名取自反射」—— 见 `_raw/source-defects/Eduardof0nt.md`）。

**⚠ 这条调整的意义**：P4–P6 **不需要再做了** —— 不是「做完了」，
而是**它们要解决的问题不存在**（那些域本仓库已有能力）。
**真正的剩余缺口是「把已有能力暴露成 MCP 工具」**（已知事实 25 的交集 0），
评估见 `docs/T-011-expose-capabilities-assessment.md`（真实工作量 **~120 个函数**，不是 814）。


**缺口口径**（**别用错数**：曾把「四家域操作总数」当成「我们的缺口」，草图 77 vs 真实 42）：

```powershell
python D:\AI\SW\map_gaps.py          # ⚠ 这是**MCP 暴露面**口径，合计 339（**不是**能力缺口）
python D:\AI\SW\capability_gap.py    # ✅ 这才是**能力面**口径（两个口径并存各标，不可合并）
```

**排序理由**：

- **P0** 是「推送任何远端都要带」的硬义务，很小，先清掉。
- **P1/P2** 把**刚做到一半的护城河闭环**（趁上下文热；护城河是任务里那个「1」）。
- **P3 故意选最小的四个域**（16 个操作）：**目的是定型模板，不是刷量**。
  这四个域我们目前是 0，闭掉它们 ⇒ A1 的「每一格都有来源」立刻有四个域达标，
  而且它们是 Eduardof0nt 独家有货（许可面最窄，冲突最少）。
- **P4–P6 按缺口从小到大**：先用中量域把模板练熟（P4），再啃第一大域（P5），
  最后清尾（P6）。**反过来做（先啃 49）会在模板还没定型时踩最多坑。**
- **P5 与 P6 并列可换序**：工程图 49 是最大单域，但草图 42 更**基础**
  （其余域的实现常依赖草图）。若在 P4 之后发现草图是瓶颈，**对调 P5/P6 是允许的调整**。


---

## 三 · 阶段详情

> 每块只写**不变的**四件事：读数 / 做 / 验收 / 产出。
> 状态在 §一；对后续阶段的改动写在块的「调整记录」里，并在 §四 汇总。

### P0 · 发布前置义务（`THIRD-PARTY-NOTICES.md`）

**读数**
- [AGENTS.md](../AGENTS.md) §二 铁律 6（Apache-2.0 的 NOTICE 义务）
- [docs/sources.md](../docs/sources.md) 的许可判定表
- 代码副本 `tools/union-sources.json` 的 `license` 字段（四家的真实许可）

**做**
写 `C:\swprojects\sw-skill-fork\THIRD-PARTY-NOTICES.md`，含：
1. `Slacker-LLC/solidworks-mcp` 的 `Copyright 2026 JIALE LIU`（Apache-2.0 要求保留 NOTICE）
2. **声明改动了哪些文件**（Apache-2.0 的另一项义务）
3. MIT 三家（`Eduardof0nt` / `andrewbartels1` / `vespo92`）与上游的版权声明保留说明
4. 一句话写清「本项目是原创仓库，不是上述任何一家的 fork」

**验收**
```powershell
cd C:\swprojects\sw-skill-fork
Test-Path THIRD-PARTY-NOTICES.md                                    # → True
Select-String THIRD-PARTY-NOTICES.md -Pattern 'JIALE LIU' | Measure-Object | % Count   # → >= 1
python scripts\check_union_conventions.py                           # → exit 0
```
**★ 这条是可 grep 的**：A6 要求「Apache-2.0 来源带 NOTICE 义务」，判据就是那个版权行在不在。

**产出**：`THIRD-PARTY-NOTICES.md`

**调整记录**：（暂无）

---

### P1 · 拓扑结果读取（A9 的后半）

**读数**
- 代码副本 `scripts/sw_topology.py` 的模块 docstring「覆盖边界」段 —— 里面写明了**为什么现在没有**
  （反射里未核到对应成员，按铁律 5 不编）
- 抢救区那份笔记的「下一步」段：`D:\AI\SW\solidpilot-salvage\官方文档\拓扑优化_官方做法.md`
- 本机 CHM 清单：`cworks.chm`（17 MB，Simulation 总览，**未解包**）

**做**
1. 解包 `cworks.chm`（方法照抢救区笔记 §0：输出目录必须**不存在**、路径**短且无空格**）
2. 在解包物 + `cosworks` 反射转储里找这三个入口的**真实成员名**：
   - `Material Mass` 结果图（官方 `t_viewing_optimization_results.htm`）
   - `View Convergence Data and Graph`（官方 `t_exporting_optimization_results.htm`）
   - `Export Smoothed Mesh`（同上，产出 mesh BREP 的新 .SLDPRT）
3. **找到就实现；找不到就写「查不到」并停**（铁律 5）—— 不许用相似名字蒙混
4. 补契约测试（连同 P1 一起跑）；`capabilities.yaml` 的 `limitations` 相应条目要**删掉**
   （那条写的是「结果读取未实现」，实现后就过期了 —— 过期的东西就是腐坏）

**验收**
```powershell
cd C:\swprojects\sw-skill-fork
python -m pytest tests/test_sw_topology_contract.py -q      # → 全绿，且条数 >= 8
python scripts\audit_call_arity.py scripts\sw_topology.py `
    D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt           # → 「查不到」= 0
python scripts\check_union_conventions.py                   # → exit 0
# ↓ 若确实查不到，则必须满足：模块里出现「查不到」字样，且 limitations 保留该条
```
**★ 判据是双向的**：要么实现且 arity 审计「查不到=0」；要么明写「查不到」。
**不允许的是「既没实现、也没说不做」** —— 那正是 A8 要的「写明仍空缺什么」。

**产出**：`scripts/sw_topology.py`（补函数）+ 契约测试 + `capabilities.yaml` 的 `limitations` 更新

**调整记录**：（暂无）

---

### P2 · 拓扑真机实测（升 `verified`）

**读数**
- [AGENTS.md](../AGENTS.md) 铁律 2（实测三条安全约束：`CommandInProgress` / 超时 / 收尾）
- 代码副本 `scripts/sw_simulation.py` 的 `get_cosmosworks`（加载项入口与许可证检查）
- 官方 CHM `C:\topo_en\t_creating_topology_study.htm`（**只能单实体零件**那条约束）

**做**
1. **先问用户**：本机有没有 Simulation 许可证？有没有可用的测试零件？
2. 找一个**单实体零件**（装配体必须先另存为零件 —— 官方硬约束）
3. 按官方流程跑一遍：建 13 型研究 → 目标 + 质量约束 75% → 夹具 → 载荷 → 网格 → 求解
4. 把**真实跑过的命令 + 结果摘要**写进 `capabilities.yaml` 该条的 `evidence`，
   并把 `level` 从 `stitched` 升 `verified`，`allowed_modes` 加 `unattended`（R11 要求）

**验收**
```powershell
cd C:\swprojects\sw-skill-fork
python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));e=[x for x in d['capabilities'] if x['id']=='topology_optimization'][0];print(e['level'], e.get('evidence'))"
# → verified ['<真跑过的命令与结果>']      ← evidence 非空是硬要求
python scripts\check_union_conventions.py    # → exit 0（R5 会查 verified 的 evidence）
python -m pytest tests/test_unattended_equivalence.py -q   # → 全绿（授权集合变化要被这条测试承认）
```
**⚠ 这台机器上只有用户的 SolidWorks**：可**自行拉起**，但**必须自关** —— 跑完立刻收尾；
拉起用 `python tools/reclaim_solidworks.py --restart`（自带安全判定：打开的文档只要有一个不是自己的就拒绝重启），
**不要手写 WMI 派发**；关闭时**只关自己开的那一个**（同时可能有别的会话在用）。
★ 2026-10-05 业主明确授权「自开自关」；原文（只接管已开的实例、**不自行启动**）已按授权改。

**产出**：`capabilities.yaml` 该条升 `verified` + `evidence`；实测脚本归 `D:\AI\SW\`

**调整记录**：（暂无）

---

### P3 · 并入模板定型（**最小的四个域**）

> **这是整条 B 级路线的模板。** 哪怕只有 16 个操作，也要把六条规则**全部**走一遍并留下可复制的样板。
> 选最小的四个域是**故意的**：模板定型期的目的是**把坑踩完**，不是刷量。

**读数**
- 代码副本 `docs/union-coverage-matrix.md` **§五 的 ⑧ 焊件 / ⑨ 模具 / ② 参考几何 / ⑬ 仿真 四节**
  （每节给了来源、许可、**来源验证状态**、缺口操作名）
- [AGENTS.md](../AGENTS.md) §五「并入五步」+ 并入六条规则表
- 代码副本 `docs/union-conventions.md`（六条规则**全文**）
- **工作区** `docs/provenance-format.md`（`provenance` 字段与格式 —— ⚠ 在**工作区**不在代码副本）
- **来源仓**：`C:\swprojects\Eduardof0nt\`（MIT；这四个域它**独家**有货）

**做**
1. 在来源仓里定位该域的实现文件，**读它的实现**（不是抄它的注释）
2. 每个 COM 调用与官方签名对齐（铁律 4：两套官方源 + 反射三源互证）
3. 移植进 `scripts/`，带**来源头注释**（仓库 / 文件 / 定位 / 许可 / 未实测标注）
4. 在 `capabilities.yaml` 登记：`id` / `label` / `level` / `backends` / `limitations` /
   `allowed_modes` / **`provenance`**（`repo` 用 `owner/repo` 全名、`license` 在白名单、
   `files` 非空、`upstream_verified` 字段必须在 —— 可为**空串**，因为 Eduardof0nt 没声明跑过）
5. 写契约测试（照 `tests/test_sw_topology_contract.py` 的形状：枚举对账 + 成员名对反射）
6. 跑门禁；**`level` 只能标 `stitched`**（来源没声明跑过 + 我们没跑过）

**验收**
```powershell
cd C:\swprojects\sw-skill-fork
python -m compileall -q scripts                               # → exit 0
python scripts\check_union_conventions.py                     # → exit 0（6 组全 PASS）
python scripts\check_provenance.py                            # → PASS（新代码行都有出处）
python -m pytest tests -q                                     # → 与基线逐条相同
# 四个域的缺口是否闭掉（对地图重生成后逐域核）
python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));print(len([c for c in d['capabilities'] if c.get('provenance')]),'条带 provenance')"
# → >= 4（四个域各自至少一条），且总条数 >= 28 + 4
```
**★ A2 的判据就是这条**：`grep` 抽查 10 条并入条目，100% 带 `provenance`。

**产出**：`scripts/` 下的域模块 + 测试 + `capabilities.yaml` 条目 +
**一份「并入模板」记录**（写进 `docs/harvest-report.md`，供 P4–P6 照抄）

**调整记录**：（暂无）

---

### P4–P6 · ~~并入逐域推进~~ **已作废**（2026-10-01 前提被证伪）

> ⛔ **本节整段作废，保留仅为留痕。** 它按「**339 个缺口操作**」拆活，而那个数字是
> **MCP 暴露面之差**、不是能力缺口（见 §二 的调整记录）。
> 表里那些「域（真实缺口）」在本仓库**多数已有实现** —— 照它并入会**重复实现**。
> **真正剩下的活是「把已有能力暴露成 MCP 工具」**，见
> [T-011 评估](history/T-011-expose-capabilities-assessment.md)（~120 个函数，不是 814）。
>
> 本节以下内容**一字未删**，因为它是「一个口径不清的数字如何污染整份计划」的标本。

**共用读数 / 做 / 验收**：与 P3 同构，只换域与来源行。每域开工前**必读**
`docs/union-coverage-matrix.md` §五 的**该域那一节**。

**重构提示**：P3 定型后若发现「每个域一个模块」不如「按来源仓分模块」，
**在这里改**（并写进调整记录）—— 模板的价值就是它可以被推翻一次。

| 阶段 | 域（**真实缺口**） | 首选来源（该域有数） | 注意 |
|---|---|---|---|
| **P4** | 尺寸 11 · 钣金 11 · 曲面 12 · 检查 16 · 装配 19 | Eduardof0nt 6/10/11/11/13 | 钣金与曲面上游**已有** `subskills/` 与既有模块 ⇒ **先看能否扩，不重写**（铁律 1：沿用本项目既有模式） |
| **P5** | **工程图 49**（最大单域） | Eduardof0nt 18 · andrewbartels1 18 · Slacker-LLC 17 · vespo92 15 | 上游 `subskills/solidworks-engineering-drawing` 有 2033 行 ⇒ **扩写优先**。`Slacker-LLC` 是**唯一声明跑过**的家（`SW 2026 SP3.2 简体中文`）⇒ 它的部分可标 `source_verified` |
| **P6** | 草图 42 · 宏 42 · 未归类 44 · 会话 37 · 零件 30 · 外观 10 | 见地图各节 | 草图上：`andrewbartels1` 的「草图完全定义探针」**有测试**且 MIT ⇒ 优先（[AGENTS.md](../AGENTS.md) 已知事实 22）。`Slacker-LLC` 的**声明式 selection** 也是它家的（MIT 三家没有） |

**⚠ 每个域都要过一遍的「反大杂烩」检查**（六条规则里最容易漏的两条）：
- **规则 1 命名统一** `solidworks_<域>_<动作>`；headless 的 `cadstudio_*` 不混用
- **规则 3 声明式 `selection`**，不写裸坐标

**⚠ 每次并入前先问一句**：这个域的缺口操作，**是不是同义词重复**？
（四个来源各起一个名字的同一件事，只应登记一条 —— 否则 `capabilities.yaml` 会被灌水）

**调整记录**：（各阶段完成时填）

---

### P7 · 收口：审计与报告刷新

**读数**
- 代码副本 `docs/signature-audit.md`（当前是 09-29 的，**已过时**）
- 代码副本 `docs/harvest-report.md`（当前标题写「A1 · 逐域打勾表（14 域，无空白格）」，
  但那是**官方 API 覆盖**的口径，**不是** A1 要的「四家广度并入」口径 —— 见 §五 反模式）

**做**
1. 重跑 arity 审计覆盖**全部**改动过的模块，刷新 `signature-audit.md`
2. **重写 `harvest-report.md`**：把「A1 打勾表」明确切成两张表 ——
   「官方 API 覆盖（14 域）」与「四家广度并入（16 域）」，**标题不许都叫 A1**
3. 逐域核对 A1：「每一格都有来源，或写明「不做 + 原因」」

**验收**
```powershell
cd C:\swprojects\sw-skill-fork
python scripts\audit_call_arity.py scripts\sw_weldment.py D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt
python scripts\check_diff_markers.py                          # → PASS
Select-String docs\harvest-report.md -Pattern '14 域|16 域' | Measure-Object | % Count   # → >= 2（两张表都在）
python -m pytest tests -q                                     # → 与基线逐条相同
```

**产出**：`docs/signature-audit.md`（刷新）+ `docs/harvest-report.md`（重写）

**调整记录**：（暂无）

---

### P8 · 发布准备

**读数**：[AGENTS.md](../AGENTS.md) §七（Git 规则：建自建仓库 / 加远端 / 推送**都要先批准**）

**做**：等用户给远端地址 → `git remote add` → 推送（**必须先获批准**）
**验收**：`git remote -v` 有目标远端；`THIRD-PARTY-NOTICES.md` 在仓库根
**产出**：自建仓库

---

### P9 · 用户视角覆盖面缺口（规格 `specs/202-user-coverage-gaps`）

**读数**（开工前先跑，确认起点是**真的**，不是记忆里的"应该做完了"）

```powershell
python tools\audit_gap_implementations.py     # 35 个缺口项里，本仓**已有真实现**的有几条（AST 判，不用 grep）
python -c "import io,re;t=io.open('docs/user-feature-coverage.md',encoding='utf-8').read();print(re.search(r'本仓库\*\* \| (\d+/145)',t).group(1))"
```

**做**：按 `specs/202-user-coverage-gaps/research.md` §五 的分诊五类
（A 已建成 · B 有实现未暴露 · C 候选直入法 · D 到不了 · E 待查）逐批推进：
① **C 类先做工程图 13 项**（视图族 5 + 标注族 8；侦察已确认官方入口 13/13 命中）；
② **钣金/焊件 5 项先试直入法**（真名已回查到）；
③ **E 类 2 项换名重查**（加厚 · 曲线驱动阵列）。

**验收**（可跑；跑不出绿就不算完成）

```powershell
python tools\audit_gap_implementations.py                                    # 重扫实现状态
python -c "import io,re;t=io.open('docs/user-feature-coverage.md',encoding='utf-8').read();print(int(re.search(r'本仓库\*\* \| (\d+)/145',t).group(1))>=110)"   # SC-001（★ 现 99，未达标）
pwsh -File tools\round_chain.ps1 -Tests tests\test_official_md_claims_gate.py  # release_check 第 1 轮 OK
```

**产出**：`specs/202-user-coverage-gaps/`（spec / plan / tasks / research / recon）·
新工具（`mcp-server/tool_specs_batch*.py` + `scripts/`）· `capabilities.yaml` 条目 ·
`docs/backend-limited-items.json` 追加项。

⚠ **本阶段明令不许**（★ 三条都是本轮**用真金白银换来的**）：
1. ★ 把**未真机验证**的标 `verified`（铁律 2）；
2. ★ 因为 `*FeatureData` 带 `AccessSelections` 就**先判「到不了」** ——
   反例就在本仓：分割线也有 `ISplitLineFeatureData`，而**它的直入法真机建成了**（事实 484）；
3. ★ 拿**「有实现」当「能用」** —— 反例：样条曲线（AST 说有实现，实为轮 141 已判死不达，事实 488）。

---

