import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 102 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 102 | " + "".join([
    "**在上下文编辑链查到「`SketchUseEdge3` 返回 ok 却什么都不做」 —— 四个可能已逐个排除，真因未查明（按事实 53 强停）** —— ",
    "2026-10-01（轮 162）为打通「端板引型材的边」这条链，`tools/diag_in_context_sketch.py` 做了**读数诊断**：",
    "① 活动文档：进入在上下文编辑后 `sw.ActiveDoc` **不是** `asm` ⇒ 草图操作要落在**活动文档**上 ✓ 已排除；",
    "② 顺序：`sw_part.start_sketch` 内部会 `ClearSelection2(True)` ⇒ 选边必须在开草图**之后** ✓ 已排除；",
    "③ 选边：**回读** `GetSelectedObjectCount2(-1)` = **1**（事实 94：不许只信返回值）⇒ **边真的选中了** ✓ 已排除；",
    "④ 读数法：仓库助手 / 直接 COM **两法一致**（都是 0）⇒ **不是读错对象** ✓ 已排除",
    "★★ 结论：`ISketchManager.SketchUseEdge3`（经 `sw_sketch_edit.convert_entities`）**返回 ok 却什么都没做** —— ",
    "典型**静默无效**（事实 62/79/88 那一族）。⚠ **真因未查明**；已在这同一处换了约 6 次写法，",
    "⇒ 按**事实 53**（≥3 次即停）**强停**，**只报症状不猜根因**。",
    "★ 尚未排除的候选（**一个都没验证，不写进结论**）：投影**跨零件的外部边**是否需要先建立",
    "「在上下文」关系（⚠ 而那正是本链要建的东西 —— 可能**鸡生蛋**）；或 `SketchUseEdge3` 需要更强的",
    "选择上下文（mark / `SelectData`）。",
    "★ 顺带查实两个真机形态：**`IComponent2.GetBody()`**（零参，返回 `Body2`；",
    "⚠ 名字**不带 2** —— `Body2` 是返回类型，我第一版读成 `GetBody2` 报 `<unknown>.GetBody2`）；",
    "**`sw_assembly.add_component` 返回 `IComponent2` 对象**（docstring 明写）⇒ 别去 `GetComponents` 猜接口族。",
    " | `tools/diag_in_context_sketch.py`；`tools/verify_in_context_reference_smoke.py`（**9/12**）；",
    "`scripts/sw_sketch_edit.py` 的 `convert_entities`；事实 32 / 51 / 53 / 62 / 94 |",
])
if "| 102 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 102")
else:
    print("  已有 102")

