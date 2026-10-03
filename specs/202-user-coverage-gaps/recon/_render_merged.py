"""★ 渲染合并总表为 preselect-family-merged.md（按工具名排序）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
RECON = ROOT / "specs" / "202-user-coverage-gaps" / "recon"

HEADER = """# 「要求调用方先选」工具族 —— ★ 三路合并总表（唯一总表）

> ★ **本文件是唯一总表**：`preselect-family-a.md`（batch1–25 · 81 条）/ `-b.md`（batch26–50 · 108 条）/
> `-c.md`（batch51–76 · 88 条）三路的**并集**，并补齐三路合计**一条不丢**的全部 ToolSpec。
> ★ 合并者 + 复核者；★ 已对「真危险」那批**逐条独立复核**（spec 侧 + 函数侧 + 官方页）。
> ★ **没有跑 SolidWorks、没有跑 pytest、没有改任何已有文件。**

## 〇、机制前提（复核者逐字核过，不是转述）

`mcp-server/tool_registry.py::make_tool_function._impl` 的调用序（★ 行号为本轮 grep 实测）：

```
507:  kwargs[inject_as or inj] = resolver(params)   ← 第 1 步：注入解析器
508:  if spec.extra_op is not None: return spec.extra_op(params)
510:  if spec.pre_call is not None:
513:      spec.pre_call(params)                    ← 第 2 步：唯一的「建立选区」钩子
514:  if spec.derived_args is not None:
516:      extra = spec.derived_args(params) or {}  ← 第 3 步：第二个可用窗口
524:  mod = __import__("scripts.%s" % spec.module, …)
525:  return getattr(mod, spec.function)(**kwargs) ← 第 4 步：目标函数
```

⇒ **「声明式 selection → 建选区」只有 `pre_call`（第 2 步）与 `derived_args`（第 3 步）两个落点。**
⇒ 两者都没有 ⇒ 该工具在 MCP 表面**没有任何参数**能表达「选哪个实体」。

### ★ 全仓 `pre_call` 盘点（AST 实测，非转述）

★ **全仓 277 条 ToolSpec 里只有 22 条挂了 `pre_call`**，`pre_call` 实现只有 6 个：
`_pre_draft` / `_pre_edge_flange` / `_pre_gusset`（batch4）· `_select_edge`（batch23）·
`_select_face`（batch26/29/58/60）· `_select_faces_for`（batch74）。
★ 另有 **1 条**走 `derived_args` 形态（batch4 的 `swept_flange`）。

### ★ 事实 503「`RESOLVERS` 会清空选区」—— 本轮找到了真机证据文件

★ A 路在其 §五.1 写「**『必被清空』这半句在静态上不成立**」。**本轮复核认为该保留为存疑的只有静态路径，真机路径已有证据**：

`D:\\AI\\SW\\output\\selection-lifetime-evidence.json`（`at: 2026-10-03 22:27:11`）逐步记录：
```
选 2 个面 mark=1（刚选完）      mark1 = 2  ✔
…（读 feature_names / GetBodies2 / GetFaces / FeatureManager / SelectionManager 都不掉）
调过 RESOLVERS['model'] 之后     mark1 = 0  ← ★ 这里被清掉
```
⇒ ★ 「顺序」与「必被清空」**两半都成立**（静态证不出是**因为清空发生在 `connect_solidworks()` 内部**，不在解析器那一行）。

### 分档口径（本轮统一，三路原本不一致）

