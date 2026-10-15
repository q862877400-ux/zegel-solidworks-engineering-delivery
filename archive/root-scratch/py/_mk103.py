import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 123 | " + "".join([
    "**样条**从「建不出来」变成「能建」—— 修的是两处：实参形态 + 成员名（而「建不出来」是**误判**）** —— ",
    "2026-10-01（轮 183）。",
    "★ 背景：轮 141/182 记着「样条建不出来（`CreateSpline2` 返回 None）」⇒ 它**挡住了 `composite_curve`**。",
    "★★★ **读官方 Remarks ⇒ 发现实参形态要求**：",
    "```",
    "`CreateSpline` / `CreateSpline2` 的 Remarks：\"The PointData array is a set of, at least,",
    "**two X, Y, Z values**. X 起点 = PointData[0]，Y = [1]，Z = [2]；下一点 X = [3] …\"",
    "⇒ ★ 即一个**扁平的一维数组** `[x0,y0,z0, x1,y1,z1, …]`，⚠ 而仓库传的是 **list of tuples**。",
    "```",
    "★★★ **真机逐形态判别**（`tools/probe_spline_forms.py`，**每次回读草图段数**）：",
    "```",
    "① 扁平 list                   ⇒ 段数 0 → 0（没变）· 返回 None",
    "② 扁平 tuple                  ⇒ 段数 0 → 0（没变）· 返回 None",
    "③ **VARIANT(VT_ARRAY|VT_R8)** ⇒ 段数 **0 → 1（变了 ✚）**   ★★★ **成了**",
    "④ list of tuples（原写法）     ⇒ 段数 0 → 0（没变）· 返回 None",
    "⇒ ★★ 与**事实 167**（`AddRelation` 必须包 `VARIANT(VT_ARRAY|VT_DISPATCH)`）**完全同一族**：",
    "   **数组实参必须包 VARIANT**，且**官方 Remarks 没说** ⇒ 只能实测出来。",
    "```",
    "⚠⚠ **修的过程中还查出第二处**：`getattr(sketch_manager, \"CreateSpline\")` ⇒ **None** ⇒",
    "在 `get_com_member` 里报 `TypeError: 'NoneType' object is not callable` ——",
    "★ 而**官方 md 明写 `CreateSpline` 是 `Obsolete. Superseded by CreateSpline2`** ⇒",
    "★★ **必须走 `CreateSpline2`**；⚠ 那个 `TypeError` **指不出真因**（又是「报错看不出病因」那一族）。",
    "★ 修后**三种写法全部成功**（点对 / 扁平 / `simulate=True` ⇒ 段数**都 0 → 1**）：",
    "```",
    "create_spline 现在：**自己摊平** + 包 VARIANT(VT_ARRAY|VT_R8) + **走 CreateSpline2**",
    "```",
    "★★★ **意义**：这是一个**「挡着不止一个能力」的上游** —— 它一修，",
    "`composite_curve` 的**前置从「不可达」变成「可达」**（⚠ 本轮**未**重跑它，留给下轮）。",
    " | `tools/probe_spline_forms.py`；`C:/swapi/types/ISketchManager/{CreateSpline,CreateSpline2}.md`；",
    "`scripts/sketch_relations.create_spline`；事实 40 / 122 / 167 |",
])
if "| 123 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 123")
else:
    print("  已有 123")

