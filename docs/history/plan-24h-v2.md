# 24 小时计划 v2（`plan-24h-v2.md`）—— **真缺口批量挂柜台**

> 状态与进度**不写这里**（宪法：那在 `ROADMAP.md` §一 / `capabilities.yaml` / `docs/metrics.md`）。
> ★ 本文件是**作业单**：24 小时分几段、每段做什么、怎么算做完。
> ★ 第一轮 24h 计划（`docs/plan-24h.md`，六段）**已收口**（收敛报告 `docs/plan-24h-convergence.md`）。

## 〇、这 24 小时该干什么 —— **由刚跑出来的那张表决定**

```
$ python tools/audit_real_gaps.py
  公开 202 · 有我们工具 86 · 被上游调 22  ⇒ ★ **真缺口 101**
```

**按模块分布**（★ 这就是作业面）：

| 模块 | 真缺口 | 性质 |
|---|---|---|
| `sw_simulation_loads` | **28** | ★ 最大的一块（载荷/约束族） |
| `sw_part` | **16** | 建模核心（草图图元 + 实体特征） |
| `sw_surface` | **16** | ⚠ `IModeler.Create*Surface` 族 —— **事实 40 说返回值不可靠** ⇒ 多半要**标"不做"+原因** |
| `sw_simulation` | **11** | ⚠ 混着**内部件**（`get_cosmosworks` / `resolve_face_selector`）⇒ 要分诊 |
| `sw_hole_features` | **8** | 孔族（含 `get_fastener_*` / `configure_*_tap`） |
| `sw_selection_spec` | **7** | ★ **选择底座** —— 杠杆最高 |
| `sw_export` | **6** | 导出（bmp/image/batch/flat-pattern） |
| `sw_topology` | **5** | 护城河域 |
| `sw_weldment` | **4** | 焊件 |

★ **关键认识**：这 101 条**不是 101 个该挂的工具** —— 里面混着
**内部件**（`get_modeler` / `require_runtime_available` / `EntitySelectionError` / `iter_features_recursive` /
`SketchSelectionRef` / `HoleFeatureEvidence`）与**不该挂的**（返回值不可靠、需要新注入键）。
⇒ ★★ **所以第 0 段是分诊，不是挂工具**（★ 否则会花几小时挂一批没人能调的按钮）。

## 一、排序原则（★ 为什么是这个顺序）

**按杠杆排，不按数量排。** 两条判据：

1. **前置优先**：先做让**后面每批都变便宜**的东西。
   - ★ **选择底座**（`sw_selection_spec` 7 条）：选择是**每一次真机验证**都要用的东西；
     它一挂上，后面每批的探针都能少写几十行。
   - ★ **草图图元**（`sketch_arc/ellipse/polygon/slot/spline`）：它们让**测试几何**更丰富
     ⇒ 后面的验证能从"能不能建成"升级到"建出来的形状对不对"。
2. **同模块成批**：同一模块的 inject 键 / 选择方式 / 探针形状**都一样**
   ⇒ 一个批次的边际成本远低于零散挂。
   ★ **反面**：跨模块混着做 = 每件都要重新摸一遍契约。

## 二、24 小时 = **8 段 × 3 小时**

| 段 | 时段 | 干什么 | 为什么排这里 |
|---|---|---|---|
| **0** | 0–3h | ★★ **分诊 101 条 + 造"挂一个工具"的模板** | ★ 分诊决定后面挂什么；模板让后面 7 段**机械** |
| **1** | 3–6h | ★★ **选择底座**（`sw_selection_spec` 7 条） | ★ 杠杆最高：后面每批的探针都用到它 |
| **2** | 6–9h | ★★ **草图图元**（`sw_part` 6 条：arc/ellipse/polygon/slot/spline/centerline） | ★ 让测试几何更丰富 ⇒ 后面验证更强 |
| **3** | 9–12h | ★ **零件实体族**（`sw_part` 余下 10 条：shell/rib/dome/pattern/dimension…） | ★ 建模核心，用户最常要 |
| **4** | 12–15h | ★ **孔族**（`sw_hole_features` 8 条） | ★ 与段 3 同属"建件"，探针形状可复用 |
| **5** | 15–18h | ★★ **仿真载荷族**（`sw_simulation_loads` 28 条） | ★ 数量最大的一块（★ 而它有真机基础） |
| **6** | 18–21h | **导出 6 + 焊件 4 + 拓扑 5** | ★ 收尾三个小族（★ 拓扑是护城河域） |
| **7** | 21–24h | ★★ **objective② 收口**（画图域 `balloon`/`datum`/`jog` + `hem`）· **曲面族 16 条分诊**（该"不做"的写清原因）· **收敛报告** | ★ 把上一轮的三件事收干净，并**如实记下不做的东西** |

