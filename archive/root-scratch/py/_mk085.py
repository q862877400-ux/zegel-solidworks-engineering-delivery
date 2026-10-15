import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\085-gtol-frame-order")
S.mkdir(parents=True, exist_ok=True)

spec = """# 085 · 「帧取不到」是**顺序问题** —— `ConvertFormat()` 必须先于 `AddFrame()`

**Status**: Implemented（轮 165）· ⚠ `geometric_tolerance` 仍为 `stitched`（3/5）

## 一、线索来源（顺 `0x80010105` 回查）
轮 164 更正了 `CreateChamfer` 的误判后，我顺那条线索回查「**还有哪些能力是被『只看异常』误判的**」。
★ 我写了一个扫描（按「附近有没有回读字样」判）⇒ **73 处命中，大多假阳性**
（门禁自己的措辞 / 参数校验 / 官方 Remarks 引文）⇒ ★ **判据又是"邻近文本"式，弃用**。

⇒ 但里面有一条值得动手：`sw_gtol.py` 的「**我们在 SW 2026，那条路不可用**」——
★ 而 `geometric_tolerance` 正是 5 条 `stitched` 之一（3/5）。

## 二、★ 先核实：那条断言**不是**「只看异常」
```
它的依据是**官方 Remarks 原文**：
  IGtol.SetFrameSymbols2 > "valid only if this Gtol was created in a version of
                            SOLIDWORKS earlier than 2022."
⇒ 这是**读文档**读出来的 ✓；而「到不了」那半也**回读了状态**：
  GetFrameCount 1 →（ConvertFormat 成功后）0 · GetFrame(0/1/2) 全 None
⇒ ★ **所以这条本来就不是误判** —— 我的扫描判据误报了它（已如实记）。
```

## 三、★★★ 但**它自己列的「未查证」里藏着真因**
```
轮 120 写的顺序是：AddFrame()（False）→ ConvertFormat()（成功）→ GetFrame(1)/(2)（None）
★ 读官方 `IGtol.AddFrame` 的 Remarks（`C:/swapi/types/IGtol/AddFrame.md`）**原文**：
  > This method is valid only if this Gtol was created in SOLIDWORKS **2022 or later**.
⇒ 新建的 Gtol **默认是旧格式** ⇒ `AddFrame()` 在**转换前**调用**必然 False**
⇒ ★★★ **正确顺序**：**先 `ConvertFormat()` → 再 `AddFrame()` → 再 `GetFrame(n)`**
```

## 四、★★ 实测（`tools/probe_gtol_frame_order.py`）
```
新建后 AddFrame()【旧顺序】   ⇒ **False**
ConvertFormat()              ⇒ 0（成功）
★★ AddFrame()【转换之后】     ⇒ **True**        ← ★★★ 旧顺序下是 False
   加帧后 GetFrameCount      ⇒ **2**
★★ GetFrame(0..3)            ⇒ ['None', '有', '有', 'None']  ← ★★ **拿到对象了**
★★★ AddIndicator(0,0,'A')    ⇒ **False**        ← ⚠ 这一层仍未通
```

## 五、★ 修法与更正
```
修：`ensure_gtol_frame` 改为**先 ConvertFormat() 再 AddFrame()**
正：改掉两句**已过时**的报错
    · `GetFrame` 那句不再说「该 Gtol 可能不是 2022 格式」（⚠ 走了那个分支就已转换过）
    · `AddIndicator` 那句不再说「不是 2022 格式」⇒ 改成「**帧已拿到 ⇒ 参数/前置未查明**」
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-8501 | ★ 核实原断言**不是**「只看异常」（有官方 Remarks + 回读状态）⇒ 我的扫描**误报**了它 |
| SC-8502 | ★★★ **从它自己写的「未查证」里读出真因**（`AddFrame` 的 Remarks）|
| SC-8503 | ★★★ **顺序更正**：`ConvertFormat()` → `AddFrame()` ⇒ **`AddFrame()` True**、`GetFrame` **拿到对象** |
| SC-8504 | ★ 修 `ensure_gtol_frame` + 改两句已过时的报错 |
| SC-8505 | ★ 事实 105；条目更正（「帧取不到」→「**帧路径已通**，指示符未查明」）|
| SC-8506 | 门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ **`IGtolFrame.AddIndicator(Int32, Int32, String)` 仍返回 `False`** ⇒ **参数/前置未查明**
  （★ 但**不再**是「帧取不到」）；
* ⚠ `geometric_tolerance` **仍为 `stitched`**（3/5）—— **没有**升 `verified`；
* ⚠ 本轮**没有**试 `SetSymbolXml`（XML 路径）；
* ⚠ 我那个「按邻近文本扫误判」的判据**已弃用**，**没有**接进任何门禁。
"""
plan = """# 085 · Plan

## 步骤
1. 顺 `0x80010105` 回查「还有哪些能力是被『只看异常』误判的」
2. ⚠ 第一版扫描判据（邻近文本）**73 处、大多假阳性** ⇒ **弃用**
3. ★ 挑里面一条值得动手的：`geometric_tolerance`（`stitched` 之一）
4. ★ 先核实原断言 ⇒ **它不是误判**（有官方 Remarks + 回读状态）⇒ **我的扫描误报了**
5. ★★★ 但**它自己写的「未查证」里藏着真因**：读 `AddFrame` 的 Remarks ⇒ **2022 or later**
6. ⇒ **顺序**：`ConvertFormat()` 必须**先于** `AddFrame()`
7. 实测 ⇒ `AddFrame()` **True** · `GetFrameCount` **2** · `GetFrame(1)/(2)` **拿到对象** ✓
8. ⚠ `AddIndicator` 仍 False ⇒ **未查明**（如实记）· 修模块 + 改过时报错
9. 事实 105 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 拿一个假阳性高的扫描当结论 | ★ **一眼假就弃用**（本轮 73 处大多不相关）|
| 把「我没试对」当成「它做不到」 | ★ **读官方 Remarks** 找 API 的**用法前提**（本轮的核心）|
| 报错信息过时却留着 | ★ **改掉**（否则下一个人会顺着错话走）|
| 顺手把条目升 verified | ★ **不升** —— `AddIndicator` 那半还没通 |
"""
tasks = """# 085 · Tasks（全部完成，轮 165）

- [x] T-8501 顺线索回查 ⇒ 第一版扫描判据**弃用**（73 处大多假阳性）
- [x] T-8502 ★ 核实 `geometric_tolerance` 的原断言 ⇒ **不是**误判（我的扫描误报）
- [x] T-8503 ★★★ 读 `AddFrame` 的 Remarks 找出**顺序**这个真因
- [x] T-8504 ★★ 实测 `→ 验收:` `python tools/probe_gtol_frame_order.py`
  （`ConvertFormat` → `AddFrame()` **True** → `GetFrameCount` **2** → `GetFrame` **有对象**）
- [x] T-8505 修 `ensure_gtol_frame` + 改两句过时报错
- [x] T-8506 事实 105 + 条目更正
- [x] T-8507 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 085 · Converge

**Converged**: 2026-10-01（轮 165）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8501 核实原断言 | ✅ 不是误判；我的扫描误报 |
| SC-8502 从其「未查证」里读出真因 | ✅ `AddFrame` 的 Remarks |
| SC-8503 顺序更正 + 实测 | ✅ `AddFrame()` True · `GetFrame` 有对象 |
| SC-8504 修模块 + 改报错 | ✅ |
| SC-8505 事实 105 + 条目更正 | ✅ |
| SC-8506 门禁 + 回归 | ✅ `release_check` exit 0 · **1246 passed** |

## 二、★★★ 「顺序问题」第二次被误判成「做不到」
```
事实 104（轮 164）：CreateChamfer —— 把「**返回值拿不到**」读成「**接口到不了**」
事实 105（轮 165）：AddFrame      —— 把「**顺序不对**」读成「**帧取不到**」
⇒ ★★ 两次的共同点：**我试的是这个 API 的一种用法，却把结论写成了这个 API 的性质。**
⇒ ★ 可复用的问句（本轮加进事实表）：
   **「我试的是这个 API 的哪一种用法？」** —— 问完再决定要不要写"做不到"。
```

## 三、★ 本轮第一次尝试是**失败判据**（如实记）
```
我按「附近有没有回读字样」扫「只看异常就定性」⇒ **73 处命中，大多假阳性**
（门禁自己的措辞 / 参数校验 / 官方 Remarks 引文）
⇒ ★ 判据又是"邻近文本"式（事实 74 那一族）⇒ **弃用，未接进任何门禁**
★ 而且它对**唯一那条真正相关的**（`sw_gtol`）也是**误报** —— 那条本来就有依据。
```

## 四、未查证
* ⚠ `IGtolFrame.AddIndicator` **仍返回 False** ⇒ 参数/前置未查明；
* ⚠ `geometric_tolerance` **仍 `stitched`**（未升）；
* ⚠ 未试 `SetSymbolXml`（XML 路径）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

# ── ROADMAP 游标 ────────────────────────────────────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           489 🎯 **Spec Kit `085`：★ 「帧取不到」是****顺序问题**** —— `ConvertFormat()` 必须先于 `AddFrame()`**（轮 165）——
               线索：轮 164 更正 `CreateChamfer` 的误判后，顺 `0x80010105` 回查
               「**还有哪些能力是被『只看异常』误判的**」。
               ⚠ 我第一版扫描判据（按「附近有没有回读字样」）⇒ **73 处命中、大多假阳性**
               （门禁自己的措辞 / 参数校验 / 官方 Remarks 引文）⇒ ★ **又是"邻近文本"式，弃用**。
            490 ★ **先核实那条值得动手的**（`geometric_tolerance`，`stitched` 之一）：
               它说「我们在 SW 2026，那条路**不可用**」—— ★ 而它的依据是**官方 Remarks 原文**
               （`SetFrameSymbols2` > "valid only if … earlier than 2022"），
               且「到不了」那半**回读了状态**（`GetFrameCount` 1 → 0 · `GetFrame` 全 None）
               ⇒ ★★ **所以它本来就不是误判 —— 我的扫描误报了它**（已如实记）。
            491 ★★★ **但**它自己写的「未查证」里藏着真因****：轮 120 的顺序是
               `AddFrame()`（False）→ `ConvertFormat()`（成功）→ `GetFrame()`（None）。
               ★ 读官方 `IGtol.AddFrame` 的 Remarks **原文**：
               > This method is valid only if this Gtol was created in SOLIDWORKS **2022 or later**.
               ⇒ 新建的 Gtol **默认是旧格式** ⇒ `AddFrame()` 在**转换前**调用**必然 False**
               ⇒ ★★★ **正确顺序：先 `ConvertFormat()` → 再 `AddFrame()` → 再 `GetFrame(n)`**。
            492 ★★ **实测**（`tools/probe_gtol_frame_order.py`）：
               ```
               新建后 AddFrame()【旧顺序】   ⇒ **False**
               ConvertFormat()              ⇒ 0（成功）
               ★★ AddFrame()【转换之后】     ⇒ **True**     ← ★★★ 旧顺序下是 False
                  加帧后 GetFrameCount      ⇒ **2**
               ★★ GetFrame(0..3)            ⇒ ['None', '有', '有', 'None']  ← **拿到对象了**
               ★★★ AddIndicator(0,0,'A')    ⇒ **False**     ← ⚠ 这一层仍未通
               ```
               ★ 已修 `ensure_gtol_frame`（先转换再加帧）+ 改掉两句**已过时**的报错
                 （`GetFrame` / `AddIndicator` 那两句都不再说「不是 2022 格式」—— **我们确实转换过了**）。
            493 ★★★ **「顺序问题」第二次被误判成「做不到」**：
               ```
               事实 104（轮 164）：CreateChamfer —— 把「**返回值拿不到**」读成「**接口到不了**」
               事实 105（轮 165）：AddFrame      —— 把「**顺序不对**」读成「**帧取不到**」
               ⇒ ★★ 两次的共同点：**我试的是这个 API 的一种用法，
                 却把结论写成了这个 API 的性质。**
               ⇒ ★ 可复用的问句：**「我试的是这个 API 的哪一种用法？」** —— 问完再决定要不要写「做不到」。
               ```
            494 ⚠ `geometric_tolerance` **仍为 `stitched`**（3/5）—— ★ **没有**因为"帧通了"就升它：
               `AddIndicator` 那半仍未通。
               ⚑ **未查证**：⚠ `IGtolFrame.AddIndicator(Int32, Int32, String)` **仍返回 False**
                 ⇒ 参数/前置未查明（★ 但**不再**是「帧取不到」）；⚠ 未试 `SetSymbolXml`（XML 路径）；
                 ⚠ 我那个「按邻近文本扫误判」的判据**已弃用，未接进任何门禁**。
               能力 **38** 条（verified **32**）· 门禁 + `release_check` exit 0 · 回归 **1246 passed**。
               下轮候选：① 查 `AddIndicator` 的参数/前置（**先读官方 Remarks**，别再猜）；
               ② 顺同一线索查 `surface_modeling` / `mold_tools`（那两条 `stitched` **连 evidence 都没有**）；
               ③ 回到「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+489 ", before, re.M):
    print("  游标 489 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+494 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 494 行已存在 ✓")