| 档 | 判据 |
|---|---|
| **安全** | 读选区 ＋ 有 `pre_call`（或 `derived_args → resolve_entity`）⇒ 选区在 inject **之后**建立，能活到第 4 步 |
| **真危险·官方前置** | 官方 Remarks/描述行明写「调用前必须先选」＋ 函数体**不读**选区（选区由 SolidWorks 自己吃）⇒ 缺选区时**静默失败**（返回 None / 无树增量），最隐蔽 |
| **真危险·显式拒** | 函数体自己 `GetSelectedObjectCount2` ＋ 计数为 0 时 `return {"ok": False, "stage": "selection"}` ⇒ 经工具层**必然失败**、失败可见 |
| **真危险·诊断型** | 只读工具，读的就是那个被清空的选区 ⇒ 经工具层**恒回 0**；它不是受害者，是**受害者链的源头** |
| **真危险·条件** | 前置只对某些参数取值成立 |
| **真危险·软失败** | 前置是真的，但代码**不硬拒**：只把 `preconditions_held: False` 写进返回值后**仍然调** |
| **无关** | 不读选区（自建 / 按名选 / 清选区 / 只读遍历 / 纯数据），**或**官方明示可降级、或有回退路径 |

★ **三路口径原本打架的地方（已统一）**：
① A 路把 `solidworks_current_selection` 判「无关（回读方向）」，C 路把同族的
`solidworks_selection_count` / `resolve_selection` / `selection_point` / `resolve_entity` 判「真危险」。
★ 本轮按**同一条判据**统一为「真危险·诊断型」（5 条），并把 `current_selection` 计入（见 §三-改正 1）。
② A 路把 `solidworks_entities_on_body` 判「无关」——★ **这一条是对的**：复核确认它走
`GetBodies2` ＋ `IBody2.GetEdges/GetFaces/GetVertices` 按序号枚举，**完全不碰当前选区**（见总表依据列）。

### ★ 待补依据的判法

★ 凡**给不出可搜索原文片段**的，一律标 **待补依据**，★ 不替它编。
本轮标 **5 条**（见总表 `依据` 列末的「★ 官方依据缺失」/「依据链弱一档」）：
★ 拓扑三条（`CreateSymmetryControl` / `CreateDemoldControl` / `CreatePreservedRegionControl`）
在 `C:\\swapi` 下检索**全部 0 命中**（本轮已重跑该检索）；
★ 钣金斜接法兰 / 钣金闭合角两条的官方页**无 `## Remarks` 段**（本轮已逐页核过），
能力层自己就把 `preconditions_held` 如实报成 `None`；
★ 基准点那一条的官方 `## Remarks` **只有 `NumberOfRefPoints` 那句、没有选区句**。
另：`IProfileCenterMateData` 在 `C:\\swapi` 下亦**无命中** ⇒ 焊件型材中心配合的**官方 mark 无法引用**。

---

## 一、总表（277 条，按工具名排序；★ 三路并集，一条不丢）

★ 「依据」列给的是**文件 + 可直接 grep 的原文片段**（不含行号）。
★ 「路」列 = 该条出自哪一路候选（A/B/C）；`—` = 本轮补录（三路都没写）。

| # | 工具名 | batch | module.function | 读选区 | pre_call | 档位 | 路 | 依据（可 grep 原文片段） |
|---|---|---|---|---|---|---|---|---|
"""

FOOTER = """
---

## 二、统计

| 档位 | 条数 |
|---|---|
| **真危险**（合计） | **36** |
| ├ 真危险·官方前置 | 20 |
| ├ 真危险·显式拒 | 5 |
| ├ 真危险·诊断型 | 5 |
| ├ 真危险·条件 | 2 |
| └ 真危险·软失败 | 4 |
| 安全 | 23 |
| 无关 | 218 |
| **合计** | **277** |

★ **36 + 23 + 218 = 277** ✓（batch1–25 **81** + batch26–50 **108** + batch51–76 **88** = **277** ✓）
★ 其中 **★ 待补依据 5 条**（见 §〇 末段）。

---

## 三、★ 复核结论

### 3.1 复核了几条