S = Path(r"D:\AI\SW\specs\103-spline-can-now-be-created")
S.mkdir(parents=True, exist_ok=True)
spec = """# 103 · 样条**从「建不出来」变成「能建」** —— 修实参形态 + 成员名（而「建不出来」是**误判**）

**Status**: Implemented（轮 183）

## 一、起因
轮 141/182 记着「样条建不出来（`CreateSpline2` 返回 None）」⇒ ★ 它**挡住了 `composite_curve`**。

## 二、★★★ 读官方 Remarks ⇒ 发现**实参形态**要求
```
`CreateSpline` / `CreateSpline2` 的 Remarks：
  "The PointData array is a set of, at least, **two X, Y, Z values**.
   X 起点 = PointData[0]，Y = [1]，Z = [2]；下一点 X = [3] …"
⇒ ★ 即一个**扁平的一维数组** `[x0,y0,z0, x1,y1,z1, …]`，⚠ 而仓库传的是 **list of tuples**。
```

## 三、★★★ 真机逐形态判别（`tools/probe_spline_forms.py`，**每次回读草图段数**）
```
① 扁平 list                   ⇒ 段数 0 → 0（没变）· 返回 None
② 扁平 tuple                  ⇒ 段数 0 → 0（没变）· 返回 None
③ **VARIANT(VT_ARRAY|VT_R8)** ⇒ 段数 **0 → 1（变了 ✚）**   ★★★ **成了**
④ list of tuples（原写法）     ⇒ 段数 0 → 0（没变）· 返回 None
⇒ ★★ 与**事实 167**（`AddRelation` 必须包 `VARIANT(VT_ARRAY|VT_DISPATCH)`）**完全同一族**：
  **数组实参必须包 VARIANT**，且**官方 Remarks 没说** ⇒ 只能实测出来。
```

## 四、⚠⚠ 修的过程中查出**第二处**
```
`getattr(sketch_manager, "CreateSpline")` ⇒ **None**
  ⇒ 在 `get_com_member` 里报 `TypeError: 'NoneType' object is not callable`
★ 而**官方 md 明写**：`CreateSpline` 是 "**Obsolete. Superseded by ISketchManager::CreateSpline2**"
⇒ ★★ **必须走 `CreateSpline2`**；
⚠ 那个 `TypeError` **指不出真因**（又是「报错看不出病因」那一族）。
```

## 五、修后
```
create_spline 现在：**自己摊平**（两种写法都收）+ 包 `VARIANT(VT_ARRAY|VT_R8)` + **走 `CreateSpline2`**
★ 真机：点对 / 扁平 / `simulate=True` ⇒ 段数**都 0 → 1** ✓
```

## 六、★★★ 意义
```
这是一个**「挡着不止一个能力」的上游** —— 它一修，
`composite_curve` 的**前置从「不可达」变成「可达」**
（⚠ 本轮**未**重跑它 —— 留给下轮，且要看它现在是否真的能建成）。
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-10301 | ★★★ **读官方 Remarks** 得到实参形态（扁平 X,Y,Z 序列）|
| SC-10302 | ★★★ **逐形态真机判别**（每次回读段数）⇒ `VARIANT(VT_ARRAY\\|VT_R8)` 唯一可行 |
| SC-10303 | ★★ **与事实 167 同族**（数组实参必须包 VARIANT）|
| SC-10304 | ★★ 查出第二处：`CreateSpline` 已 Obsolete ⇒ 走 `CreateSpline2` |
| SC-10305 | ★ 修后**三种写法全部成功**（段数 0 → 1）|
| SC-10306 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **`composite_curve` 本轮未重跑** —— 它的前置现在**可达**，但它**是否真能建成** **未验**；
* ⚠ 官方 Remarks **没说「要包 VARIANT」** ⇒ 这条知识**只能来自实测**（不可从文档推出）；
* ⚠ 只验了「段数变了」⇒ **不证样条的几何形状**；
* ⚠ `CreateSplineByEqnParams` 族（B 曲线：控制点 + 节点向量）**未试**。
"""
plan = """# 103 · Plan

## 步骤
1. 轮 182 查明「样条建不出」挡着 `composite_curve` ⇒ 本轮攻它
2. ★ 读官方 md ⇒ **CreateSpline 的 Remarks 写明 PointData 是**扁平的 X,Y,Z 序列****
3. ★★ 真机逐形态判别（扁平 list / tuple / VARIANT / list of tuples）
4. ★★★ ⇒ **只有 `VARIANT(VT_ARRAY|VT_R8)` 成**（段数 0 → 1）
5. ⚠ 修的时候踩到第二处：`CreateSpline` 取不到（Obsolete）⇒ `TypeError`（**指不出真因**）
6. ★ 修 `create_spline`（摊平 + VARIANT + 走 `CreateSpline2`）⇒ **三种写法全成**
7. 事实 123 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把"形态不对"读成"接口到不了" | ★ **读官方 Remarks + 逐形态实测** |
| 只试一种形态就下结论 | ★ **四种形态都试**（含现状做对照）|
| 报错看不出真因 | ★ 打 **traceback** 定位到 `member(*args)` |
| 顺手去修 `composite_curve` | ★ **不顺手**（本轮只修上游，它的复验留给下轮）|
"""
tasks = """# 103 · Tasks（全部完成，轮 183）

- [x] T-10301 读官方 Remarks 得实参形态
- [x] T-10302 ★★★ 逐形态真机判别 `→ 验收:` `python tools/probe_spline_forms.py`（**只有 VARIANT 成**）
- [x] T-10303 修 `create_spline`（摊平 + VARIANT + CreateSpline2）
- [x] T-10304 ★★ 真机复验三种写法 `→ 验收:` 段数**都 0 → 1**
- [x] T-10305 契约测试 `→ 验收:` `python -m pytest tests -q -k "spline or relation"`（**5 passed / 1 skipped**）
- [x] T-10306 事实 123 · 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 103 · Converge

**Converged**: 2026-10-01（轮 183）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-10301 官方 Remarks 定形态 | ✅ 扁平 X,Y,Z |
| SC-10302 逐形态判别 | ✅ **只有 VARIANT 成** |
| SC-10303 与事实 167 同族 | ✅ |
| SC-10304 查出 Obsolete 那一处 | ✅ |
| SC-10305 三种写法全成 | ✅ 0 → 1 |
| SC-10306 门禁 + 回归 | ✅ |

## 二、★★★ 「样条建不出来」是**误判** —— 而它**已经写进事实表**（轮 141/182）
```
轮 141 的结论是「样条建不出来（CreateSpline2 返回 None）」，我今天还据此把 `composite_curve`
定性成「前置不可达」。⇒ ★ 而真相是：**实参形态不对**（裸 list/tuple 静默返回 None）。
⇒ ★★ 教训：**"返回 None" 既可能是「做不到」，也可能是「喂的东西不对」** ——
   而**官方 Remarks 里的形态要求**是区分它们的第一步（★ 本轮就是这么分出来的）。
```

## 三、★ 这是本会话第 4 次「数组实参必须包 VARIANT」
```
`AddRelation`（轮 167）· `Select4` 的 Callout（事实 33）· `CreateSpline`（本轮）…
⇒ ★ 定则（可复用）：**官方签名里是 `Object` 的数组实参，先按「要包 VARIANT」准备** ——
   裸 list/tuple 多半**静默失败**，而**报错看不出病因**。
```

## 四、未查证
* ⚠ **`composite_curve` 未重跑**（前置现在可达 ⇒ 下轮验）；
* ⚠ Remarks **没说「要包 VARIANT」** ⇒ 该知识只能来自实测；
* ⚠ 只证「段数变了」，**不证几何形状**；
* ⚠ `CreateSplineByEqnParams` 族未试。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