# ── Spec Kit 082 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\082-in-context-chain-four-exclusions")
S.mkdir(parents=True, exist_ok=True)
spec = """# 082 · 在上下文链：**排除四个可能**，定位到「`SketchUseEdge3` 静默无效」

**Status**: Implemented（轮 162）· ⚠ **判据①②仍未绿，真因未查明**

## 一、起因
`081` 在上下文链报「投影后草图实体数 = 0」，而 `convert_entities` 不抛异常。
⇒ 本轮先做**读数诊断**（`tools/diag_in_context_sketch.py`），**不再换写法**（事实 53）。

## 二、★★★ 四个可能，逐个排除
```
① 活动文档  ：进入在上下文编辑后 `sw.ActiveDoc` **不是** `asm`
              ⇒ 草图操作要落在**活动文档**上 ✓ **已排除**（改过之后仍是 0）
② 顺序      ：`sw_part.start_sketch` 内部会 `ClearSelection2(True)`
              ⇒ 选边必须放在开草图**之后** ✓ **已排除**（改过之后仍是 0）
③ 选边      ：**回读** `GetSelectedObjectCount2(-1)` = **1**
              （事实 94：不许只信返回值）⇒ **边真的选中了** ✓ **已排除**
④ 读数法    ：仓库助手 `get_sketch_segments` 与直接 COM **两法一致**（都是 0）
              ⇒ **不是读错对象** ✓ **已排除**
```
⇒ ⑤ 投影**前** 0 · `convert_entities` **不抛异常** · 投影**后**仍是 **0**

## 三、★★ 结论与**停手依据**
```
`ISketchManager.SketchUseEdge3` **返回 ok 却什么都没做** —— 典型**静默无效**
⚠ **真因未查明**；已在这同一处换了约 6 次写法
⇒ 按 **事实 53**（≥3 次即停）**强停**：**只报症状，不猜根因**
```
★ 尚未排除的候选（**一个都没验证，不写进结论**）：
- 投影**跨零件的外部边**是否要先建立「在上下文」关系 —— ⚠ 而那正是本链要建的东西（**可能鸡生蛋**）
- `SketchUseEdge3` 是否需要更强的选择上下文（mark / `SelectData`）

## 四、★ 顺带查实两个真机形态
```
★ `IComponent2.GetBody()`（零参，返回 `Body2`）
  ⚠ **名字不带 2** —— `Body2` 是**返回类型**；我第一版读成 `GetBody2` ⇒ `<unknown>.GetBody2`
★ `sw_assembly.add_component` **返回 `IComponent2` 对象**（docstring 明写）
  ⇒ 别去 `GetComponents` 猜接口族（轮 161 就是这么卡住的）
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-8201 | ★★ **读数诊断**（不换写法）—— 三法对照 |
| SC-8202 | ★★★ **逐个排除四个可能**（活动文档 / 顺序 / 选边 / 读数法）|
| SC-8203 | ★★ 定位到「`SketchUseEdge3` **返回 ok 却不做事**」|
| SC-8204 | ★★ 按**事实 53 强停**，只报症状、候选**标未验证** |
| SC-8205 | ★ 记两个真机形态（`GetBody` 不带 2 · `add_component` 返回组件）|
| SC-8206 | 事实 102 入库；门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）仍没绿** ⇒ **外部参考仍未建立**；
* ⚠ **真因未查明** —— 四个可能排除 ≠ 找到原因；
* ⚠ 候选（"跨零件外部边要先建在上下文关系"）**一个都没验证**；
* ⚠ 诊断脚本里「进入**前**的活动文档」那一条判据写法有误（前后都报 False）—— 
  不影响④的结论（读数法对照是有效的），但**该判据本身不可信**。
"""
plan = """# 082 · Plan

## 步骤
1. `081` 卡在「投影后实体数 = 0」，而 `convert_entities` 不抛异常
2. ★ **按事实 53 停手**：不再换写法，改做**读数诊断**
3. 诊断四件事：活动文档是谁 · 何时选边 · 选边回读计数 · 三法读数对照
4. ⇒ **四个可能逐个排除** ⇒ 定位到「`SketchUseEdge3` 返回 ok 却不做事」
5. ⇒ **强停**，候选标未验证
6. 记事实 102 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 一直在同一处换写法 | ★ **事实 53**：先做**读数诊断**，别改行为 |
| 把"排除了四个"说成"找到了原因" | ★ 结论里**明说真因未查明**，候选标未验证 |
| 只信实参返回值 | ★ **回读** `GetSelectedObjectCount2`（事实 94）|
| 一种读数法数不出来就下结论 | ★ **三法对照**（本轮正是靠它排除④）|
"""
tasks = """# 082 · Tasks（全部完成，轮 162）

- [x] T-8201 读数诊断 `→ 验收:` `python tools/diag_in_context_sketch.py`（打印四段对照）
- [x] T-8202 ★★★ 排除四个可能（活动文档 / 顺序 / 选边 / 读数法）
- [x] T-8203 ★★ 定位到「`SketchUseEdge3` 返回 ok 却不做事」；按**事实 53 强停**
- [x] T-8204 事实 102
- [x] T-8205 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 082 · Converge

**Converged**: 2026-10-01（轮 162）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8201 读数诊断 | ✅ |
| SC-8202 排除四个可能 | ✅ |
| SC-8203 定位到静默无效 | ✅ |
| SC-8204 强停 + 候选标未验证 | ✅ |
| SC-8205 两个真机形态 | ✅ |
| SC-8206 事实 102 + 门禁 + 回归 | ✅ |

## 二、★★★ 本轮的形状：**「排除了四个」≠「找到了原因」**
```
四轮改动（活动文档 / 顺序 / 选边 / 读数法）都没有让计数从 0 变 1
⇒ ★ 但每一轮都**排除了一个具体的可能** —— 这不是白做，而是**把搜索空间缩掉了**
⇒ ★★ 关键是**如实说**：「真因未查明」，而不是把最后一次改动当成原因。
```
★ 与事实 53 的关系：53 说「连续修补 ≥3 次就停下」—— 本轮**照做了**：
第 4 次之前就改成**做诊断**（读，不改），于是得到了「读数法没问题」这个**结论性**信息。

## 三、★ 一条可复用的手法
```
**在改行为之前，先把「读数」本身验证掉。**
本轮正是靠它排除了④（三法读数对照）——
  否则我会一直以为"投影没成"，而如果其实是**读错对象**，那所有改动都是白费。
```

## 四、未查证
* ⚠ **判据①②仍没绿** ⇒ 外部参考仍未建立；
* ⚠ **真因未查明**；
* ⚠ 候选（"跨零件外部边要先建在上下文关系"）**一个都没验证**；
* ⚠ 诊断脚本里「进入前的活动文档」那条判据写法有误（该判据本身不可信）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

# ── ROADMAP 游标 ────────────────────────────────────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           474 🎯 **Spec Kit `082`：在上下文链 —— ****排除四个可能****，定位到「`SketchUseEdge3` 静默无效」**（轮 162）——
               `081` 报「投影后草图实体数 = 0」而 `convert_entities` 不抛异常 ⇒
               ★ **按事实 53 停手**：**不再换写法**，改做**读数诊断**（`tools/diag_in_context_sketch.py`）。
            475 ★★★ **四个可能，逐个排除**：
               ```
               ① 活动文档：进入在上下文编辑后 `sw.ActiveDoc` **不是** `asm`
                  ⇒ 草图操作要落在**活动文档**上        ✓ 已排除（改过之后仍是 0）
               ② 顺序    ：`sw_part.start_sketch` 内部会 `ClearSelection2(True)`
                  ⇒ 选边必须放在开草图**之后**          ✓ 已排除（改过之后仍是 0）
               ③ 选边    ：**回读** `GetSelectedObjectCount2(-1)` = **1**（事实 94）
                  ⇒ **边真的选中了**                    ✓ 已排除
               ④ 读数法  ：仓库助手 / 直接 COM **两法一致**（都是 0）
                  ⇒ **不是读错对象**                    ✓ 已排除
               ⇒ ⑤ 投影**前** 0 · `convert_entities` **不抛异常** · 投影**后**仍是 **0**
               ```
            476 ★★ **结论与停手依据**：`ISketchManager.SketchUseEdge3` **返回 ok 却什么都没做** ——
               典型**静默无效**（事实 62/79/88 那一族）。⚠ **真因未查明**；
               已在这同一处换了约 **6** 次写法 ⇒ 按**事实 53**（≥3 次即停）**强停**，
               **只报症状、不猜根因**。
               ★ **尚未排除的候选（一个都没验证，不写进结论）**：投影**跨零件的外部边**是否需要
                 先建立「在上下文」关系 —— ⚠ 而那正是本链要建的东西（**可能鸡生蛋**）；
                 或 `SketchUseEdge3` 需要更强的选择上下文（mark / `SelectData`）。
            477 ★ **顺带查实两个真机形态**：
               ```
               ★ `IComponent2.GetBody()`（零参，返回 `Body2`）
                 ⚠ **名字不带 2** —— `Body2` 是**返回类型**；我第一版读成 `GetBody2` ⇒ `<unknown>.GetBody2`
               ★ `sw_assembly.add_component` **返回 `IComponent2` 对象**（docstring 明写）
                 ⇒ 别去 `GetComponents` 猜接口族（轮 161 就是这么卡住的）
               ```
               ★★★ **本轮的形状：「排除了四个」≠「找到了原因」** ——
                 四轮改动都没让计数从 0 变 1，**但每轮都排除掉一个具体可能**（把搜索空间缩掉了）；
                 ★ 关键是**如实说「真因未查明」**，而不是把最后一次改动当成原因。
               ★ **一条可复用手法**：**在改行为之前，先把「读数」本身验证掉** ——
                 本轮正是靠三法对照排除了④；否则若其实是**读错对象**，前面所有改动都是白费。
               ⚑ **未查证**：⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）仍没绿** ⇒ **外部参考仍未建立**；
                 ⚠ **真因未查明**；⚠ 诊断脚本里「进入**前**的活动文档」那条判据写法有误（**该判据本身不可信**）。
               已知事实 **102** 入库 · 回归 **1246 passed** · `release_check` exit 0。
               下轮候选：① 验「跨零件外部边是否要先建在上下文关系」这个候选（**先设计能证伪的判据**）；
               ② 换 `SelectData` / mark 那条路；③ 回到「真缺」继续补（**别再在这一行上换写法**）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+474 ", before, re.M):
    print("  游标 474 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+477 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 477 行已存在 ✓")