★ **逐条独立复核 41 条**（三路标为「真危险」的全部条目）。
★ **两侧都自己打开看过**，不是转述：
- **spec 侧**：AST 解析每个 `ToolSpec`/`_spec` 调用（含跨文件工厂）⇒ **41 条全部确认 `pre_call` 与 `derived_args` 都为 `None`**；
- **函数侧**：41 条目标函数的源码全文逐条读过（24 条函数体**零选区 token**——靠官方 API 隐式吃选区，故逐条读 docstring + spec doc + 官方页）；
- **官方侧**：对能定位的成员**逐页打开 `C:\\swapi\\types\\<接口>\\<成员>.md`** 取 `## Remarks` / 描述行原文。

### 3.2 改正了几条

★ **改正 5 条**（4 条降级 + 1 条升级）：

| # | 工具 | 原判 | 实为 | 依据 |
|---|---|---|---|---|
| 1 | `solidworks_surface_fill` | B 路：真危险 | **无关（可降级）** | `scripts/sw_surface_features.py::insert_fill_surface_report`：声明式分支回读计数为 0 时 **不失败而是回退** —— `_selected_readback <= 0` ⇒ 设 `_fallback_note`、`_declarative = False` ⇒ 走 `SelectByID2(…, MARK_BOUNDARY, …)` 自动选边路径（**在 inject 之后执行** ⇒ 不受事实 503 影响，真机建成过）⇒ 传 `selection` 也不失败。★ B 路自己在「拿不准 1」里留了这个口子，但**档位仍按保守口径计了真危险** |
| 2 | `solidworks_drawing_create_hole_table` | C 路：真危险 | **无关（告警后仍尝试）** | `scripts/sw_drawing_expose.py::create_hole_table`：`if not pre:` 段源码内注「★★ 2026-10-03（接手轮）**从\"硬失败\"改成\"告警后仍然尝试\"**」⇒ 只记 `preconditions_held: False` + `attempted_without_precondition: True` 后**仍然调** `InsertHoleTable3` |
| 3 | `solidworks_helix_insert` | B 路：真危险 | **无关** | ★ 官方示例 `C:\\swapi\\examples\\Create_Spiral_Example_VB.md` 在 `InsertHelix` **之前**执行 `swModel.ClearSelection2 True` 且**并未选中圆**（只 `SelectByID2(\"Front Plane\",\"PLANE\",…)` 选基准面后 `CreateCircle`）⇒ ★ 前置是「**活动草图里有圆**」，不是选区。★ B 路依据的能力层 docstring「官方示例显示要先**选中一个圆**」**与示例不符** |
| 4 | `solidworks_drawing_add_note` | C 路：真危险 | **无关（官方明示降级）** | `C:\\swapi\\types\\IModelDoc2\\InsertNote.md` Remarks 逐字：「…**If there are no selections, the note: Does not have a leader / Is free standing / Is at the origin of the model or drawing**」⇒ 无选区也能建，只是没引线 |
| 5 | `solidworks_current_selection` | A 路：无关 | **真危险·诊断型（升级）** | ★ 与 C 路那 4 条**同一判据**下 A 路口径不自洽。复核：`sw_selection_spec.py::current_selection` 确实 `count = get_selection_count(model)` + `GetSelectedObject6(i, mark)` **读选区**；`tool_specs_batch5.py` 的 spec **无 `pre_call`/`derived_args`** ⇒ 经工具层恒回空列表 |

### 3.3 ★ 另有 1 处**依据链改正**（档位不变，但证据该升级）

★ `solidworks_insert_offset_surface`：能力层 `sw_surface_edit_ops.py::insert_offset_surface` 的 docstring 写
「⚠ ★ **官方没写"要不要先选面"**，而语义上要（参考面）」—— ★ **与官方页不符**。
`C:\\swapi\\types\\IModelDoc2\\InsertOffsetSurface.md` 的 `## Remarks` 首句逐字就是：
「**Make the selections using IModelDocExtension::SelectByID2 before calling this method.**」
⇒ ★ **档位不变（真危险·官方前置），但依据应从「语义推断」升到「官方逐字」** ⇒ ★ 这条比 C 路原本写的**更硬**。