★ **每段结束都必须**：跑收尾链（`round_chain.ps1`）+ 提交 + 把结论写进 `capabilities.yaml` / 事实表。
★ **不做"半件"**：一段里没验完的，要么回退，要么**明确标 `stitched` + 写清卡在哪**（硬约束③⑥）。

## 三、每批的固定形状（★ 段 0 要把它做成模板）

一个批次 = 一个模块 = 一个 commit，固定五件套：

```
① 实现包装     scripts/<module>.py —— 按官方签名包一层，★ 规则 2（单位）/ 3（声明式选择）/ 6（建后回读）
② ToolSpec     mcp-server/tool_specs_batch<NN>.py —— 声明 inject 与 params
③ 真机探针     tools/prove_<module>_<family>.py —— ★ 走 tools/sw_guard.py 护栏 · 正例 + 负例
④ capabilities capabilities.yaml —— mcp_tools + evidence（★ verdict: pass 才能算过）
⑤ 契约测试     tests/test_<module>_<family>_contract.py —— ★ 负例至少一条
```

★ **收工一条命令**：`pwsh -NoProfile -File tools/round_chain.ps1 -Tests tests/<新的>.py`

## 四、⚠ **不做的**（有据，写清理由 —— ★ 与本计划同等重要）

| 不做 | 理由 |
|---|---|
| `IModeler.Create*Surface` 那 13 条（`create_cylindrical_surface` 等） | ★ **事实 40**：返回值**跨次都变**，官方 4 个已 `Obsolete` 且 `*2` 后继同样返回 `None` ⇒ 挂出来只会给人"能调"的错觉。**写进"不做"+原因** |
| 纯内部件（`get_modeler` / `require_runtime_available` / `EntitySelectionError` / `iter_features_recursive` / `SketchSelectionRef` / `HoleFeatureEvidence`） | ★ 不是能力，是**实现细节**；挂出去污染工具面 |
| `InsertMoldShutOffSurface` | ★ **已穷尽式**（事实 309：三次尝试都"回 Feature 而树不变"）⇒ 不再试 |
| 高风险写操作（保存 / 另存 / 删除） | ★ 硬约束⑦（用户未批准） |
| 强推 / 建远端 / 发 release | ★ 红线 |

## 五、验收（24 小时后怎么算成）

| # | 判据 | 怎么验 |
|---|---|---|
| V1 | 真缺口数**下降**且**每一条下降都有真机证据** | `python tools/audit_real_gaps.py` 前后对比 + 逐条 `capabilities.yaml` 的 evidence |
| V2 | 新增工具的**真机 pass 率** = 100% | 每个新工具都有 `output/*-evidence.json` 且 `verdict: pass` |
| V3 | 门禁全绿 | `python scripts/release_check.py` ⇒ exit 0 |
| V4 | 两个仓库 clean，每批一个 commit（本地） | `git status --porcelain` 空 |
| V5 | ★ **不做的东西写清了原因** | 本文件 §四 + `docs/union-gap-evidence-based.md` |
| V6 | 收敛报告 | `docs/plan-24h-v2-convergence.md`（数字全来自生成物） |

★ **判据"先找后搓"**（`AGENTS.md` §5.0）：每段动手前**先按关键词搜**有没有现成实现/判据，
找不到再自己搓 —— ★ 四家 MIT 项目可抄代码（留版权声明），AGPL 只读思想。