### 3.4 ★ 本轮补录（三路都漏了、但不影响档位）

★ `solidworks_hole_wizard`（batch72）**在三份候选报告里都不出现**。复核结果：**无关（自建选区）** ——
`sw_hole_features.py::create_hole_wizard_at_selection_report` 自己 `ClearSelection2(True)` ＋
`ext.SelectByRay(…, int(SW_SEL_FACES), …)` 建孔位，只 `GetSelectedObjectCount2(-1)` **回读自己那条射线**。
★ 补录以保证「总表覆盖全部 ToolSpec」这一条成立。

### 3.5 ★ 三路原本的覆盖缺口（本轮已补）

★ 三路的 batch 切分是 **1–25 / 26–50 / 51–76**，本轮用 AST 逐文件核过条数：
**81 / 108 / 88**，合计 **277**，与仓库里 AST 抽出的 ToolSpec 总数**完全一致**（无重名、无缺 `module`/`function`）。
★ ⇒ **并集没有丢行**；唯一的缺口是上面 3.4 那条（三路都漏报，但档位正确）。

---

## 四、★ 最该先修的 5 条

★ 排序口径（两条，按题目要求）：
① **「覆盖率关键词命中」** = 官方页里 `SelectByID2` / `selection mark` / `Marks of` / `pre-selected` 这些字样的密度
—— 命中越多 = 官方把前置写得越死 = 越不可能是「猜的」；
② **是否已有其它工具覆盖** = 同一个官方能力，仓里是不是已经有别的工具能做（已有 ⇒ 边际收益低；没有 ⇒ 空白）。

| 排序 | 工具 | ① 关键词命中 | ② 其它工具覆盖 | 为什么排这里 |
|---|---|---|---|---|
| **1** | `solidworks_mold_parting_line` | ★★★ 官方给了**完整 mark 表**：方向 mark 1 / 分型线边 mark 4 | ❌ **无**。全仓只有这一条碰 `InsertMoldPartingLine` | ★ 官方前置写得最死（逐字 + 表格）· mark 现成 · `resolve_selection` 的 `EDGE`/`FACE` **两种 kind 现成** · 照 `batch23::_select_edge` 抄一个 `_pre_parting_line` 连做两次（第二次 `append`）即可 ⇒ **改动量最小、收益最直接** |
| **2** | `solidworks_mold_parting_surface` | ★★★ 与第 1 条**完全同形**（同一段官方表述：方向 mark 1 + 边 mark 4） | ❌ 无 | ★ **与第 1 条可共用同一个 `pre_call`** ⇒ 修第 1 条时顺手一起改，**边际成本≈0**；只是触发条件窄（模型里还没有分型线时），故排第 2 |
| **3** | `solidworks_part_wrap` | ★★★ 官方 `InsertWrapFeature2.md` Remarks 给了一张**完整 mark 表**（面=1 / 拔模方向实体 / 线性边…） | ⚠ 部分：`solidworks_sketch_offset`/`fillet`/`linear_pattern` 走 `_select_spec`，但**没有**「草图 mark=4 + 面 mark=1 同时」的双 mark 工具 | ★ 现成解法**已经在仓里**：`tool_specs_batch74.py::_select_faces_for(mark, count)`（按对象遍历体→面、按 mark 选、回读计数、不够就抛）—— ★ 直接复用两个 `pre_call` 即可（`(4,1)` + `(1,1)`）⇒ **改造成本最低、官方 mark 最全** |
| **4** | `solidworks_part_sweep` / `solidworks_part_loft` / `solidworks_part_axis` / `solidworks_part_wrap`（四件套的**共同底座**） | ★★☆ 三条都有官方 mark（sweep: 轮廓 1 / 路径 4 / 引导线 2；loft: 轮廓 1；axis: 未定） | ⚠ 四条**各自只有自己**，但**四条同型** ⇒ 一起修 | ★ ★ **这四条是「显式拒」里最硬的**（计数为 0 就 `return {"ok": False, "stage": "selection"}` ⇒ 经工具层**必然失败、且失败原因明确**）· ★ 四条共用同一个 `_select_faces_for` 形状 ⇒ **一次改动修四条**。⚠ `axis` 的 mark 官方**没给**（圆柱面/圆锥面/两点）⇒ 先做前三条 |
| **5** | `solidworks_add_sketch_relation` | ★☆ 官方**只有描述行**一句（`Adds the specified constraint to the selected entities.`），**没有 mark** | ❌ 无 | ★ **隐蔽度最高**（Python 体一行、零报错线索，失败时只回一个 bool）⇒ 「用户投诉找不到原因」的头号候选。⚠ 但**修起来比前四条难**：需要的实体是**草图图元**（线/圆/点），而 `resolve_selection` 的 `ENTITY_KINDS` 只有 `EDGE`/`FACE`/`VERTEX`，**三种都不覆盖草图段** ⇒ 要么给底座加第四种 kind（动公共底座），要么复用 `sw_sketch_edit_ops._select_spec`（它已能做「草图段按 index」）—— ★ **排在第 5 正是因为它要动公共底座，不是抄一个 `pre_call` 就完** |

★ **通用建议（三条，按性价比）**：

1. **★ 先做 1 + 2**：两条共用一个 `pre_call`，`kind` 现成、官方 mark 现成 ⇒ 一次改动修两条。
2. **★ 再做第 4 组的四条**：复用 `tool_specs_batch74.py::_select_faces_for(mark, count)` 这个仓内**现成、已被 fact 503 检验过的形状**。
3. **★ 补一条静态门禁**：现状是「只有 `batch4`/`batch23`/`batch26`/`batch29`/`batch58`/`batch60`/`batch74` 记得写 `pre_call`」。
   判据可以照 `mcp-server/tool_registry.py::check_spec` 的形态写：**当 spec 的 `doc`（或目标函数 docstring）含
   「调用前 / 先选 / caller must first select / the selected entities / selected profiles / last selection」
   且 `pre_call is None and derived_args is None` ⇒ 报。**
   ★ 这条门禁一次就会抓住本表 **30 条**（36 条里减掉 5 条诊断型 + 1 条条件——那 6 条的 doc 里没有「先选」字样，
   得靠另一条判据「doc 里没有 `selection` 参数却引用 SelectionManager」）。

★ **诊断型那 5 条**（`selection_count` / `resolve_selection` / `selection_point` / `resolve_entity` / `current_selection`）
**单独处置、不要混进上面那批**：它们不是「缺 `pre_call`」，而是 **`inject="model"` 本身会清空它们要读的东西**
⇒ ★ 修法是**让它们绕开 `RESOLVERS["model"]`**（它们并不需要解析器去连文档），
★ ★ **而这一条改完，上面几档里凡以 `__current_selection__` 为入口的也一起活了** ⇒ 投入产出比最高，但**机制不同**，别当同一件事做。
"""


def main():
    data = json.loads((RECON / "_merged_rows.json").read_text(encoding="utf-8"))
    rows = sorted(data["rows"], key=lambda r: r["n"])
    assert len(rows) == 277, len(rows)
    lines = [HEADER]
    for i, r in enumerate(rows, 1):
        ev = r["ev"].replace("|", "\\|")
        lines.append(f"| {i} | `{r['n']}` | {r['file'].replace('tool_specs_batch','b').replace('.py','')} "
                     f"| `{r['mod']}.{r['fn']}` | {r['reads']} | {r['pre']} | {r['grade']} | {r['fam']} "
                     f"| {ev} |\n")
    lines.append(FOOTER)
    out = RECON / "preselect-family-merged.md"
    out.write_text("".join(lines), encoding="utf-8")
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()